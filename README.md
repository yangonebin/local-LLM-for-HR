<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>양한빈 포트폴리오 - HR AI 플랫폼</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Noto Sans KR', sans-serif;
  background: #0a0e1a;
  -webkit-font-smoothing: antialiased;
}

.page {
  width: 210mm;
  height: 297mm;
  margin: 0 auto 2px;
  background: #080c14;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ── 공통 요소 ── */
.mono { font-family: 'JetBrains Mono', monospace; }

.label {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9.5px;
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 3px 10px;
  border-radius: 100px;
  margin-bottom: 18px;
}
.label-blue   { color: #60a5fa; background: rgba(59,130,246,0.1);  border: 1px solid rgba(59,130,246,0.2); }
.label-purple { color: #a78bfa; background: rgba(139,92,246,0.1);  border: 1px solid rgba(139,92,246,0.2); }
.label-green  { color: #34d399; background: rgba(16,185,129,0.1);  border: 1px solid rgba(16,185,129,0.2); }

.page-title {
  font-size: 26px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.8px;
  line-height: 1.2;
  margin-bottom: 6px;
}

.page-desc {
  font-size: 12px;
  color: #475569;
  line-height: 1.8;
  margin-bottom: 28px;
}

.inner { padding: 44px 52px; flex: 1; }

.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #334155;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255,255,255,0.04);
}

.card {
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 10px;
}

.card-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 7px;
}

.card-body {
  font-size: 11.5px;
  color: #64748b;
  line-height: 1.8;
}

.tag {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  padding: 3px 9px;
  border-radius: 100px;
  margin: 2px;
}
.tag-blue   { color: #60a5fa; background: rgba(59,130,246,0.1);  border: 1px solid rgba(59,130,246,0.15); }
.tag-purple { color: #a78bfa; background: rgba(139,92,246,0.1);  border: 1px solid rgba(139,92,246,0.15); }
.tag-green  { color: #34d399; background: rgba(16,185,129,0.1);  border: 1px solid rgba(16,185,129,0.15); }
.tag-gray   { color: #64748b; background: rgba(100,116,139,0.08); border: 1px solid rgba(100,116,139,0.12); }

/* 스크린샷 placeholder */
.screenshot {
  background: rgba(255,255,255,0.02);
  border: 1.5px dashed rgba(255,255,255,0.1);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #2d3748;
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
  overflow: hidden;
}
.screenshot-label {
  position: absolute;
  top: 8px;
  left: 10px;
  font-size: 9px;
  color: #1e293b;
  font-family: 'JetBrains Mono', monospace;
}
/* 실제 이미지로 교체 시: <img> 태그로 대체하세요 */

/* 상단 바 */
.top-bar {
  height: 40px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 52px;
  flex-shrink: 0;
}
.top-bar-left {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: #1e293b;
  letter-spacing: 1px;
}
.top-bar-right {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: #1e293b;
}

/* 하단 바 */
.bottom-bar {
  height: 36px;
  border-top: 1px solid rgba(255,255,255,0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 52px;
  flex-shrink: 0;
}
.bottom-bar-name {
  font-size: 10px;
  color: #1e293b;
  font-weight: 500;
}
.bottom-bar-page {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: #1e293b;
}

/* ══════════════════════════════════════
   1페이지: 커버
══════════════════════════════════════ */
.cover { background: #080c14; }

.cover-bg {
  position: absolute;
  top: -120px; right: -120px;
  width: 480px; height: 480px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%);
  pointer-events: none;
}

.cover-inner {
  padding: 52px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.cover-top { flex: 1; }

.cover-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #475569;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 100px;
  padding: 5px 14px;
  margin-bottom: 36px;
}

.cover-title {
  font-size: 48px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -2px;
  line-height: 1.1;
  margin-bottom: 14px;
}

.cover-title .grad {
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cover-sub {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
  max-width: 320px;
  margin-bottom: 52px;
}

.cover-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 44px;
}

.cover-stat {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 20px;
}

.cover-stat-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 30px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.cover-stat-label { font-size: 10.5px; color: #334155; }

.cover-bottom {
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.cover-name {
  font-size: 20px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 6px;
}

.cover-contact {
  font-size: 11px;
  color: #334155;
  line-height: 2;
}

.cover-year {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #1e293b;
  text-align: right;
}

/* ══ 인쇄 ══ */
@media print {
  body { background: #080c14; }
  .page { margin: 0; page-break-after: always; width: 210mm; height: 297mm; }
  @page { margin: 0; size: A4; }
}
</style>
</head>
<body>

<!-- ═══════════════════════════════
     PAGE 1 · COVER
═══════════════════════════════ -->
<div class="page cover">
  <div class="cover-bg"></div>
  <div class="cover-inner">
    <div class="cover-top">
      <div class="cover-tag">
        <span style="width:6px;height:6px;border-radius:50%;background:#334155;"></span>
        PERSONAL PROJECT · 2025
      </div>

      <div class="cover-title">
        로컬 HR AI<br><span class="grad">LLM 플랫폼</span>
      </div>

      <div class="cover-sub">
        외부 서버 전송 없이, 클릭 한 번으로<br>기업 전용 AI를 구축하는 완전 로컬 서비스
      </div>
    </div>

    <div class="cover-stats">
      <div class="cover-stat">
        <div class="cover-stat-val">6</div>
        <div class="cover-stat-label">단계 워크플로우</div>
      </div>
      <div class="cover-stat">
        <div class="cover-stat-val">100%</div>
        <div class="cover-stat-label">완전 로컬 실행</div>
      </div>
      <div class="cover-stat">
        <div class="cover-stat-val">13+</div>
        <div class="cover-stat-label">학습 데이터셋</div>
      </div>
    </div>

    <div class="cover-bottom">
      <div>
        <div class="cover-name">양한빈</div>
        <div class="cover-contact">
          010-3861-4897<br>
          yangonebin@gmail.com
        </div>
      </div>
      <div class="cover-year">
        개인 프로젝트<br>2025
      </div>
    </div>
  </div>
</div>


<!-- ═══════════════════════════════
     PAGE 2 · 문제 정의
═══════════════════════════════ -->
<div class="page">
  <div class="top-bar">
    <span class="top-bar-left">PROBLEM DEFINITION</span>
    <span class="top-bar-right">양한빈 · HR AI 플랫폼</span>
  </div>

  <div class="inner">
    <div class="label label-blue">01 · PROBLEM</div>
    <div class="page-title">왜 HR팀은 AI를<br>마음껏 쓰지 못할까</div>
    <div class="page-desc">
      ChatGPT 등 상용 AI가 빠르게 확산되고 있지만, 기업 HR 업무에는 여전히 보안 장벽이 존재합니다.
    </div>

    <!-- 문제 vs 해결 -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:22px;">
      <div style="background:rgba(239,68,68,0.04); border:1px solid rgba(239,68,68,0.12); border-radius:10px; padding:18px 20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:600; letter-spacing:1.5px; color:#ef4444; text-transform:uppercase; margin-bottom:12px;">현재 문제</div>
        <div style="font-size:11.5px; color:#64748b; line-height:2;">
          사내 연봉·인사 데이터 외부 서버 전송<br>
          개인정보보호법 위반 리스크<br>
          기업 기밀 유출 가능성<br>
          IT 보안 정책상 사용 금지<br>
          법무팀 컴플라이언스 우려
        </div>
      </div>
      <div style="background:rgba(16,185,129,0.04); border:1px solid rgba(16,185,129,0.12); border-radius:10px; padding:18px 20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:600; letter-spacing:1.5px; color:#34d399; text-transform:uppercase; margin-bottom:12px;">본 프로젝트 해결</div>
        <div style="font-size:11.5px; color:#64748b; line-height:2;">
          데이터 외부 전송 제로<br>
          회사 서버에서만 완전 동작<br>
          IT팀은 Docker 설치 1회만<br>
          HR팀은 웹 브라우저 클릭만으로<br>
          법적 리스크 없음
        </div>
      </div>
    </div>

    <!-- 타겟 -->
    <div class="section-label">Target User</div>
    <div class="card" style="border-left:2px solid #3b82f6; margin-bottom:16px;">
      <div class="card-title">기업 인사팀 (HR Team)</div>
      <div class="card-body">
        취업규칙, 노동법, 사내 규정에 관한 질문에 빠른 답변이 필요하지만, 보안 정책상 상용 AI 사용이
        제한된 환경. 노동법 해석, 급여 규정, 징계 절차 등 전문 HR 지식을 AI에게 질의하고 싶으나
        정보 유출 우려로 활용하지 못하고 있음.
      </div>
    </div>

    <!-- 통계 -->
    <div class="section-label">Market Insight</div>
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px;">
      <div class="card" style="text-align:center; padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:700; color:#60a5fa; margin-bottom:4px;">78%</div>
        <div style="font-size:10.5px; color:#475569; line-height:1.6;">AI 도입 시 보안을<br>최우선 고려</div>
      </div>
      <div class="card" style="text-align:center; padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:700; color:#a78bfa; margin-bottom:4px;">63%</div>
        <div style="font-size:10.5px; color:#475569; line-height:1.6;">HR 담당자 법률 질문<br>30분 이상 소요</div>
      </div>
      <div class="card" style="text-align:center; padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:700; color:#34d399; margin-bottom:4px;">41%</div>
        <div style="font-size:10.5px; color:#475569; line-height:1.6;">AI 사용 규정 부재로<br>임의 사용 중</div>
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span class="bottom-bar-name">양한빈</span>
    <span class="bottom-bar-page">02 / 06</span>
  </div>
</div>


<!-- ═══════════════════════════════
     PAGE 3 · 아키텍처
═══════════════════════════════ -->
<div class="page">
  <div class="top-bar">
    <span class="top-bar-left">SOLUTION & ARCHITECTURE</span>
    <span class="top-bar-right">양한빈 · HR AI 플랫폼</span>
  </div>

  <div class="inner">
    <div class="label label-purple">02 · ARCHITECTURE</div>
    <div class="page-title">시스템 구조</div>
    <div class="page-desc">Docker Compose로 4개 서비스가 사내망 내에서 완전 격리 실행됩니다.</div>

    <!-- 아키텍처 다이어그램 -->
    <div style="background:#060a12; border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:24px; margin-bottom:18px;">

      <div style="font-family:'JetBrains Mono',monospace; font-size:8.5px; color:#1e293b; letter-spacing:1px; text-transform:uppercase; margin-bottom:14px;">[ 사내망 · 완전 격리 환경 ]</div>

      <!-- Row 1 -->
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <div style="flex:1; background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#60a5fa; margin-bottom:3px;">브라우저</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">React + TypeScript</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.2); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#a78bfa; margin-bottom:3px;">Nginx</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">Reverse Proxy</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#34d399; margin-bottom:3px;">FastAPI</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">REST Backend</div>
        </div>
      </div>

      <!-- Row 2 -->
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#e2e8f0; margin-bottom:3px;">Redis</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">Task Queue</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#e2e8f0; margin-bottom:3px;">Celery Worker</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">비동기 학습 처리</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(251,191,36,0.06); border:1px solid rgba(251,191,36,0.15); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#fbbf24; margin-bottom:3px;">GPU Server</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">PyTorch · CUDA</div>
        </div>
      </div>

      <!-- Row 3 -->
      <div style="display:flex; align-items:center; gap:8px;">
        <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#e2e8f0; margin-bottom:3px;">ChromaDB</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">Vector DB · RAG</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#e2e8f0; margin-bottom:3px;">SQLite</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">RLHF 피드백 저장</div>
        </div>
        <div style="color:#334155; font-size:14px;">→</div>
        <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px; text-align:center;">
          <div style="font-size:11px; font-weight:600; color:#e2e8f0; margin-bottom:3px;">Docker Compose</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#334155;">전체 오케스트레이션</div>
        </div>
      </div>
    </div>

    <!-- 6단계 플로우 -->
    <div class="section-label">6-Step Workflow</div>
    <div style="display:flex; gap:0; align-items:stretch;">
      {%for step in steps%}
      </div>
      <!-- 수동 작성 -->
      <div style="display:flex; gap:6px;">
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b; margin-bottom:6px;">STEP 01</div>
          <div style="font-size:10.5px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">모델 선택</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">스크래치<br>또는 사전학습</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b; margin-bottom:6px;">STEP 02</div>
          <div style="font-size:10.5px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">데이터 선택</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">나무위키·법령<br>클릭·자동 다운로드</div>
        </div>
        <div style="flex:1; background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.15); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e4080; margin-bottom:6px;">STEP 03</div>
          <div style="font-size:10.5px; font-weight:600; color:#60a5fa; margin-bottom:4px;">LLM 학습</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">로컬 GPU<br>실시간 모니터링</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b; margin-bottom:6px;">STEP 04</div>
          <div style="font-size:10.5px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">문서 업로드</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">취업규칙·사내규정<br>RAG 적용</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b; margin-bottom:6px;">STEP 05</div>
          <div style="font-size:10.5px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">Q&A</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">사내 문서 기반<br>HR 질문 답변</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px 8px; text-align:center;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b; margin-bottom:6px;">STEP 06</div>
          <div style="font-size:10.5px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">RLHF</div>
          <div style="font-size:9.5px; color:#334155; line-height:1.5;">피드백으로<br>지속 개선</div>
        </div>
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span class="bottom-bar-name">양한빈</span>
    <span class="bottom-bar-page">03 / 06</span>
  </div>
</div>


<!-- ═══════════════════════════════
     PAGE 4 · 기술 스택
═══════════════════════════════ -->
<div class="page">
  <div class="top-bar">
    <span class="top-bar-left">TECH STACK & IMPLEMENTATION</span>
    <span class="top-bar-right">양한빈 · HR AI 플랫폼</span>
  </div>

  <div class="inner">
    <div class="label label-green">03 · TECH STACK</div>
    <div class="page-title">기술 스택</div>
    <div class="page-desc">프론트엔드부터 LLM 학습, 인프라까지 전 영역을 직접 설계·구현하였습니다.</div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px;">
      <div class="card">
        <div class="card-title">Frontend</div>
        <div style="margin-bottom:10px;">
          <span class="tag tag-blue">React 18</span>
          <span class="tag tag-blue">TypeScript</span>
          <span class="tag tag-blue">Vite</span>
          <span class="tag tag-blue">TailwindCSS</span>
          <span class="tag tag-blue">React Query</span>
          <span class="tag tag-blue">Recharts</span>
        </div>
        <div class="card-body">실시간 학습 진행률, Loss 그래프, 드래그앤드롭, 채팅 UI를 React Query 폴링으로 백엔드와 실시간 동기화</div>
      </div>
      <div class="card">
        <div class="card-title">Backend</div>
        <div style="margin-bottom:10px;">
          <span class="tag tag-purple">FastAPI</span>
          <span class="tag tag-purple">Celery</span>
          <span class="tag tag-purple">Redis</span>
          <span class="tag tag-purple">SQLAlchemy</span>
          <span class="tag tag-purple">ChromaDB</span>
          <span class="tag tag-purple">PyPDF2</span>
        </div>
        <div class="card-body">비동기 학습 태스크를 Celery+Redis로 처리. ChromaDB 벡터 DB로 RAG 파이프라인 구현</div>
      </div>
      <div class="card">
        <div class="card-title">AI / ML</div>
        <div style="margin-bottom:10px;">
          <span class="tag tag-green">PyTorch</span>
          <span class="tag tag-green">Transformers</span>
          <span class="tag tag-green">PEFT · LoRA</span>
          <span class="tag tag-green">SentencePiece</span>
          <span class="tag tag-green">HuggingFace Hub</span>
        </div>
        <div class="card-body">GPT 트랜스포머 스크래치 구현. EXAONE·Qwen3·LLaMA3를 LoRA로 파인튜닝. BPE 토크나이저 학습</div>
      </div>
      <div class="card">
        <div class="card-title">Infrastructure</div>
        <div style="margin-bottom:10px;">
          <span class="tag tag-gray">Docker</span>
          <span class="tag tag-gray">Docker Compose</span>
          <span class="tag tag-gray">Nginx</span>
          <span class="tag tag-gray">CUDA</span>
          <span class="tag tag-gray">NVIDIA Container</span>
        </div>
        <div class="card-body">4개 서비스 Docker Compose 오케스트레이션. GPU 컨테이너 CUDA 가속 지원. 단일 포트(80) 통합</div>
      </div>
    </div>

    <div class="section-label">Data Pipeline</div>
    <div class="card">
      <div class="card-body" style="display:grid; grid-template-columns:1fr 1fr; gap:8px 24px;">
        <div><span style="color:#64748b; font-weight:600;">자동 수집</span><br>나무위키·위키피디아 덤프 자동 다운로드 및 XML/JSON 파싱</div>
        <div><span style="color:#64748b; font-weight:600;">법령 API</span><br>국가법령정보센터 Open API — 노동법·판례·민법 등 13개 데이터셋</div>
        <div><span style="color:#64748b; font-weight:600;">전처리</span><br>SentencePiece BPE 토크나이저 적용 후 바이너리(.bin) 변환</div>
        <div><span style="color:#64748b; font-weight:600;">RAG 인덱싱</span><br>PDF·TXT 500자 청크 분할 → ChromaDB 코사인 유사도 임베딩</div>
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span class="bottom-bar-name">양한빈</span>
    <span class="bottom-bar-page">04 / 06</span>
  </div>
</div>


<!-- ═══════════════════════════════
     PAGE 5 · 스크린샷
═══════════════════════════════ -->
<div class="page">
  <div class="top-bar">
    <span class="top-bar-left">SCREENSHOTS</span>
    <span class="top-bar-right">양한빈 · HR AI 플랫폼</span>
  </div>

  <div class="inner" style="padding-bottom:30px;">
    <div class="label label-blue">04 · SCREENSHOTS</div>
    <div class="page-title">주요 화면</div>
    <div class="page-desc">6단계 워크플로우의 핵심 화면입니다.</div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">

      <!-- 스크린샷 1 -->
      <div>
        <div style="font-size:10px; color:#334155; margin-bottom:6px; font-family:'JetBrains Mono',monospace;">STEP 01 · 모델 선택</div>
        <!-- 스크린샷 교체 방법: 아래 div를 <img src="모델선택.png" style="width:100%;border-radius:8px;"> 로 교체 -->
        <div style="height:130px; background:rgba(255,255,255,0.02); border:1.5px dashed rgba(255,255,255,0.08); border-radius:8px; display:flex; align-items:center; justify-content:center;">
          <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b;">스크린샷 삽입</span>
        </div>
      </div>

      <!-- 스크린샷 2 -->
      <div>
        <div style="font-size:10px; color:#334155; margin-bottom:6px; font-family:'JetBrains Mono',monospace;">STEP 02 · 데이터 선택</div>
        <div style="height:130px; background:rgba(255,255,255,0.02); border:1.5px dashed rgba(255,255,255,0.08); border-radius:8px; display:flex; align-items:center; justify-content:center;">
          <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b;">스크린샷 삽입</span>
        </div>
      </div>

      <!-- 스크린샷 3 -->
      <div>
        <div style="font-size:10px; color:#334155; margin-bottom:6px; font-family:'JetBrains Mono',monospace;">STEP 03 · LLM 학습 (실시간 Loss)</div>
        <div style="height:130px; background:rgba(255,255,255,0.02); border:1.5px dashed rgba(255,255,255,0.08); border-radius:8px; display:flex; align-items:center; justify-content:center;">
          <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b;">스크린샷 삽입</span>
        </div>
      </div>

      <!-- 스크린샷 4 -->
      <div>
        <div style="font-size:10px; color:#334155; margin-bottom:6px; font-family:'JetBrains Mono',monospace;">STEP 05 · Q&A 채팅</div>
        <div style="height:130px; background:rgba(255,255,255,0.02); border:1.5px dashed rgba(255,255,255,0.08); border-radius:8px; display:flex; align-items:center; justify-content:center;">
          <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e293b;">스크린샷 삽입</span>
        </div>
      </div>
    </div>

    <!-- 스크린샷 교체 안내 -->
    <div style="margin-top:14px; padding:12px 16px; background:rgba(59,130,246,0.04); border:1px solid rgba(59,130,246,0.1); border-radius:8px;">
      <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e4080; margin-bottom:4px;">HOW TO INSERT SCREENSHOTS</div>
      <div style="font-size:10.5px; color:#334155; line-height:1.8;">
        1. 브라우저에서 각 페이지 캡처 후 PNG로 저장<br>
        2. HTML 파일에서 "스크린샷 삽입" div를 찾아<br>
        &nbsp;&nbsp;&nbsp;<code style="background:rgba(255,255,255,0.04); padding:1px 5px; border-radius:3px; font-size:9px;">&lt;img src="파일명.png" style="width:100%;border-radius:8px;"&gt;</code> 로 교체
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span class="bottom-bar-name">양한빈</span>
    <span class="bottom-bar-page">05 / 06</span>
  </div>
</div>


<!-- ═══════════════════════════════
     PAGE 6 · 역량 & 마무리
═══════════════════════════════ -->
<div class="page">
  <div class="top-bar">
    <span class="top-bar-left">KEY COMPETENCIES</span>
    <span class="top-bar-right">양한빈 · HR AI 플랫폼</span>
  </div>

  <div class="inner">
    <div class="label label-purple">05 · COMPETENCIES</div>
    <div class="page-title">이 프로젝트가<br>보여주는 역량</div>
    <div class="page-desc">단순 API 호출이 아닌, LLM 전체 생애주기를 직접 설계·구현한 경험입니다.</div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:22px;">
      <div class="card" style="border-left:2px solid #3b82f6;">
        <div class="card-title">보안 이해도</div>
        <div class="card-body">기업 데이터 보안 문제를 정확히 파악하고, 완전 로컬 아키텍처 설계로 해결. 법적 컴플라이언스까지 고려한 제품 기획.</div>
      </div>
      <div class="card" style="border-left:2px solid #8b5cf6;">
        <div class="card-title">AI 전문성</div>
        <div class="card-body">GPT 스크래치 구현 + LoRA 파인튜닝 + RAG + RLHF 전 파이프라인을 직접 구현. LLM 동작 원리에 대한 깊은 이해.</div>
      </div>
      <div class="card" style="border-left:2px solid #10b981;">
        <div class="card-title">풀스택 설계</div>
        <div class="card-body">React·FastAPI·Docker·GPU까지 전체 스택을 혼자 설계·구현. 각 기술 간 연결과 트레이드오프를 직접 결정.</div>
      </div>
      <div class="card" style="border-left:2px solid #f59e0b;">
        <div class="card-title">사용자 중심 사고</div>
        <div class="card-body">비개발자인 HR팀이 터미널 없이 클릭만으로 사용할 수 있도록 전체 UX를 설계. 기술보다 문제 해결에 집중.</div>
      </div>
    </div>

    <!-- 연락처 -->
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:24px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:10px;">양한빈</div>
        <div style="font-size:12px; color:#334155; line-height:2.2;">
          010-3861-4897<br>
          yangonebin@gmail.com
        </div>
      </div>
      <div style="text-align:right;">
      </div>
    </div>
  </div>

  <div class="bottom-bar">
    <span class="bottom-bar-name">양한빈</span>
    <span class="bottom-bar-page">06 / 06</span>
  </div>
</div>

</body>
</html>
