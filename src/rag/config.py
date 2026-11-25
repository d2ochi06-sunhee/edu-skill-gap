"""RAG 설정. 비밀값(API 키)은 .env 에서만 읽습니다."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

RAG_DIR = ROOT / "data" / "rag"
CHROMA_DIR = RAG_DIR / "chroma"
MANIFEST_PATH = RAG_DIR / "manifest.json"
URL_LIST_PATH = RAG_DIR / "urls.txt"      # 한 줄에 URL 하나 (# 주석 허용)
EXTRA_DOC_DIR = RAG_DIR / "docs"          # 사용자가 직접 넣는 PDF/CSV/MD 폴더
DASHBOARD_DIR = ROOT / "dashboard"
LITE_DIR = RAG_DIR / "lite"               # 경량 모드 색인(청크 JSONL + 매니페스트). 임베딩·벡터DB 없음
LITE_CHUNKS_PATH = LITE_DIR / "chunks.jsonl"
LITE_MANIFEST_PATH = LITE_DIR / "manifest.json"
COLLECTION = "hr_edu_docs"

GITHUB_BLOB = "https://github.com/kimsaemi/edu-skill-gap/blob/main/"

# 인덱싱 대상 로컬 문서 (프로젝트 루트 기준)
DEFAULT_LOCAL_DOCS = [
    "NCS_Demand_Analysis_Report.pdf",
    "README.md",
    "CRAWLING_AND_PREPROCESSING_REPORT.md",
    "JOB_ANALYSIS_FRAMEWORK_AND_PROMPT.md",
    "docs/EDUCATION_DATA_PIPELINE.md",
    "docs/EMBEDDING_AND_CLUSTERING_ROADMAP.md",
    "docs/STEP5_2_EMBEDDING_ROADMAP.md",
    "data/sample/ncs_curriculums.csv",
    "data/sample/kmooc_courses.csv",
    "data/sample/occupation_labor_shortage.csv",
    "data/sample/remote_learning_stats.csv",
]

SUPPORTED_EXT = {".pdf", ".md", ".txt", ".csv", ".html", ".htm"}

NOT_FOUND_MESSAGE = "제공된 자료에서 답을 찾지 못했습니다."


@dataclass(frozen=True)
class RagSettings:
    # auto: fastembed(ONNX) → sentence-transformers → hash(모델 없는 어휘 임베딩, 최후 대체)
    embed_backend: str = os.getenv("RAG_EMBED_BACKEND", "auto")
    embed_model: str = os.getenv("RAG_EMBED_MODEL", "intfloat/multilingual-e5-large")
    llm_model: str = os.getenv("RAG_LLM_MODEL", "claude-sonnet-5-5")
    # 과부하(429/5xx/529)·연결 오류 시 앞에서부터 차례로 시도하는 모델 체인
    llm_chain: str = os.getenv("RAG_LLM_CHAIN", "claude-sonnet-5-5,claude-haiku-5-5")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "600"))       # 글자 수
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))
    default_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    # lite: BM25 키워드 검색만(임베딩 모델·chromadb 불필요, 배포용) / full: 벡터+BM25 하이브리드
    rag_mode: str = os.getenv("RAG_MODE", "lite")
    lite_threshold: float = float(os.getenv("RAG_LITE_THRESHOLD", "10"))
    # 비워 두면 임베딩 백엔드별 기본값 사용
    threshold_override: str = os.getenv("RAG_THRESHOLD", "")


def llm_models(settings: "RagSettings") -> list[str]:
    models = [settings.llm_model] + [m.strip() for m in settings.llm_chain.split(",") if m.strip()]
    return list(dict.fromkeys(models))


def get_settings() -> RagSettings:
    return RagSettings()


def get_anthropic_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return key or None
