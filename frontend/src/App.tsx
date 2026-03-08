import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Layers, Database, Play, FileText, MessageSquare, Zap, Shield } from "lucide-react";

import ModelPage from "./pages/ModelPage";
import DatasetPage from "./pages/DatasetPage";
import TrainingPage from "./pages/TrainingPage";
import RAGPage from "./pages/RAGPage";
import QAPage from "./pages/QAPage";
import RLHFPage from "./pages/RLHFPage";

const queryClient = new QueryClient();

const NAV = [
  { to: "/model", label: "모델 선택",   icon: Layers,        step: "06" },
  { to: "/",      label: "데이터 선택", icon: Database,      step: "06" },
  { to: "/training", label: "LLM 학습", icon: Play,          step: "06" },
  { to: "/rag",   label: "문서 업로드", icon: FileText,      step: "06" },
  { to: "/qa",    label: "Q&A",         icon: MessageSquare, step: "06" },
  { to: "/rlhf",  label: "RLHF 개선",  icon: Zap,           step: "06" },
];

function Sidebar() {
  return (
    <aside className="w-60 min-h-screen flex flex-col py-7 px-4 shrink-0"
      style={{ background: "rgba(8,12,20,0.95)", borderRight: "1px solid rgba(255,255,255,0.05)" }}>

      <div className="px-2 mb-8">
        <div className="flex items-center gap-2.5 mb-1">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)" }}>
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-white tracking-tight">HR AI</span>
        </div>
        <p className="text-xs ml-9.5" style={{ color: "#475569" }}>완전 로컬 LLM 플랫폼</p>
      </div>

      <nav className="flex flex-col gap-0.5 flex-1">
        {NAV.map(({ to, label, icon: Icon, step }) => (
          <NavLink key={to} to={to} end={to === "/"}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive ? "text-white" : "text-slate-500 hover:text-slate-300"
              }`
            }
            style={({ isActive }) => isActive
              ? { background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.2)" }
              : { background: "transparent", border: "1px solid transparent" }
            }
          >
            {({ isActive }) => (
              <>
                <div className={`w-6 h-6 rounded-md flex items-center justify-center transition-all ${
                  isActive ? "text-blue-400" : "text-slate-600 group-hover:text-slate-400"
                }`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="flex-1">{label}</span>
                <span className={`text-[10px] font-mono transition-all ${
                  isActive ? "text-blue-500" : "text-slate-700 group-hover:text-slate-600"
                }`}>{step}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mx-2 mt-6 p-3 rounded-lg"
        style={{ background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.12)" }}>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-emerald-400">완전 로컬 실행 중</span>
        </div>
        <p className="text-[11px] leading-relaxed" style={{ color: "#475569" }}>
          모든 데이터가 외부로 전송되지 않습니다
        </p>
      </div>
    </aside>
  );
}

function Layout() {
  return (
    <div className="flex min-h-screen" style={{ background: "#080c14" }}>
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/model" element={<ModelPage />} />
          <Route path="/" element={<DatasetPage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/rag" element={<RAGPage />} />
          <Route path="/qa" element={<QAPage />} />
          <Route path="/rlhf" element={<RLHFPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
