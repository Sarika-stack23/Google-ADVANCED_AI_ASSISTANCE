"""
Knowledge Base Indexing Pipeline — Data loading, preprocessing, and chunking.

Extracted from main.py L80-L270. Contains:
- MathDataLoader: loads NCERT knowledge base from knowledge_base.py
- MathDataPreprocessor: cleans, deduplicates, detects topics
- MathTextSplitter: splits documents into chunks for vector indexing
"""

import re
import hashlib
import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger("math_assistant.indexer")

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        class Document:
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}


class MathDataLoader:
    """Load NCERT math knowledge base from hardcoded knowledge_base.py."""

    def load_builtin_knowledge(self) -> List[Document]:
        """Load the hand-curated NCERT knowledge base.

        Returns:
            List of Document objects with topic metadata.
        """
        # Import from the project root knowledge_base.py
        import sys
        project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from knowledge_base import MATH_KNOWLEDGE_BASE, CLASS_EXAMPLES
        documents = []

        # Process topic documents
        for topic, sections in MATH_KNOWLEDGE_BASE.items():
            if isinstance(sections, dict):
                for sub_topic, content in sections.items():
                    if isinstance(content, str) and len(content.strip()) > 50:
                        documents.append(Document(
                            page_content=content,
                            metadata={"source": "builtin_kb", "topic": topic,
                                      "sub_topic": sub_topic}
                        ))
                    elif isinstance(content, dict):
                        for k, v in content.items():
                            if isinstance(v, str) and len(v.strip()) > 50:
                                documents.append(Document(
                                    page_content=v,
                                    metadata={"source": "builtin_kb", "topic": topic,
                                              "sub_topic": f"{sub_topic}/{k}"}
                                ))
            elif isinstance(sections, str) and len(sections.strip()) > 50:
                documents.append(Document(
                    page_content=sections,
                    metadata={"source": "builtin_kb", "topic": topic}
                ))

        # Process class examples
        for class_id, chapters in CLASS_EXAMPLES.items():
            if isinstance(chapters, dict):
                for chapter, questions in chapters.items():
                    if isinstance(questions, list):
                        for q in questions:
                            if isinstance(q, dict):
                                text = q.get("question", "") + "\n" + q.get("solution", "")
                                if len(text.strip()) > 50:
                                    documents.append(Document(
                                        page_content=text,
                                        metadata={"source": "ncert_examples",
                                                  "class": class_id,
                                                  "chapter": chapter,
                                                  "topic": q.get("topic", "general_math")}
                                    ))
                    elif isinstance(questions, str) and len(questions.strip()) > 50:
                        documents.append(Document(
                            page_content=questions,
                            metadata={"source": "ncert_examples",
                                      "class": class_id, "chapter": chapter}
                        ))

        logger.info(f"Loaded {len(documents)} documents from built-in knowledge base")
        return documents

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Load a single PDF file."""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            docs = PyPDFLoader(pdf_path).load()
            logger.info(f"Loaded {len(docs)} pages from: {pdf_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path}: {e}")
            return []

    def load_pdfs_from_directory(self, dir_path: str) -> List[Document]:
        """Load all PDFs from a directory."""
        try:
            from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
            docs = DirectoryLoader(dir_path, glob="**/*.pdf", loader_cls=PyPDFLoader).load()
            logger.info(f"Loaded {len(docs)} documents from: {dir_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDFs from {dir_path}: {e}")
            return []

    def load_web_pages(self, urls: List[str]) -> List[Document]:
        """Load content from web URLs."""
        from langchain_community.document_loaders import WebBaseLoader
        docs = []
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                loader.requests_kwargs = {"timeout": 15}
                docs.extend(loader.load())
                logger.info(f"Loaded: {url}")
            except Exception as e:
                logger.warning(f"Failed URL {url}: {e}")
        return docs

    def load_text_file(self, file_path: str) -> List[Document]:
        """Load a text or markdown file."""
        try:
            if file_path.endswith(".md"):
                from langchain_community.document_loaders import UnstructuredMarkdownLoader
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            logger.info(f"Loaded: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []

    def load_all(self, pdf_paths=None, urls=None, text_paths=None, pdf_directory=None) -> List[Document]:
        """Load all data sources: builtin KB + PDFs + URLs + text files."""
        import os
        all_docs = self.load_builtin_knowledge()
        if pdf_paths:
            for p in pdf_paths:
                all_docs.extend(self.load_pdf(p))
        if pdf_directory and os.path.exists(pdf_directory):
            all_docs.extend(self.load_pdfs_from_directory(pdf_directory))
        if urls:
            all_docs.extend(self.load_web_pages(urls))
        if text_paths:
            for p in text_paths:
                all_docs.extend(self.load_text_file(p))
        logger.info(f"Total documents loaded: {len(all_docs)}")
        return all_docs


class MathDataPreprocessor:
    """Clean, deduplicate, and enrich math documents with metadata."""

    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "calculus":       ["derivative", "integral", "differentiate", "integrate", "limit", "continuity", "taylor"],
        "linear_algebra": ["matrix", "vector", "eigenvalue", "determinant", "rank", "span", "basis"],
        "statistics":     ["probability", "distribution", "mean", "variance", "regression", "hypothesis"],
        "algebra":        ["polynomial", "equation", "quadratic", "factor", "root", "logarithm", "exponent"],
        "trigonometry":   ["sine", "cosine", "tangent", "angle", "radian", "unit circle", "trig"],
        "discrete_math":  ["graph", "combinatorics", "permutation", "combination", "modular", "prime"],
        "geometry":       ["triangle", "circle", "area", "volume", "perimeter", "pythagorean", "coordinate"],
        "number_theory":  ["prime", "divisor", "gcd", "lcm", "modular", "congruence", "integer"],
    }

    def __init__(self):
        self._seen_hashes: set = set()

    def _clean(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"https?://\S+", "[URL]", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        replacements = {
            "\u2019": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "--", "\u00a0": " ",
            "\u03c0": "pi", "\u221e": "infinity",
            "\u2264": "<=", "\u2265": ">="
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.strip()

    def _detect_topic(self, text: str) -> str:
        tl = text.lower()
        scores = {t: sum(1 for kw in kws if kw in tl) for t, kws in self.TOPIC_KEYWORDS.items()}
        scores = {k: v for k, v in scores.items() if v > 0}
        return max(scores, key=scores.get) if scores else "general_math"

    def _difficulty(self, text: str) -> str:
        adv = ["eigenvalue", "differential equation", "fourier", "laplace", "manifold", "tensor"]
        mid = ["derivative", "integral", "matrix", "probability", "polynomial", "logarithm"]
        tl = text.lower()
        if sum(1 for t in adv if t in tl) >= 2: return "advanced"
        if sum(1 for t in mid if t in tl) >= 2: return "intermediate"
        return "beginner"

    def preprocess_document(self, doc):
        text = doc.page_content
        if len(text.strip()) < 50:
            return None
        text = self._clean(text)
        h = hashlib.md5(text.strip().lower().encode()).hexdigest()
        if h in self._seen_hashes:
            return None
        self._seen_hashes.add(h)
        meta = doc.metadata.copy()
        meta.update({
            "topic":        meta.get("topic") or self._detect_topic(text),
            "difficulty":   self._difficulty(text),
            "char_count":   len(text),
            "word_count":   len(text.split()),
            "content_hash": h,
        })
        return Document(page_content=text, metadata=meta)

    def preprocess_documents(self, documents):
        logger.info(f"Preprocessing {len(documents)} documents...")
        self._seen_hashes.clear()
        processed = [r for doc in documents if (r := self.preprocess_document(doc)) is not None]
        logger.info(f"Done: {len(processed)} kept, {len(documents)-len(processed)} skipped")
        return processed


class MathTextSplitter:
    """Split documents into overlapping chunks optimized for math content."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
            strip_headers=False,
        )
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
        )

    def split_document(self, doc) -> list:
        """Split a single document into chunks with metadata preserved."""
        try:
            md_chunks = self._markdown_splitter.split_text(doc.page_content)
            if len(md_chunks) > 1:
                chunks = []
                for mc in md_chunks:
                    sub_chunks = self._text_splitter.split_text(mc.page_content)
                    for sc in sub_chunks:
                        meta = {**doc.metadata, **mc.metadata}
                        chunks.append(Document(page_content=sc, metadata=meta))
                final = chunks
            else:
                texts = self._text_splitter.split_text(doc.page_content)
                final = [Document(page_content=t, metadata=doc.metadata.copy()) for t in texts]
        except Exception:
            texts = self._text_splitter.split_text(doc.page_content)
            final = [Document(page_content=t, metadata=doc.metadata.copy()) for t in texts]

        for i, chunk in enumerate(final):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(final)

        return final

    def split_documents(self, documents) -> list:
        """Split multiple documents and flatten into a single list."""
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.split_document(doc))
        logger.info(f"Split {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
