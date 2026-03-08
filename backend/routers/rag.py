import uuid
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import chromadb
from chromadb.config import Settings
import PyPDF2

from db.database import get_db, Document
from schemas import DocumentInfo, QueryRequest, QueryResponse

router = APIRouter(prefix="/api/rag", tags=["rag"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

chroma_client = chromadb.PersistentClient(
    path="/app/chroma_db",
    settings=Settings(anonymized_telemetry=False),
)
collection = chroma_client.get_or_create_collection(
    name="company_docs",
    metadata={"hnsw:space": "cosine"},
)

CHUNK_SIZE = 500  # 글자 수


def extract_text(file_path: str, filename: str) -> str:
    if filename.endswith(".pdf"):
        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def split_chunks(text: str, size: int = CHUNK_SIZE) -> list[str]:
    return [text[i: i + size] for i in range(0, len(text), size) if text[i: i + size].strip()]


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    text = extract_text(save_path, file.filename)
    chunks = split_chunks(text)

    if chunks:
        collection.add(
            documents=chunks,
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
            metadatas=[{"doc_id": doc_id, "filename": file.filename, "chunk": i}
                       for i in range(len(chunks))],
        )

    doc = Document(
        id=doc_id,
        filename=file.filename,
        size_bytes=len(content),
        chunk_count=len(chunks),
        uploaded_at=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()

    return DocumentInfo(
        id=doc_id,
        filename=file.filename,
        uploaded_at=doc.uploaded_at,
        chunk_count=len(chunks),
        size_bytes=len(content),
    )


@router.get("/documents", response_model=list[DocumentInfo])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [DocumentInfo(
        id=d.id, filename=d.filename, uploaded_at=d.uploaded_at,
        chunk_count=d.chunk_count, size_bytes=d.size_bytes,
    ) for d in docs]


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    # ChromaDB에서 해당 문서 청크 삭제
    results = collection.get(where={"doc_id": doc_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])

    db.delete(doc)
    db.commit()
    return {"message": "삭제 완료"}


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, db: Session = Depends(get_db)):
    import sys
    sys.path.insert(0, "/app/llm")

    results = collection.query(
        query_texts=[req.question],
        n_results=min(req.top_k, collection.count() or 1),
    )

    contexts = results["documents"][0] if results["documents"] else []
    sources = []
    if results["metadatas"] and results["metadatas"][0]:
        sources = list({m["filename"] for m in results["metadatas"][0]})

    # 학습된 모델로 답변 생성
    answer = _generate_answer(req.question, contexts)

    # QA 기록 저장
    import json
    from db.database import QAPair
    qa = QAPair(
        question=req.question,
        answer=answer,
        sources=json.dumps(sources, ensure_ascii=False),
    )
    db.add(qa)
    db.commit()

    return QueryResponse(answer=answer, sources=sources, qa_id=qa.id)


def _generate_answer(question: str, contexts: list[str]) -> str:
    """학습된 LLM + RAG 컨텍스트로 답변 생성"""
    import os
    import glob
    import torch

    checkpoints = sorted(glob.glob("/app/llm/checkpoints/epoch_*.pt"))
    if not checkpoints:
        context_text = "\n".join(contexts[:2])
        return f"[모델 미학습] 관련 문서:\n{context_text}"

    try:
        sys_path_inserted = False
        import sys
        if "/app/llm" not in sys.path:
            sys.path.insert(0, "/app/llm")
            sys_path_inserted = True

        from config import GPTConfig
        from model.gpt import GPT
        from tokenizer.bpe import KoreanTokenizer

        cfg = GPTConfig()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = GPT(cfg).to(device)

        ckpt = torch.load(checkpoints[-1], map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()

        tokenizer = KoreanTokenizer()
        tokenizer.load("/app/llm/tokenizer/saved/spm.model")

        context_text = "\n".join(contexts)
        prompt = f"[문서]\n{context_text[:800]}\n\n[질문]\n{question}\n\n[답변]\n"

        input_ids = tokenizer.encode(prompt)
        input_tensor = torch.tensor([input_ids[-512:]], dtype=torch.long).to(device)

        with torch.no_grad():
            for _ in range(200):
                logits, _ = model(input_tensor)
                next_token = logits[0, -1, :].argmax().item()
                if next_token == tokenizer.eos_id():
                    break
                input_tensor = torch.cat(
                    [input_tensor, torch.tensor([[next_token]]).to(device)], dim=1
                )

        generated = input_tensor[0, len(input_ids):].tolist()
        return tokenizer.decode(generated)

    except Exception as e:
        context_text = "\n".join(contexts[:2])
        return f"답변 생성 오류: {e}\n\n관련 문서:\n{context_text}"
