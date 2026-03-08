import { useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { startTraining, fetchTrainingStatus, stopTraining } from "../api";
import { Play, Square, CheckCircle2, AlertCircle, Loader2, ArrowRight, Activity } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const STATUS_META: Record<string, { label: string; color: string; bg: string }> = {
  idle:      { label: "대기 중",    color: "#475569", bg: "rgba(71,85,105,0.12)" },
  running:   { label: "학습 중",    color: "#60a5fa", bg: "rgba(59,130,246,0.12)" },
  completed: { label: "학습 완료",  color: "#34d399", bg: "rgba(16,185,129,0.12)" },
  failed:    { label: "오류",       color: "#f87171", bg: "rgba(239,68,68,0.12)" },
  stopped:   { label: "중지됨",     color: "#fb923c", bg: "rgba(249,115,22,0.12)" },
  stopping:  { label: "중지 중...", color: "#fb923c", bg: "rgba(249,115,22,0.12)" },
};

export default function TrainingPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const lossHistory = useRef<{ step: number; loss: number }[]>([]);

  const { data: status } = useQuery({
    queryKey: ["training-status"],
    queryFn: fetchTrainingStatus,
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "running" || s === "stopping" ? 2000 : false;
    },
  });

  useEffect(() => {
    if (status?.status === "running" && status.loss > 0) {
      lossHistory.current = [...lossHistory.current.slice(-99), { step: status.step, loss: status.loss }];
    }
  }, [status?.step]);

  const startMut = useMutation({
    mutationFn: () => {
      const ids = JSON.parse(sessionStorage.getItem("selected_datasets") || "[]");
      return startTraining({ dataset_ids: ids });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training-status"] }),
  });

  const stopMut = useMutation({
    mutationFn: stopTraining,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training-status"] }),
  });

  const isRunning = status?.status === "running" || status?.status === "stopping";
  const isDone = status?.status === "completed";
  const pct = Math.round((status?.progress ?? 0) * 100);
  const meta = STATUS_META[status?.status ?? "idle"];

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>STEP 03</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">LLM 학습</h1>
        <p style={{ color: "#64748b" }} className="text-sm">모든 연산이 로컬 서버에서만 진행됩니다. 외부로 데이터가 전송되지 않습니다.</p>
      </div>

      {/* 상태 카드 */}
      <div className="p-6 rounded-xl mb-5" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5"
              style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.color}30` }}>
              {status?.status === "running" && <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse inline-block" />}
              {status?.status === "completed" && <CheckCircle2 className="w-3 h-3" />}
              {status?.status === "failed" && <AlertCircle className="w-3 h-3" />}
              {meta.label}
            </div>
            <span className="text-sm" style={{ color: "#475569" }}>{status?.message}</span>
          </div>

          <div className="flex gap-2">
            {!isRunning && !isDone && (
              <button onClick={() => startMut.mutate()} disabled={startMut.isPending}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                style={{ background: "linear-gradient(135deg,#3b82f6,#6366f1)", color: "white", boxShadow: "0 0 20px rgba(59,130,246,0.2)" }}>
                {startMut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                학습 시작
              </button>
            )}
            {isRunning && (
              <button onClick={() => stopMut.mutate()} disabled={status?.status === "stopping"}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                style={{ background: "rgba(239,68,68,0.12)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
                <Square className="w-4 h-4" />
                중지
              </button>
            )}
            {isDone && (
              <button onClick={() => navigate("/rag")}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
                style={{ background: "rgba(16,185,129,0.12)", color: "#34d399", border: "1px solid rgba(16,185,129,0.2)" }}>
                다음 단계
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* 진행률 */}
        <div className="mb-4">
          <div className="flex justify-between text-xs mb-2" style={{ color: "#475569" }}>
            <span>진행률</span>
            <span>{pct}%{status?.status === "running" ? ` · epoch ${status.epoch}/${status.total_epochs} · step ${status.step}` : ""}</span>
          </div>
          <div className="w-full rounded-full h-1.5" style={{ background: "rgba(255,255,255,0.05)" }}>
            <div className="h-1.5 rounded-full transition-all duration-700"
              style={{
                width: `${pct}%`,
                background: isDone ? "linear-gradient(90deg,#10b981,#34d399)" : "linear-gradient(90deg,#3b82f6,#6366f1)",
                boxShadow: pct > 0 ? "0 0 8px rgba(59,130,246,0.4)" : "none",
              }} />
          </div>
        </div>

        {/* 지표 */}
        {(isRunning || isDone) && (
          <div className="grid grid-cols-3 gap-3 pt-4" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
            {[
              { label: "현재 Loss", value: status?.loss?.toFixed(4) ?? "-" },
              { label: "경과 시간", value: formatTime(status?.elapsed_seconds ?? 0) },
              { label: "Step", value: (status?.step ?? 0).toLocaleString() },
            ].map(({ label, value }) => (
              <div key={label}>
                <p className="text-[11px] mb-1" style={{ color: "#475569" }}>{label}</p>
                <p className="text-lg font-semibold text-white font-mono">{value}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Loss 그래프 */}
      {lossHistory.current.length > 1 && (
        <div className="p-5 rounded-xl" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-3.5 h-3.5" style={{ color: "#60a5fa" }} />
            <p className="text-xs font-medium" style={{ color: "#64748b" }}>Loss 추이</p>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={lossHistory.current}>
              <XAxis dataKey="step" stroke="#1e293b" tick={{ fontSize: 10, fill: "#334155" }} />
              <YAxis stroke="#1e293b" tick={{ fontSize: 10, fill: "#334155" }} domain={["auto", "auto"]} />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#475569" }}
                itemStyle={{ color: "#60a5fa" }}
                labelFormatter={(v) => `step ${v}`}
              />
              <Line type="monotone" dataKey="loss" stroke="#3b82f6" dot={false} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function formatTime(s: number) {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = Math.floor(s % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}
