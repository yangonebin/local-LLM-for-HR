import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchRLHFStats, triggerRLHF } from "../api";
import type { RLHFStats } from "../api";
import { ThumbsUp, ThumbsDown, Zap, Loader2 } from "lucide-react";

export default function RLHFPage() {
  const { data: stats, isLoading, refetch } = useQuery<RLHFStats>({
    queryKey: ["rlhf-stats"],
    queryFn: fetchRLHFStats,
    refetchInterval: 10000,
  });

  const trainMut = useMutation({
    mutationFn: triggerRLHF,
    onSuccess: () => refetch(),
  });

  const positiveRate = stats && stats.total_feedback > 0
    ? Math.round((stats.positive / stats.total_feedback) * 100) : 0;

  const needMore = 10 - (stats?.positive ?? 0);

  return (
    <div className="max-w-3xl mx-auto px-8 py-10">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: "rgba(139,92,246,0.12)", color: "#a78bfa", border: "1px solid rgba(139,92,246,0.2)" }}>STEP 06</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">RLHF 피드백 학습</h1>
        <p style={{ color: "#64748b" }} className="text-sm">Q&A에서 수집된 피드백으로 모델을 지속적으로 개선합니다.</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="w-5 h-5 rounded-full border-2 border-purple-500 border-t-transparent animate-spin" />
        </div>
      ) : (
        <>
          {/* 통계 */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              { label: "총 피드백", value: stats?.total_feedback ?? 0, color: "#64748b", bg: "rgba(255,255,255,0.02)", border: "rgba(255,255,255,0.05)" },
              { label: "긍정 피드백", value: stats?.positive ?? 0, icon: <ThumbsUp className="w-3.5 h-3.5" />, color: "#34d399", bg: "rgba(16,185,129,0.06)", border: "rgba(16,185,129,0.12)" },
              { label: "부정 피드백", value: stats?.negative ?? 0, icon: <ThumbsDown className="w-3.5 h-3.5" />, color: "#f87171", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.12)" },
            ].map(({ label, value, icon, color, bg, border }) => (
              <div key={label} className="p-4 rounded-xl"
                style={{ background: bg, border: `1px solid ${border}` }}>
                <div className="flex items-center gap-1.5 mb-3" style={{ color }}>
                  {icon}
                  <span className="text-xs font-medium">{label}</span>
                </div>
                <p className="text-2xl font-semibold text-white">{value.toLocaleString()}</p>
              </div>
            ))}
          </div>

          {/* 만족도 바 */}
          {stats && stats.total_feedback > 0 && (
            <div className="p-5 rounded-xl mb-6"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="flex justify-between text-xs mb-2.5">
                <span style={{ color: "#475569" }}>답변 만족도</span>
                <span className="font-semibold text-white">{positiveRate}%</span>
              </div>
              <div className="w-full rounded-full h-1.5" style={{ background: "rgba(255,255,255,0.05)" }}>
                <div className="h-1.5 rounded-full transition-all duration-700"
                  style={{
                    width: `${positiveRate}%`,
                    background: positiveRate >= 70
                      ? "linear-gradient(90deg,#10b981,#34d399)"
                      : positiveRate >= 40
                      ? "linear-gradient(90deg,#f59e0b,#fbbf24)"
                      : "linear-gradient(90deg,#ef4444,#f87171)",
                  }} />
              </div>
            </div>
          )}

          {/* 마지막 학습 */}
          {stats?.last_rlhf_at && (
            <p className="text-xs mb-6" style={{ color: "#334155" }}>
              마지막 RLHF 학습: {new Date(stats.last_rlhf_at).toLocaleString("ko-KR")}
            </p>
          )}

          {/* 재학습 버튼 */}
          <button onClick={() => trainMut.mutate()}
            disabled={trainMut.isPending || (stats?.positive ?? 0) < 10}
            className="w-full flex items-center justify-center gap-2.5 py-3.5 rounded-xl text-sm font-semibold transition-all"
            style={(stats?.positive ?? 0) >= 10 ? {
              background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
              color: "white",
              boxShadow: "0 0 24px rgba(124,58,237,0.2)",
            } : {
              background: "rgba(255,255,255,0.03)",
              color: "#334155",
              border: "1px solid rgba(255,255,255,0.05)",
              cursor: "not-allowed",
            }}>
            {trainMut.isPending
              ? <><Loader2 className="w-4 h-4 animate-spin" /> RLHF 학습 중...</>
              : <><Zap className="w-4 h-4" /> RLHF 재학습 시작</>
            }
          </button>

          {needMore > 0 && (
            <p className="text-center text-xs mt-3" style={{ color: "#334155" }}>
              긍정 피드백이 {needMore}개 더 필요합니다
            </p>
          )}

          {trainMut.isSuccess && (
            <div className="mt-4 p-3.5 rounded-xl text-xs text-center"
              style={{ background: "rgba(16,185,129,0.08)", color: "#34d399", border: "1px solid rgba(16,185,129,0.15)" }}>
              RLHF 학습이 백그라운드에서 시작되었습니다
            </div>
          )}
        </>
      )}
    </div>
  );
}
