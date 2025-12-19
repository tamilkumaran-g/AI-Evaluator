import React from "react";
import { useNavigate } from "react-router-dom";
import myveLogo from "../assets/myvelogo.png";

interface LayoutShellProps {
  title?: string;
  rightActions?: React.ReactNode;
  variant?: "marketing" | "app";
  children: React.ReactNode;
}

const LayoutShell: React.FC<LayoutShellProps> = ({
  title,
  rightActions,
  variant = "app",
  children,
}) => {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7fb] text-slate-900">
      {/* NAVBAR */}
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center px-4 sm:px-6">
          {/* Logo + title */}
          <div
            className="flex cursor-pointer items-center gap-3"
            onClick={() => navigate("/")}
          >
            <img
              src={myveLogo}
              alt="Myve Logo"
              className="h-10 w-auto object-contain"
            />
            {variant === "app" && title && (
              <span className="text-sm font-semibold text-slate-900">
                {title}
              </span>
            )}
          </div>

          {/* Right side actions */}
          <div className="ml-auto flex items-center gap-3">
            {rightActions}
          </div>
        </div>
      </nav>

      {/* PAGE BODY */}
      <main className="flex-1 w-full">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-10">
          {children}
        </div>
      </main>
    </div>
  );
};

export default LayoutShell;