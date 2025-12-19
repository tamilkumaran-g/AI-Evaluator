# app.py
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore

# Local project modules (must exist in your project)
# comment_combine, config, firebase_db, models, services.validator (from your project)
from comment_combine import analyze_url, analyze_comments_with_gemini
from config import get_settings
from firebase_db import FirebaseDB, VALIDATIONS_COLLECTION
from models import IdeaInput, ValidationReport
from services.validator import ValidationService
from idea_analyzer import run_idea_analyzer

# include router from final_report (ensure final_report.py exists and defines `router`)
from final_report import router as final_router

# ========= SETTINGS & APP =========
settings = get_settings()
app = FastAPI(title="Startup Toolkit API", version="2.0.0")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ========= MIDDLEWARE =========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Development-friendly session middleware:
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "SUPER_SECRET_CHANGE_ME_123456789"),
    https_only=False,   # in dev allow http; set True in prod
    same_site="lax",    # adjust to "none" + https_only=True if cross-site iframe in prod
    max_age=60 * 60 * 24 * 7
)

# ========= FIREBASE SETUP =========
cred_path = BASE_DIR / "serviceAccountKey.json"
if not cred_path.exists():
    raise FileNotFoundError("serviceAccountKey.json missing! Place it at project root.")

cred = credentials.Certificate(str(cred_path))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

FirebaseDB.initialize()

# ========= SERVICES =========
validation_service = ValidationService()

# ========= Pydantic helper models =========
class GoogleAuthPayload(BaseModel):
    idToken: str

# Removed AnalyzeRequest as it's no longer needed

# include final_report routes so they share the same `app` (and session middleware)
app.include_router(final_router)

# ========= ROUTES - AUTH & PAGES =========
@app.get("/final", response_class=HTMLResponse)
async def final_page(request: Request):
    user = request.session.get("user")
    if not user:
        # redirect to home if not signed-in (keeps behavior consistent)
        return RedirectResponse(url="/", status_code=302)
    # Render templates/final.html with user context
    return templates.TemplateResponse("final.html", {"request": request, "user": user})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("history.html", {"request": request, "user": user})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("welcome.html", {"request": request, "user": user})
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/google")
async def auth_google(payload: GoogleAuthPayload, request: Request):
    try:
        decoded_token = firebase_auth.verify_id_token(payload.idToken)
        user_info = {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
        }
        request.session["user"] = user_info
        return {"status": "ok"}
    except Exception as e:
        print("Firebase verify error:", e)
        return JSONResponse({"status": "error", "detail": "Invalid or expired token"}, status_code=400)

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# =========================================
# COMMENT ANALYZER
# =========================================
@app.get("/analyzer", response_class=HTMLResponse)
async def analyzer_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("comments.html", {"request": request})

@app.post("/api/analyze")
async def api_analyze(request: Request):
    try:
        payload = await request.json()
        url = payload.get("post_url", "").strip()
    except:
        url = ""
    if not url:
        return JSONResponse({"error": "Please enter a Reddit or X/Twitter post URL."}, status_code=400)

    data = analyze_url(url)
    if not data or "error" in data:
        return JSONResponse({"error": data.get("error", "Unknown error while fetching comments.")}, status_code=400)

    current_user = None
    try:
        user = request.session.get("user")
        if user and user.get("uid"):
            current_user = user
            try:
                users_col = FirebaseDB.get_collection("users")
                user_doc_ref = users_col.document(user["uid"])
                query = user_doc_ref.collection("ideas").order_by("created_at", direction=firestore.Query.DESCENDING).limit(5)
                idea_docs = query.stream()
                user_ideas = []
                for doc in idea_docs:
                    d = doc.to_dict() or {}
                    idea_input = d.get("idea_input") or {}
                    def _t(x, n=500):
                        if not x:
                            return ""
                        s = str(x)
                        return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."
                    snippet = {
                        "idea_id": d.get("idea_id") or doc.id,
                        "created_at": d.get("created_at"),
                        "idea_name": _t(idea_input.get("idea_name", "")),
                        "problem": _t(idea_input.get("problem", "")),
                        "solution": _t(idea_input.get("solution", "")),
                        "key_features": _t(idea_input.get("key_features", "")),
                        "uniqueness": _t(idea_input.get("uniqueness", "")),
                    }
                    user_ideas.append(snippet)
                if user_ideas:
                    data["user_ideas"] = user_ideas
            except Exception as e:
                print("Warning: failed to fetch user ideas:", e)
    except Exception:
        pass

    try:
        analysis = analyze_comments_with_gemini(data)
    except Exception as e:
        print("ERROR in Gemini analysis:", e)
        return JSONResponse({"error": f"Analysis failed: {e}"}, status_code=500)

    comment_summary_id = None
    if current_user and current_user.get("uid"):
        try:
            now_iso = datetime.utcnow().isoformat() + "Z"
            users_col = FirebaseDB.get_collection("users")
            user_doc_ref = users_col.document(current_user["uid"])
            user_doc_ref.set({
                "email": current_user.get("email"),
                "name": current_user.get("name"),
                "last_analyzed_at": now_iso
            }, merge=True)

            comment_subcol = user_doc_ref.collection("Comment Summary")
            cs_doc_ref = comment_subcol.document()
            cs_payload = {
                "summary_id": cs_doc_ref.id,
                "created_at": now_iso,
                "post_url": url,
                "platform": data.get("platform"),
                "post_title": data.get("post_title") or data.get("text") or "",
                "raw_post": {
                    "post_data": data.get("post_title") or data.get("text") or "",
                    "post_body": data.get("post_text", "")
                },
                "analysis": analysis,
                "preview": {
                    "idea": (analysis.get("idea")[:400] + "...") if isinstance(analysis.get("idea"), str) and len(analysis.get("idea")) > 400 else analysis.get("idea"),
                    "summary": (analysis.get("summary")[:400] + "...") if isinstance(analysis.get("summary"), str) and len(analysis.get("summary")) > 400 else analysis.get("summary")
                }
            }
            cs_doc_ref.set(cs_payload)
            comment_summary_id = cs_doc_ref.id
            print(f"✅ Saved comment summary: users/{current_user['uid']}/Comment Summary/{cs_doc_ref.id}")
        except Exception as e:
            print("Warning: failed to save comment summary to Firestore:", e)

    resp = {"results": data, "analysis": analysis}
    if comment_summary_id:
        resp["comment_summary_id"] = comment_summary_id

    return resp

# =========================================
# STARTUP VALIDATOR PAGES & API
# =========================================
@app.get("/evaluator", response_class=HTMLResponse)
async def evaluator_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("evaluator.html", {"request": request})

@app.post("/api/validate")
async def validate_idea(idea_input: IdeaInput, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        print("\n" + "=" * 60)
        print("📥 NEW VALIDATION REQUEST")
        print(f"  User: {user.get('email')}")
        print(f"  Idea: {idea_input.idea_name}")
        print("=" * 60)

        validation_report: ValidationReport = await validation_service.validate_idea(idea_input)

        idea_dict = idea_input.model_dump()
        report_dict = validation_report.model_dump(by_alias=True, exclude={"id"})

        now_iso = datetime.utcnow().isoformat() + "Z"
        report_dict["user_id"] = user["uid"]
        report_dict["user_email"] = user["email"]
        report_dict["saved_at"] = now_iso

        global_col = FirebaseDB.get_collection(VALIDATIONS_COLLECTION)
        global_doc_ref = global_col.document()
        global_doc_ref.set(report_dict)
        print(f"  ✅ Global validation saved with ID: {global_doc_ref.id}")

        users_col = FirebaseDB.get_collection("users")
        user_uid = user["uid"]
        user_doc_ref = users_col.document(user_uid)

        user_doc_ref.set({
            "email": user.get("email"),
            "name": user.get("name"),
            "last_validation_at": now_iso
        }, merge=True)

        ideas_subcol = user_doc_ref.collection("ideas")
        idea_doc_ref = ideas_subcol.document()
        idea_payload = {
            "idea_id": idea_doc_ref.id,
            "created_at": now_iso,
            "idea_input": idea_dict,
            "status": "validated",
        }
        idea_doc_ref.set(idea_payload)
        print(f"  ✅ User idea saved: users/{user_uid}/ideas/{idea_doc_ref.id}")

        ai_subcol = user_doc_ref.collection("AI Summary")
        ai_doc_ref = ai_subcol.document()
        final_summary = validation_report.final_summary.model_dump()
        ai_payload = {
            "summary_id": ai_doc_ref.id,
            "created_at": now_iso,
            "idea_ref": idea_doc_ref.id,
            "startup_validation_id": global_doc_ref.id,
            "final_summary": final_summary,
        }
        ai_doc_ref.set(ai_payload)
        print(f"  ✅ AI summary saved: users/{user_uid}/AI Summary/{ai_doc_ref.id}")

        validation_report_dict = validation_report.model_dump()
        validation_report_dict["_id"] = global_doc_ref.id

        return {
            "success": True,
            "message": "Validation completed successfully",
            "report_id": global_doc_ref.id,
            "data": validation_report_dict
        }

    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# =========================================
# LIST USER IDEAS & SUMMARIES
# =========================================
@app.get("/api/my/ideas")
async def list_my_ideas(request: Request, limit: int = 50):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_doc_ref = FirebaseDB.get_collection("users").document(user["uid"])
        query = user_doc_ref.collection("ideas").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        out = []
        for doc in docs:
            d = doc.to_dict()
            d["_id"] = doc.id
            out.append(d)
        return {"success": True, "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list ideas: {e}")

@app.get("/api/my/summaries")
async def list_my_summaries(request: Request, limit: int = 50):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_doc_ref = FirebaseDB.get_collection("users").document(user["uid"])
        query = user_doc_ref.collection("AI Summary").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        out = []
        for doc in docs:
            d = doc.to_dict()
            d["_id"] = doc.id
            out.append(d)
        return {"success": True, "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list summaries: {e}")

@app.get("/api/my/comment-summaries")
async def list_my_comment_summaries(request: Request, limit: int = 50):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_doc_ref = FirebaseDB.get_collection("users").document(user["uid"])
        query = user_doc_ref.collection("Comment Summary").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        out = []
        for doc in docs:
            d = doc.to_dict()
            d["_id"] = doc.id
            out.append(d)
        return {"success": True, "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list comment summaries: {e}")

@app.get("/api/my/final-reports")
async def list_my_final_reports(request: Request, limit: int = 50):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_doc_ref = FirebaseDB.get_collection("users").document(user["uid"])
        query = user_doc_ref.collection("Final Reports").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        out = []
        for doc in docs:
            d = doc.to_dict()
            d["_id"] = doc.id
            out.append(d)
        return {"success": True, "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list final reports: {e}")

# =========================================
# REPORTS CRUD (global_validations)
# =========================================
@app.get("/api/reports")
async def get_all_reports(request: Request, limit: int = 10):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        collection = FirebaseDB.get_collection(VALIDATIONS_COLLECTION)
        docs = collection.where("user_id", "==", user["uid"]).limit(limit).stream()
        reports = []
        for doc in docs:
            report = doc.to_dict()
            report["_id"] = doc.id
            reports.append(report)
        return {"success": True, "data": reports, "total": len(reports)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        collection = FirebaseDB.get_collection(VALIDATIONS_COLLECTION)
        doc = collection.document(report_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        report = doc.to_dict()
        if report.get("user_id") != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        report["_id"] = doc.id
        return {"success": True, "data": report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        collection = FirebaseDB.get_collection(VALIDATIONS_COLLECTION)
        doc = collection.document(report_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        report = doc.to_dict()
        if report.get("user_id") != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        collection.document(report_id).delete()
        return {"success": True, "message": "Report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

# =========================================
# DEV DEBUG SESSION ENDPOINT
# =========================================
@app.get("/dev/debug-session")
async def debug_session(request: Request):
    # dev-only: returns session info so you can inspect cookie visibility
    return JSONResponse({
        "has_session": bool(request.session.get("user")),
        "session_user": request.session.get("user")
    })

# =========================================
# HEALTH CHECK
# =========================================
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "api": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["comment_analyzer", "startup_validator"]
    }

# =========================================
# IDEA ANALYZER (from templates/)
# =========================================
@app.get("/idea-analyzer", response_class=HTMLResponse)
async def idea_analyzer_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("idea_analyzer.html", {"request": request})

@app.post("/api/analyze-idea")
async def api_analyze_idea(request: Request, idea: str = Form(...)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    idea = idea.strip()
    if not idea:
        return JSONResponse({"error": "Please provide an idea."}, status_code=400)

    try:
        # Run the idea analyzer in a threadpool since it may involve I/O
        results = await run_in_threadpool(run_idea_analyzer, idea)
        return {"results": results}
    except Exception as e:
        print("ERROR in idea analyzer:", e)
        return JSONResponse({"error": f"Analysis failed: {e}"}, status_code=500)

# =========================================
# RUN SERVER (dev)
# =========================================
if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=True)