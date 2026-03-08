import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { queryRAG, submitFeedback } from "../api";
import type { QueryResponse } from "../api";
import { Send, ThumbsUp, ThumbsDown, Loader2, FileText, Bot, User } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  qa_id?: string;
  rated?: 1 | -1;
}

const DEMO_MESSAGES: Message[] = [
  {
    role: "user",
    content: "연차 사용 규정이 어떻게 되나요?",
  },
  {
    role: "assistant",
    content: "근로기준법 제60조에 따르면, 1년간 80% 이상 출근한 근로자에게는 15일의 유급휴가가 부여됩니다.

사내 취업규칙 제23조 기준:
• 연차 사용은 최소 1일 전 팀장 결재 필요
• 반차 사용 가능 (오전·오후 각 4시간)
• 미사용 연차는 다음 해 3월 말까지 이월 가능
• 3년 이상 근속자는 2년마다 1일 추가 (최대 25일)

연차 신청은 그룹웨어 → 전자결재 → 휴가신청 메뉴에서 진행하시면 됩니다.",
    sources: ["취업규칙_2024.pdf", "근로기준법.pdf"],
    qa_id: "demo-1",
  },
];

export default function QAPage() {
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const queryMut = useMutation({
    mutationFn: ({ question }: { question: string }) => queryRAG(question),
    onSuccess: (data: QueryResponse) => {
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer, sources: data.sources, qa_id: data.qa_id }]);
    },
  });

  const feedbackMut = useMutation({
    mutationFn: ({ qa_id, rating }: { qa_id: string; rating: 1 | -1 }) => submitFeedback(qa_id, rating),
    onSuccess: (_, { qa_id, rating }) => {
      setMessages((prev) => prev.map((m) => (m.qa_id === qa_id ? { ...m, rated: rating } : m)));
    },
  });

  const send = () => {
    const q = input.trim();
    if (!q || queryMut.isPending) return;
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setInput("");
    queryMut.mutate({ question: q });
  };

  return (
    <div className="flex flex-col h-screen">
      {/* 헤더 */}
      <div className="px-8 pt-10 pb-6 shrink-0" style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>STEP 05</span>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight text-white">Q&A</h1>
      </div>

      {/* 메시지 */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: "#1e293b" }}>
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: "rgba(59,130,246,0.08)", border: "1px solid rgba(59,130,246,0.1)" }}>
              <Bot className="w-6 h-6" style={{ color: "#1d4ed8" }} />
            </div>
            <p className="text-sm font-medium text-slate-600 mb-1">HR AI에게 질문하세요</p>
            <p className="text-xs text-slate-700">예: "연차 사용 규정이 어떻게 되나요?"</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
            {/* 아바타 */}
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
              m.role === "user" ? "" : ""
            }`} style={{
              background: m.role === "user" ? "linear-gradient(135deg,#3b82f6,#6366f1)" : "rgba(255,255,255,0.04)",
              border: m.role === "assistant" ? "1px solid rgba(255,255,255,0.06)" : "none",
            }}>
              {m.role === "user"
                ? <User className="w-3.5 h-3.5 text-white" />
                : <Bot className="w-3.5 h-3.5" style={{ color: "#60a5fa" }} />
              }
            </div>

            <div className={`max-w-[75%] ${m.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1.5`}>
              <div className="px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-wrap"
                style={m.role === "user"
                  ? { background: "linear-gradient(135deg,#1d4ed8,#4338ca)", color: "white" }
                  : { background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", color: "#cbd5e1" }
                }>
                {m.content}
              </div>

              {/* 출처 */}
              {m.sources && m.sources.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {m.sources.map((s, j) => (
                    <span key={j} className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full"
                      style={{ background: "rgba(255,255,255,0.03)", color: "#334155", border: "1px solid rgba(255,255,255,0.05)" }}>
                      <FileText className="w-2.5 h-2.5" />
                      {s}
                    </span>
                  ))}
                </div>
              )}

              {/* 피드백 */}
              {m.role === "assistant" && m.qa_id && (
                <div className="flex gap-1">
                  {([1, -1] as const).map((rating) => (
                    <button key={rating}
                      onClick={() => feedbackMut.mutate({ qa_id: m.qa_id!, rating })}
                      className="flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg transition-all"
                      style={m.rated === rating
                        ? rating === 1
                          ? { background: "rgba(16,185,129,0.12)", color: "#34d399", border: "1px solid rgba(16,185,129,0.2)" }
                          : { background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }
                        : { background: "rgba(255,255,255,0.02)", color: "#334155", border: "1px solid rgba(255,255,255,0.04)" }
                      }>
                      {rating === 1 ? <ThumbsUp className="w-3 h-3" /> : <ThumbsDown className="w-3 h-3" />}
                      {rating === 1 ? "도움됨" : "아쉬움"}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {queryMut.isPending && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}>
              <Bot className="w-3.5 h-3.5" style={{ color: "#60a5fa" }} />
            </div>
            <div className="px-4 py-3 rounded-xl flex items-center gap-2"
              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
              <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: "#60a5fa" }} />
              <span className="text-sm" style={{ color: "#334155" }}>답변 생성 중...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 입력창 */}
      <div className="px-8 py-5 shrink-0" style={{ borderTop: "1px solid rgba(255,255,255,0.04)" }}>
        <div className="flex gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            placeholder="질문을 입력하세요..."
            className="flex-1 text-sm px-4 py-3 rounded-xl outline-none transition-all"
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              color: "#e2e8f0",
            }} />
          <button onClick={send} disabled={!input.trim() || queryMut.isPending}
            className="w-11 h-11 rounded-xl flex items-center justify-center transition-all"
            style={{
              background: input.trim() ? "linear-gradient(135deg,#3b82f6,#6366f1)" : "rgba(255,255,255,0.04)",
              color: input.trim() ? "white" : "#334155",
            }}>
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
