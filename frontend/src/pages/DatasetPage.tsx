import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  fetchDatasets, estimateTraining,
  fetchDownloadStatus, startDownload,
} from "../api";
import type { DatasetInfo, TrainingEstimate, DownloadStatus } from "../api";
import {
  CheckCircle2, Circle, ArrowRight, Cpu, Clock, Hash,
  Download, Loader2, Key, AlertCircle,
} from "lucide-react";

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  "일반 지식": { bg: "rgba(59,130,246,0.08)",  text: "#60a5fa", border: "rgba(59,130,246,0.2)" },
  "법률":      { bg: "rgba(139,92,246,0.08)", text: "#a78bfa", border: "rgba(139,92,246,0.2)" },
  "노동·인사": { bg: "rgba(16,185,129,0.08)",  text: "#34d399", border: "rgba(16,185,129,0.2)" },
};

const NEEDS_API_KEY = new Set([
  "law_documents","court_cases","labor_law","labor_union_law",
  "social_security_law","civil_law","employment_equality",
  "privacy_law","disability_law","foreign_worker_law","hr_admin",
]);

function fmtTokens(n: number) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B 토큰`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)}M 토큰`;
  return `${(n / 1e3).toFixed(0)}K 토큰`;
}
function fmtParams(n: number) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)}M`;
  return n.toLocaleString();
}

// ── 개별 데이터셋 카드 ──────────────────────────────────────────
function DatasetCard({ d, selected, onToggle, apiKey }: {
  d: DatasetInfo; selected: boolean; onToggle: () => void; apiKey: string;
}) {
  const qc = useQueryClient();
  const { data: dlStatus } = useQuery<DownloadStatus>({
    queryKey: ["dl-status", d.id],
    queryFn: () => fetchDownloadStatus(d.id),
    refetchInterval: (q) => q.state.data?.status === "running" ? 2000 : false,
  });

  const dlMut = useMutation({
    mutationFn: () => startDownload(d.id, NEEDS_API_KEY.has(d.id) ? apiKey : undefined),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dl-status", d.id] }),
  });

  const isReady = dlStatus?.status === "ready" || dlStatus?.status === "completed";
  const isRunning = dlStatus?.status === "running";
  const isFailed = dlStatus?.status === "failed";
  const pct = Math.round((dlStatus?.progress ?? 0) * 100);

  return (
    <div className="p-4 rounded-xl transition-all duration-150"
      style={{
        background: selected ? "rgba(59,130,246,0.1)" : "rgba(255,255,255,0.03)",
        border: selected ? "1px solid rgba(59,130,246,0.35)" : "1px solid rgba(255,255,255,0.07)",
      }}>
      <div className="flex items-start gap-3">
        {/* 선택 체크 */}
        <button onClick={onToggle} disabled={!isReady} className="mt-0.5 shrink-0">
          {selected
            ? <CheckCircle2 className="w-4 h-4" style={{ color: "#60a5fa" }} />
            : <Circle className="w-4 h-4" style={{ color: isReady ? "#475569" : "#2d3748" }} />
          }
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <p className="font-medium text-sm" style={{ color: selected ? "#fff" : "#e2e8f0" }}>
              {d.name}
            </p>

            {/* 다운로드 상태 뱃지 */}
            {isReady ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full shrink-0"
                style={{ background: "rgba(16,185,129,0.12)", color: "#34d399", border: "1px solid rgba(16,185,129,0.2)" }}>
                ✓ 준비됨
              </span>
            ) : isRunning ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 shrink-0"
                style={{ background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>
                <Loader2 className="w-2.5 h-2.5 animate-spin" /> {pct}%
              </span>
            ) : isFailed ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full shrink-0"
                style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
                <AlertCircle className="w-2.5 h-2.5 inline mr-0.5" />오류
              </span>
            ) : (
              <button onClick={() => dlMut.mutate()} disabled={dlMut.isPending || (NEEDS_API_KEY.has(d.id) && !apiKey)}
                className="text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 shrink-0 transition-all"
                style={NEEDS_API_KEY.has(d.id) && !apiKey
                  ? { background: "rgba(255,255,255,0.03)", color: "#334155", border: "1px solid rgba(255,255,255,0.06)", cursor: "not-allowed" }
                  : { background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.25)", cursor: "pointer" }
                }>
                <Download className="w-2.5 h-2.5" />
                다운로드
              </button>
            )}
          </div>

          <p className="text-xs leading-relaxed mb-2" style={{ color: "#94a3b8" }}>
            {d.description}
          </p>

          {/* 다운로드 진행 바 */}
          {isRunning && (
            <div className="mb-2">
              <div className="w-full rounded-full h-1" style={{ background: "rgba(255,255,255,0.06)" }}>
                <div className="h-1 rounded-full transition-all"
                  style={{ width: `${pct}%`, background: "linear-gradient(90deg,#3b82f6,#6366f1)" }} />
              </div>
              <p className="text-[10px] mt-1" style={{ color: "#475569" }}>{dlStatus?.message}</p>
            </div>
          )}

          <div className="flex gap-3">
            <span className="text-[11px] font-medium" style={{ color: selected ? "#60a5fa" : "#64748b" }}>
              {fmtTokens(d.estimated_tokens)}
            </span>
            <span className="text-[11px]" style={{ color: "#475569" }}>{d.size_gb} GB</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── 메인 페이지 ────────────────────────────────────────────────
export default function DatasetPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [estimate, setEstimate] = useState<TrainingEstimate | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);

  const { data: datasets = [], isLoading } = useQuery({ queryKey: ["datasets"], queryFn: fetchDatasets });

  const estimateMut = useMutation({
    mutationFn: (ids: string[]) => estimateTraining({ dataset_ids: ids }),
    onSuccess: setEstimate,
  });

  const toggle = (id: string) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
    if (next.size > 0) estimateMut.mutate([...next]);
    else setEstimate(null);
  };

  const byCategory = datasets.reduce<Record<string, DatasetInfo[]>>((acc, d) => {
    (acc[d.category] ??= []).push(d);
    return acc;
  }, {});

  const goToTraining = () => {
    sessionStorage.setItem("selected_datasets", JSON.stringify([...selected]));
    navigate("/training");
  };

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono px-2 py-0.5 rounded"
            style={{ background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>
            STEP 02
          </span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">학습 데이터 선택</h1>
        <p className="text-sm leading-relaxed" style={{ color: "#94a3b8" }}>
          데이터를 먼저 다운로드한 후 선택하면 실제 학습에 사용됩니다.
        </p>
      </div>

      {/* API 키 입력 (법령 데이터용) */}
      <div className="mb-8 p-4 rounded-xl"
        style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
        <button onClick={() => setShowApiKey(!showApiKey)}
          className="flex items-center gap-2 text-sm font-medium w-full text-left"
          style={{ color: "#94a3b8" }}>
          <Key className="w-4 h-4" style={{ color: "#a78bfa" }} />
          국가법령정보센터 API 키 (법률·노동 데이터 다운로드 시 필요)
          <span className="ml-auto text-xs" style={{ color: "#475569" }}>{showApiKey ? "접기 ▲" : "펼치기 ▼"}</span>
        </button>
        {showApiKey && (
          <div className="mt-3 space-y-2">
            <input
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="API 키를 입력하세요"
              className="w-full text-sm px-3 py-2.5 rounded-lg outline-none"
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", color: "#e2e8f0" }}
            />
            <p className="text-xs" style={{ color: "#475569" }}>
              무료 발급: <span style={{ color: "#60a5fa" }}>open.law.go.kr</span> → 오픈API 신청 (당일 발급)
            </p>
          </div>
        )}
      </div>

      {/* 데이터셋 목록 */}
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-6 h-6 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(byCategory).map(([category, items]) => {
            const c = CATEGORY_COLORS[category] ?? { bg: "rgba(255,255,255,0.03)", text: "#94a3b8", border: "rgba(255,255,255,0.08)" };
            return (
              <div key={category}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs font-medium px-2.5 py-1 rounded-full"
                    style={{ background: c.bg, color: c.text, border: `1px solid ${c.border}` }}>
                    {category}
                  </span>
                  <div className="flex-1 h-px" style={{ background: "rgba(255,255,255,0.06)" }} />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {items.map((d) => (
                    <DatasetCard key={d.id} d={d}
                      selected={selected.has(d.id)}
                      onToggle={() => toggle(d.id)}
                      apiKey={apiKey}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 예상 정보 */}
      {estimate && (
        <div className="mt-8 p-5 rounded-xl"
          style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <p className="text-xs font-medium mb-4" style={{ color: "#64748b" }}>학습 예상 정보</p>
          <div className="grid grid-cols-3 gap-4">
            {[
              { icon: <Hash className="w-3.5 h-3.5" />, label: "총 토큰", value: fmtTokens(estimate.total_tokens), color: "#60a5fa" },
              { icon: <Cpu className="w-3.5 h-3.5" />, label: "파라미터", value: fmtParams(estimate.total_parameters), color: "#a78bfa" },
              { icon: <Clock className="w-3.5 h-3.5" />, label: "예상 시간", value: `~${estimate.estimated_hours}h`, color: "#34d399" },
            ].map(({ icon, label, value, color }) => (
              <div key={label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  style={{ background: `${color}18`, color }}>{icon}</div>
                <div>
                  <p className="text-[11px] mb-0.5" style={{ color: "#64748b" }}>{label}</p>
                  <p className="text-sm font-semibold text-white">{value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 다음 버튼 */}
      <div className="mt-6 flex justify-end">
        <button onClick={goToTraining} disabled={selected.size === 0}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={{
            background: selected.size > 0 ? "linear-gradient(135deg,#3b82f6,#6366f1)" : "rgba(255,255,255,0.05)",
            color: selected.size > 0 ? "white" : "#475569",
            cursor: selected.size > 0 ? "pointer" : "not-allowed",
            boxShadow: selected.size > 0 ? "0 0 20px rgba(59,130,246,0.25)" : "none",
          }}>
          학습 시작하기
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
