import { useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadDocument, fetchDocuments, deleteDocument } from "../api";
import type { DocumentInfo } from "../api";
import { Upload, FileText, Trash2, Loader2 } from "lucide-react";

function fmtSize(bytes: number) {
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024).toFixed(0)} KB`;
}

export default function RAGPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const { data: documents = [], isLoading } = useQuery({ queryKey: ["documents"], queryFn: fetchDocuments });

  const uploadMut = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });

  const deleteMut = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach((f) => uploadMut.mutate(f));
  };

  return (
    <div className="max-w-4xl mx-auto px-8 py-10">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: "rgba(59,130,246,0.12)", color: "#60a5fa", border: "1px solid rgba(59,130,246,0.2)" }}>STEP 04</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">사내 문서 업로드</h1>
        <p style={{ color: "#64748b" }} className="text-sm">취업규칙, 사내 규정, 급여 정책 등을 업로드하면 LLM이 이를 참고해 답변합니다.</p>
      </div>

      {/* 업로드 존 */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => fileRef.current?.click()}
        className="rounded-xl p-12 text-center cursor-pointer transition-all duration-200 mb-8"
        style={{
          background: dragging ? "rgba(59,130,246,0.06)" : "rgba(255,255,255,0.01)",
          border: `2px dashed ${dragging ? "rgba(59,130,246,0.4)" : "rgba(255,255,255,0.06)"}`,
        }}
      >
        <div className="w-12 h-12 rounded-xl mx-auto mb-4 flex items-center justify-center"
          style={{ background: dragging ? "rgba(59,130,246,0.15)" : "rgba(255,255,255,0.04)" }}>
          <Upload className="w-5 h-5" style={{ color: dragging ? "#60a5fa" : "#334155" }} />
        </div>
        <p className="text-sm font-medium text-white mb-1">
          {dragging ? "여기에 놓으세요" : "파일을 드래그하거나 클릭해서 업로드"}
        </p>
        <p className="text-xs" style={{ color: "#334155" }}>PDF · TXT · DOCX 지원</p>
        <input ref={fileRef} type="file" multiple accept=".pdf,.txt,.docx" className="hidden"
          onChange={(e) => handleFiles(e.target.files)} />
      </div>

      {/* 업로드 중 */}
      {uploadMut.isPending && (
        <div className="flex items-center gap-3 p-4 rounded-xl mb-4"
          style={{ background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.15)" }}>
          <Loader2 className="w-4 h-4 animate-spin" style={{ color: "#60a5fa" }} />
          <span className="text-sm" style={{ color: "#60a5fa" }}>문서를 처리하고 있습니다...</span>
        </div>
      )}

      {/* 문서 목록 */}
      <div className="flex items-center gap-2 mb-4">
        <p className="text-xs font-medium" style={{ color: "#475569" }}>업로드된 문서</p>
        <span className="text-xs px-1.5 py-0.5 rounded font-mono" style={{ background: "rgba(255,255,255,0.05)", color: "#475569" }}>{documents.length}</span>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12" style={{ color: "#334155" }}>
          <FileText className="w-8 h-8 mx-auto mb-2 opacity-30" />
          <p className="text-sm">업로드된 문서가 없습니다</p>
        </div>
      ) : (
        <div className="space-y-2">
          {documents.map((doc: DocumentInfo) => (
            <div key={doc.id} className="flex items-center justify-between p-4 rounded-xl group"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)" }}>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  style={{ background: "rgba(59,130,246,0.1)" }}>
                  <FileText className="w-4 h-4" style={{ color: "#60a5fa" }} />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{doc.filename}</p>
                  <p className="text-xs" style={{ color: "#334155" }}>
                    {fmtSize(doc.size_bytes)} · {doc.chunk_count}개 청크 · {new Date(doc.uploaded_at).toLocaleDateString("ko-KR")}
                  </p>
                </div>
              </div>
              <button onClick={() => deleteMut.mutate(doc.id)}
                className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                style={{ color: "#ef4444" }}>
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
