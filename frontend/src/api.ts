import axios from "axios";

const api = axios.create({ baseURL: "/api" });

// ── Types ──────────────────────────────────────────────────
export interface DatasetInfo {
  id: string;
  name: string;
  description: string;
  estimated_tokens: number;
  size_gb: number;
  category: string;
  available: boolean;
}

export interface TrainingConfig {
  dataset_ids: string[];
  d_model?: number;
  n_layers?: number;
  n_heads?: number;
  d_ff?: number;
  max_seq_len?: number;
  batch_size?: number;
  learning_rate?: number;
  max_epochs?: number;
  vocab_size?: number;
}

export interface TrainingEstimate {
  total_tokens: number;
  total_parameters: number;
  estimated_hours: number;
  datasets: DatasetInfo[];
}

export interface TrainingStatus {
  task_id: string | null;
  status: "idle" | "running" | "completed" | "failed" | "stopped" | "stopping";
  epoch: number;
  total_epochs: number;
  step: number;
  loss: number;
  progress: number;
  elapsed_seconds: number;
  message: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  uploaded_at: string;
  chunk_count: number;
  size_bytes: number;
}

export interface QueryResponse {
  answer: string;
  sources: string[];
  qa_id: string;
}

export interface RLHFStats {
  total_feedback: number;
  positive: number;
  negative: number;
  last_rlhf_at: string | null;
}

// ── Dataset ────────────────────────────────────────────────
export const fetchDatasets = () =>
  api.get<DatasetInfo[]>("/datasets/").then((r) => r.data);

export const estimateTraining = (config: TrainingConfig) =>
  api.post<TrainingEstimate>("/datasets/estimate", config).then((r) => r.data);

// ── Training ───────────────────────────────────────────────
export const startTraining = (config: TrainingConfig) =>
  api.post<TrainingStatus>("/training/start", config).then((r) => r.data);

export const fetchTrainingStatus = () =>
  api.get<TrainingStatus>("/training/status").then((r) => r.data);

export const stopTraining = () =>
  api.post<TrainingStatus>("/training/stop").then((r) => r.data);

// ── RAG ───────────────────────────────────────────────────
export const uploadDocument = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post<DocumentInfo>("/rag/upload", form).then((r) => r.data);
};

export const fetchDocuments = () =>
  api.get<DocumentInfo[]>("/rag/documents").then((r) => r.data);

export const deleteDocument = (id: string) =>
  api.delete(`/rag/documents/${id}`);

export const queryRAG = (question: string, top_k = 3) =>
  api.post<QueryResponse>("/rag/query", { question, top_k }).then((r) => r.data);

// ── RLHF ─────────────────────────────────────────────────
export const submitFeedback = (qa_id: string, rating: 1 | -1, comment?: string) =>
  api.post("/rlhf/feedback", { qa_id, rating, comment }).then((r) => r.data);

export const fetchRLHFStats = () =>
  api.get<RLHFStats>("/rlhf/stats").then((r) => r.data);

export const triggerRLHF = () =>
  api.post("/rlhf/train").then((r) => r.data);

// ── Dataset Download ────────────────────────────────────────
export interface DownloadStatus {
  status: "idle" | "running" | "completed" | "ready" | "failed";
  progress: number;
  message: string;
}

export const fetchDownloadStatus = (dataset_id: string) =>
  api.get<DownloadStatus>(`/datasets/${dataset_id}/status`).then((r) => r.data);

export const startDownload = (dataset_id: string, api_key?: string) =>
  api.post(`/datasets/${dataset_id}/download`, api_key ? { api_key } : {}).then((r) => r.data);

// ── Models ─────────────────────────────────────────────────
export interface PretrainedModel {
  id: string;
  name: string;
  description: string;
  hf_repo: string;
  size_gb: number;
  params: string;
  language: string;
  recommended: boolean;
  ready: boolean;
  download_status: { status: string; progress: number; message: string };
}

export interface ModelSelection {
  track: "custom" | "pretrained" | null;
  model_id: string | null;
}

export const fetchPretrainedModels = () =>
  api.get<PretrainedModel[]>("/models/pretrained").then((r) => r.data);

export const fetchSelectedModel = () =>
  api.get<ModelSelection>("/models/selected").then((r) => r.data);

export const selectCustomModel = () =>
  api.post("/models/select/custom").then((r) => r.data);

export const selectPretrainedModel = (model_id: string) =>
  api.post(`/models/select/pretrained/${model_id}`).then((r) => r.data);

export const startModelDownload = (model_id: string) =>
  api.post(`/models/download/${model_id}`).then((r) => r.data);

export const fetchModelDownloadStatus = (model_id: string) =>
  api.get<{ status: string; progress: number; message: string }>(
    `/models/download/${model_id}/status`
  ).then((r) => r.data);

export const downloadCustomModelCode = () =>
  api.get("/models/custom/download", { responseType: "blob" }).then((r) => {
    const url = URL.createObjectURL(r.data);
    const a = document.createElement("a");
    a.href = url; a.download = "hr_llm_model.zip"; a.click();
    URL.revokeObjectURL(url);
  });

export const uploadCustomModelCode = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/models/custom/upload", form).then((r) => r.data);
};
