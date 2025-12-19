# final_report.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os
import json
import traceback

import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

if os.path.exists(os.path.join(BASE_DIR, "serviceAccountKey.json")) and not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(BASE_DIR, "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)

db = firestore.client()

try:
    import google.generativeai as genai

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
        except Exception:
            pass
except Exception:
    genai = None

router = APIRouter()


def _latest_doc_from_subcol(uid: str, subcol_name: str):
    try:
        col = db.collection("users").document(uid).collection(subcol_name)
        q = col.order_by("created_at", direction=firestore.Query.DESCENDING).limit(1)
        docs = list(q.stream())
        if not docs:
            return None
        d = docs[0].to_dict()
        d["_id"] = docs[0].id
        return d
    except Exception as e:
        print("error fetching latest doc:", e)
        traceback.print_exc()
        return None


@router.get("/final", response_class=HTMLResponse)
async def final_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("final.html", {"request": request, "user": user})


@router.get("/api/final/status")
async def final_status(request: Request):
    user = request.session.get("user")
    if not user or not user.get("uid"):
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    uid = user["uid"]
    try:
        ai = _latest_doc_from_subcol(uid, "AI Summary")
        cs = _latest_doc_from_subcol(uid, "Comment Summary")
        return {
            "has_ai_summary": bool(ai),
            "ai_summary": ai,
            "has_comment_summary": bool(cs),
            "comment_summary": cs,
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def _build_prompt(ai_summary: dict, comment_summary: dict) -> str:
    ai_text = json.dumps(ai_summary.get("final_summary") if isinstance(ai_summary, dict) else ai_summary, indent=2,
                         ensure_ascii=False)
    cs_text = json.dumps(comment_summary.get("analysis") if isinstance(comment_summary, dict) else comment_summary,
                         indent=2, ensure_ascii=False)

    prompt = f"""
You are a brutally honest startup/product validator. You analyze ideas based on market signals, problem-solution fit, and user feedback.

AI SUMMARY (structured):
\"\"\"{ai_text}\"\"\"

COMMENT SUMMARY (what real users said / analysis):
\"\"\"{cs_text}\"\"\"

Return EXACTLY a JSON object (no extra text) with these fields:

{{
  "idea": "1-2 sentence plain summary of the idea",
  "problem_faced": "1 short paragraph describing the problem this idea tries to solve",
  "your_solution": "1 short paragraph describing the proposed solution",
  "questions_and_answers": {{
    "1": {{"question":"Does this idea really solve the problem?","answer":"yes/no","explain":"1 short sentence"}},
    "2": {{"question":"Can you market this easily via social media?","answer":"yes/no","explain":"1 short sentence"}},
    "3": {{"question":"Will users pay for this product?","answer":"yes/no","explain":"1 short sentence"}},
    "4": {{"question":"Is the problem painful enough for users to seek a solution?","answer":"yes/no","explain":"1 short sentence"}},
    "5": {{"question":"Based on comments, is there genuine interest or excitement?","answer":"yes/no","explain":"1 short sentence"}}
  }},
  "final_verdict": {{"can_build": "yes" or "no", "headline":"SHORT verdict headline (e.g. STRONG SIGNAL or NEEDS VALIDATION)"}},
  "recommendations": ["Three concise recommendations to improve the idea (3 items)"],
  "final_thoughts": "One paragraph final thoughts including execution advice and 3 quick execution tips.",
  "validation_score": 0-100
}}

**SCORING GUIDELINES:**
- 0-30: Not ready - Major red flags, rethink problem or market
- 31-50: Weak - Significant issues, needs major changes
- 51-70: Promising - Has potential but needs refinement
- 71-85: Strong - Good signals, build MVP and test
- 86-100: Excellent - Strong market signals, build immediately

**RULES FOR SCORING:**
1. Start with 50 points as baseline
2. Add +10 for each "yes" answer (5 questions = max +50)
3. Add +20 if comment analysis shows genuine excitement/validation
4. Subtract -15 if comment analysis shows significant skepticism
5. Add +10 if problem is clearly defined and painful
6. Subtract -10 if solution seems overly complex
7. Add +5 for each specific positive mention in comments
8. Subtract -5 for each major criticism in comments
9. Adjust based on market size/opportunity mentioned
10. Final score should be 0-100

**final_verdict.can_build RULES:**
- "yes" if score >= 60 AND at least 3 of 5 questions are "yes"
- "no" otherwise

Be concise, brutal, and data-driven in your assessment.
"""
    return prompt


def _parse_json_from_text(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        s = raw.find("{")
        e = raw.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(raw[s:e + 1])
            except Exception:
                return None
        return None


def _calculate_fallback_score(parsed: dict) -> int:
    """Calculate a fallback score if Gemini doesn't provide one"""
    try:
        q = parsed.get("questions_and_answers", {})
        yes_count = 0
        total_questions = 0

        for key, item in q.items():
            if isinstance(item, dict):
                answer = item.get("answer", "").lower()
                if answer == "yes":
                    yes_count += 1
                total_questions += 1

        if total_questions == 0:
            return 50

        base_score = (yes_count / total_questions) * 100

        # Adjust based on final verdict
        if parsed.get("final_verdict", {}).get("can_build") == "yes":
            base_score = min(100, base_score + 15)

        return int(base_score)
    except Exception:
        return 50


@router.post("/api/generate-final-report")
async def generate_final_report(request: Request):
    user = request.session.get("user")
    if not user or not user.get("uid"):
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    uid = user["uid"]

    ai = _latest_doc_from_subcol(uid, "AI Summary")
    cs = _latest_doc_from_subcol(uid, "Comment Summary")

    if not ai or not cs:
        return JSONResponse({"error": "Both AI summary and Comment summary are required."}, status_code=400)

    prompt = _build_prompt(ai, cs)

    if genai is None:
        return JSONResponse({"error": "GenAI library not available or not configured."}, status_code=500)

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        parsed = _parse_json_from_text(raw)
        if parsed is None:
            return JSONResponse({"error": "Failed to parse model output as JSON.", "raw": raw}, status_code=500)

        # Ensure validation_score exists and is valid
        if "validation_score" not in parsed or not isinstance(parsed["validation_score"], (int, float)):
            parsed["validation_score"] = _calculate_fallback_score(parsed)

        # Ensure score is between 0-100
        parsed["validation_score"] = max(0, min(100, int(parsed["validation_score"])))

        try:
            now_iso = datetime.utcnow().isoformat() + "Z"
            final_col = db.collection("users").document(uid).collection("Final Reports")
            doc_ref = final_col.document()
            payload = {
                "report_id": doc_ref.id,
                "created_at": now_iso,
                "ai_summary_ref": ai.get("summary_id") or ai.get("_id"),
                "comment_summary_ref": cs.get("summary_id") or cs.get("_id"),
                "generated_report": parsed,
            }
            doc_ref.set(payload)
            parsed["_saved_report_id"] = doc_ref.id
        except Exception as e:
            print("warning saving final report:", e)

        return parsed
    except Exception as e:
        print("gemini call error:", e)
        return JSONResponse({"error": f"Gemini generation failed: {str(e)}"}, status_code=500)