import { useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  fetchPretrainedModels, fetchSelectedModel,
  selectCustomModel, selectPretrainedModel,
  startModelDownload, downloadCustomModelCode, uploadCustomModelCode,
} from "../api";
import type { PretrainedModel, ModelSelection } from "../api";
import {
  Code2, Sparkles, Download, Upload, CheckCircle2,
  Loader2, ArrowRight, Star, AlertCircle,
} from "lucide-react";

// ── 사전학습 모델 카드 ─────────────────────────────────────
function PretrainedCard({ m, selected, onSelect }: {
  m: PretrainedModel; selected: boolean; onSelect: () => void;
}) {
  const qc = useQueryClient();
  const dlMut = useMutation({
    mutationFn: () => startModelDownload(m.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pretrained-models"] }),
  });

  const isRunning = m.download_status.status === "running";
  const pct = Math.round((m.download_status.progress ?? 0) * 100);

  return (
    <div className="p-5 rounded-xl transition-all"
      style={{
        background: selected ? "rgba(59,130,246,0.08)" : "rgba(255,255,255,0.02)",
        border: selected ? "1px solid rgba(59,130,246,0.35)" : "1px solid rgba(255,255,255,0.06)",
      }}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <p className="font-semibold text-white">{m.name}</p>
            {m.recommended && (
              <span className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full"
                style={{ background: "rgba(251,191,36,0.12)", color: "#fbbf24", border: "1px solid rgba(251,191,36,0.2)" }}>
                <Star className="w-2.5 h-2.5" /> 추천
              </span>
            )}
          </div>
          <p className="text-xs leading-relaxed mb-2" style={{ color: "#94a3b8" }}>{m.description}</p>
          <div className="flex gap-3 text-[11px]">
            <span style={{ color: "#64748b" }}>{m.params}</span>
            <span style={{ color: "#64748b" }}>{m.size_gb} GB</span>
            <span className="px-1.5 py-0.5 rounded" style={{ background: "rgba(255,255,255,0.04)", color: "#94a3b8" }}>
              {m.language}
            </span>
          </div>
        </div>

        {/* 상태/버튼 */}
        <div className="shrink-0">
          {m.ready ? (
            <button onClick={onSelect}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              style={selected
                ? { background: "rgba(59,130,246,0.2)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.4)" }
                : { background: "rgba(16,185,129,0.1)", color: "#34d399", border: "1px solid rgba(16,185,129,0.25)" }
              }>
              {selected ? <><CheckCircle2 className="w-3.5 h-3.5" /> 선택됨</> : "이 모델 사용"}
            </button>
          ) : isRunning ? (
            <span className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg"
              style={{ background: "rgba(59,130,246,0.1)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>
              <Loader2 className="w-3 h-3 animate-spin" /> {pct}%
            </span>
          ) : m.download_status.status === "failed" ? (
            <button onClick={() => dlMut.mutate()}
              className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg"
              style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
              <AlertCircle className="w-3 h-3" /> 재시도
            </button>
          ) : (
            <button onClick={() => dlMut.mutate()} disabled={dlMut.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              style={{ background: "rgba(255,255,255,0.04)", color: "#94a3b8", border: "1px solid rgba(255,255,255,0.08)" }}>
              <Download className="w-3.5 h-3.5" /> 다운로드
            </button>
          )}
        </div>
      </div>

      {/* 다운로드 진행 바 */}
      {isRunning && (
        <div>
          <div className="w-full rounded-full h-1" style={{ background: "rgba(255,255,255,0.06)" }}>
            <div className="h-1 rounded-full transition-all"
              style={{ width: `${pct}%`, background: "linear-gradient(90deg,#3b82f6,#6366f1)" }} />
          </div>
          <p className="text-[10px] mt-1" style={{ color: "#475569" }}>{m.download_status.message}</p>
        </div>
      )}
    </div>
  );
}

// ── 메인 페이지 ────────────────────────────────────────────
export default function ModelPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [track, setTrack] = useState<"custom" | "pretrained" | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);

  const { data: models = [] } = useQuery({
    queryKey: ["pretrained-models"],
    queryFn: fetchPretrainedModels,
    refetchInterval: (q) =>
      q.state.data?.some((m: PretrainedModel) => m.download_status.status === "running") ? 3000 : false,
  });

  const { data: current } = useQuery<ModelSelection>({
    queryKey: ["selected-model"],
    queryFn: fetchSelectedModel,
  });

  const customMut = useMutation({
    mutationFn: selectCustomModel,
    onSuccess: () => {
      setTrack("custom");
      qc.invalidateQueries({ queryKey: ["selected-model"] });
    },
  });

  const pretrainedMut = useMutation({
    mutationFn: (id: string) => selectPretrainedModel(id),
    onSuccess: (_, id) => {
      setSelectedModelId(id);
      qc.invalidateQueries({ queryKey: ["selected-model"] });
    },
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => uploadCustomModelCode(file),
    onSuccess: () => setTrack("custom"),
  });

  const activeTrack = track ?? current?.track;
  const activeModelId = selectedModelId ?? current?.model_id;
  const canProceed = activeTrack === "custom" || (activeTrack === "pretrained" && activeModelId);

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      {/* 헤더 */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono px-2 py-0.5 rounded"
            style={{ background: "rgba(139,92,246,0.12)", color: "#a78bfa", border: "1px solid rgba(139,92,246,0.2)" }}>
            STEP 01
          </span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">모델 선택</h1>
        <p className="text-sm leading-relaxed" style={{ color: "#94a3b8" }}>
          학습 방식을 선택하세요. 직접 설계하거나 검증된 사전학습 모델을 파인튜닝할 수 있습니다.
        </p>
      </div>

      {/* 트랙 선택 */}
      <div className="grid grid-cols-2 gap-4 mb-10">
        {/* 트랙 A */}
        <button onClick={() => { setTrack("custom"); customMut.mutate(); }}
          className="p-6 rounded-xl text-left transition-all"
          style={{
            background: activeTrack === "custom" ? "rgba(139,92,246,0.1)" : "rgba(255,255,255,0.02)",
            border: activeTrack === "custom" ? "1px solid rgba(139,92,246,0.35)" : "1px solid rgba(255,255,255,0.06)",
          }}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
            style={{ background: "rgba(139,92,246,0.12)" }}>
            <Code2 className="w-5 h-5" style={{ color: "#a78bfa" }} />
          </div>
          <div className="flex items-center gap-2 mb-2">
            <p className="font-semibold text-white">직접 설계</p>
            {activeTrack === "custom" && <CheckCircle2 className="w-4 h-4" style={{ color: "#a78bfa" }} />}
          </div>
          <p className="text-xs leading-relaxed" style={{ color: "#64748b" }}>
            현재 GPT 모델 코드를 다운로드해서 직접 수정하고 업로드합니다.
            완전한 스크래치 학습을 원하는 경우 선택하세요.
          </p>
        </button>

        {/* 트랙 B */}
        <button onClick={() => setTrack("pretrained")}
          className="p-6 rounded-xl text-left transition-all"
          style={{
            background: activeTrack === "pretrained" ? "rgba(59,130,246,0.1)" : "rgba(255,255,255,0.02)",
            border: activeTrack === "pretrained" ? "1px solid rgba(59,130,246,0.35)" : "1px solid rgba(255,255,255,0.06)",
          }}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
            style={{ background: "rgba(59,130,246,0.12)" }}>
            <Sparkles className="w-5 h-5" style={{ color: "#60a5fa" }} />
          </div>
          <div className="flex items-center gap-2 mb-2">
            <p className="font-semibold text-white">사전학습 모델</p>
            {activeTrack === "pretrained" && <CheckCircle2 className="w-4 h-4" style={{ color: "#60a5fa" }} />}
          </div>
          <p className="text-xs leading-relaxed" style={{ color: "#64748b" }}>
            Qwen3, LLaMA3, EXAONE 등 검증된 모델을 기반으로 파인튜닝합니다.
            높은 답변 품질을 원한다면 이 방식을 추천합니다.
          </p>
        </button>
      </div>

      {/* 트랙 A: 직접 설계 */}
      {activeTrack === "custom" && (
        <div className="p-6 rounded-xl mb-6"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
          <p className="text-sm font-medium text-white mb-4">모델 코드 관리</p>
          <div className="flex gap-3">
            <button onClick={downloadCustomModelCode}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all"
              style={{ background: "rgba(139,92,246,0.1)", color: "#a78bfa", border: "1px solid rgba(139,92,246,0.2)" }}>
              <Download className="w-4 h-4" />
              현재 코드 다운로드
            </button>
            <button onClick={() => fileRef.current?.click()}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all"
              style={{ background: "rgba(255,255,255,0.04)", color: "#94a3b8", border: "1px solid rgba(255,255,255,0.08)" }}>
              {uploadMut.isPending
                ? <><Loader2 className="w-4 h-4 animate-spin" /> 업로드 중...</>
                : <><Upload className="w-4 h-4" /> 수정된 코드 업로드</>
              }
            </button>
            <input ref={fileRef} type="file" accept=".zip" className="hidden"
              onChange={(e) => e.target.files?.[0] && uploadMut.mutate(e.target.files[0])} />
          </div>
          {uploadMut.isSuccess && (
            <p className="text-xs mt-3" style={{ color: "#34d399" }}>✓ 코드가 업로드되었습니다.</p>
          )}
          <p className="text-xs mt-3 leading-relaxed" style={{ color: "#334155" }}>
            ZIP을 다운로드 → 코드 수정 → 다시 업로드하면 수정된 모델로 학습됩니다.
          </p>
        </div>
      )}

      {/* 트랙 B: 사전학습 모델 목록 */}
      {activeTrack === "pretrained" && (
        <div className="space-y-3 mb-6">
          <p className="text-xs font-medium mb-4" style={{ color: "#64748b" }}>
            모델을 다운로드한 후 선택하세요
          </p>
          {models.map((m) => (
            <PretrainedCard key={m.id} m={m}
              selected={activeModelId === m.id}
              onSelect={() => pretrainedMut.mutate(m.id)}
            />
          ))}
        </div>
      )}

      {/* 다음 버튼 */}
      <div className="flex justify-end">
        <button onClick={() => navigate("/")} disabled={!canProceed}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={{
            background: canProceed ? "linear-gradient(135deg,#7c3aed,#4f46e5)" : "rgba(255,255,255,0.05)",
            color: canProceed ? "white" : "#475569",
            cursor: canProceed ? "pointer" : "not-allowed",
            boxShadow: canProceed ? "0 0 20px rgba(124,58,237,0.25)" : "none",
          }}>
          데이터 선택으로
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
