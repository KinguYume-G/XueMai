"""
Retrieval-Augmented Generation (RAG) engine utilities.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

logger = logging.getLogger(__name__)


class RAGEngine:
    """Manage document ingestion, retrieval, and response generation."""

    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        """
        Prepare embeddings, vector store, and text splitter resources.

        Args:
            persist_directory: Location used by Chroma to store embeddings.
        """
        try:
            self.embeddings = OllamaEmbeddings(
                model="nomic-embed-text",
                base_url="http://localhost:11434",
            )

            self.vectorstore = Chroma(
                collection_name="unipulse_docs",
                embedding_function=self.embeddings,
                persist_directory=persist_directory,
            )

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,      # ← 改小，让chunks更精细
                chunk_overlap=100,   # ← 减少重叠
                length_function=len,
                separators=["\n\n", "\n", " ", ""],  # ← 添加分隔符优先级
)
            

            logger.info(
                "Initialized RAG engine with persist directory '%s'",
                persist_directory,
            )
        except Exception as exc:
            logger.error("Failed to initialize RAG engine: %s", exc)
            raise

    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Read a document, split it into chunks, and add it to the vector store.

        Args:
            file_path: Path to a UTF-8 text document.
            metadata: Optional metadata dictionary applied to every chunk.

        Returns:
            The number of chunks added to the vector store.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                text = file_obj.read()

            chunks = self.text_splitter.split_text(text)

            if metadata is None:
                metadata = {}
            metadata["file_path"] = file_path

            metadatas = [metadata.copy() for _ in chunks]
            self.vectorstore.add_texts(texts=chunks, metadatas=metadatas)

            logger.info(
                "Ingested document '%s' as %d chunks",
                file_path,
                len(chunks),
            )
            return len(chunks)
        except FileNotFoundError:
            logger.error("Document not found: %s", file_path)
            raise
        except Exception as exc:
            logger.error("Failed to ingest document '%s': %s", file_path, exc)
            raise

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Retrieve the most relevant documents for a query.

        Args:
            query: Natural language query string.
            top_k: Maximum number of documents to return.
            filters: Optional metadata filters for the vector store.

        Returns:
            A list of langchain Document instances.
        """
        try:
            if filters:
                results = self.vectorstore.similarity_search(
                    query,
                    k=top_k,
                    filter=filters,
                )
            else:
                results = self.vectorstore.similarity_search(
                    query,
                    k=top_k,
                )

            logger.info(
                "Retrieved %d documents for query '%s'",
                len(results),
                query,
            )
            return results
        except Exception as exc:
            logger.error("Failed to retrieve documents: %s", exc)
            raise

    def rag_query(
        self,
        question: str,
        ollama_client: Any,
        top_k: int = 3,
    ) -> str:
        """
        Execute a complete RAG workflow for a user question.

        Args:
            question: User question to answer.
            ollama_client: Instance of `OllamaClient` used for generation.
            top_k: Number of documents to use as supporting context.

        Returns:
            The generated answer string.
        """
        try:
            docs = self.retrieve(question, top_k=top_k)
            context = "\n\n".join(doc.page_content for doc in docs)

            prompt_path = Path(__file__).parent.parent / "prompts" / "academic.txt"
            with open(prompt_path, "r", encoding="utf-8") as prompt_file:
                system_prompt = prompt_file.read()

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Use the following context to answer the question.\n\n"
                        f"Context:\n{context}\n\n"
                        f"Question:\n{question}\n\n"
                        "Answer only with information grounded in the context."
                    ),
                },
            ]

            result = ollama_client.chat(messages)
            logger.info("RAG query completed in %d ms", result["elapsed_ms"])

            return result["content"]
        except Exception as exc:
            logger.error("Failed to execute RAG query: %s", exc)
            raise
