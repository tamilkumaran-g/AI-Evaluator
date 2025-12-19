import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import LayoutShell from "../components/LayoutShell";

const NotFound = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <LayoutShell title="Page not found">
      <div className="mx-auto max-w-xl py-20">
        <div className="rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <h1 className="mb-4 text-5xl font-bold text-slate-900">404</h1>
          <p className="mb-6 text-lg text-slate-600">
            Oops! This page could not be found.
          </p>
          <button
            onClick={() => navigate("/")}
            className="rounded-full bg-[#1b9cc8] px-4 py-2 text-sm font-medium text-white hover:bg-[#1787ad]"
          >
            Back to home
          </button>
        </div>
      </div>
    </LayoutShell>
  );
};

export default NotFound;
