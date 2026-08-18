"""Safely rebuild pgvector embeddings from the configured Ollama model."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from langchain_ollama import OllamaEmbeddings

from apps.ai.models import AIChunk, AIEmbedding


class Command(BaseCommand):
    help = "Rebuild AIChunk embeddings in batches, with optional compressed backup."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=32)
        parser.add_argument("--start-id", type=int, default=0)
        parser.add_argument("--limit", type=int)
        parser.add_argument("--missing-only", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--backup-path",
            help="Path below backend/ for a gzip JSONL backup before any vectors are changed.",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        if batch_size < 1 or batch_size > 256:
            raise CommandError("--batch-size must be between 1 and 256")

        chunks = AIChunk.objects.filter(id__gt=options["start_id"]).order_by("id")
        if options["missing_only"]:
            chunks = chunks.filter(embedding__isnull=True)
        if options["limit"] is not None:
            if options["limit"] < 1:
                raise CommandError("--limit must be positive")
            chunks = chunks[: options["limit"]]

        chunk_ids = list(chunks.values_list("id", flat=True))
        total = len(chunk_ids)
        self.stdout.write(
            f"Target chunks: {total}; model={settings.EMBEDDING_MODEL}; "
            f"dimensions={settings.VECTOR_DIMENSION}"
        )
        if options["dry_run"] or total == 0:
            return

        backup_path = options.get("backup_path")
        if backup_path:
            self._write_backup(backup_path)

        client = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        probe = client.embed_query("XueMai embedding dimension check")
        if len(probe) != settings.VECTOR_DIMENSION:
            raise CommandError(
                f"Embedding dimension mismatch: got {len(probe)}, "
                f"expected {settings.VECTOR_DIMENSION}"
            )

        processed = 0
        for offset in range(0, total, batch_size):
            ids = chunk_ids[offset : offset + batch_size]
            batch = list(AIChunk.objects.filter(id__in=ids).order_by("id"))
            non_empty = [chunk for chunk in batch if chunk.content.strip()]
            if not non_empty:
                continue

            vectors = client.embed_documents([chunk.content.strip() for chunk in non_empty])
            if any(len(vector) != settings.VECTOR_DIMENSION for vector in vectors):
                raise CommandError(f"Invalid vector dimensions in batch beginning with chunk {ids[0]}")

            existing = {
                item.chunk_id: item
                for item in AIEmbedding.objects.filter(
                    chunk_id__in=[chunk.id for chunk in non_empty]
                )
            }
            to_create = []
            to_update = []
            for chunk, vector in zip(non_empty, vectors, strict=True):
                embedding = existing.get(chunk.id)
                if embedding is None:
                    to_create.append(
                        AIEmbedding(
                            chunk=chunk,
                            embedding_vector=vector,
                            embedding_model=settings.EMBEDDING_MODEL,
                        )
                    )
                else:
                    embedding.embedding_vector = vector
                    embedding.embedding_model = settings.EMBEDDING_MODEL
                    to_update.append(embedding)

            with transaction.atomic():
                if to_create:
                    AIEmbedding.objects.bulk_create(to_create, batch_size=batch_size)
                if to_update:
                    AIEmbedding.objects.bulk_update(
                        to_update,
                        ["embedding_vector", "embedding_model"],
                        batch_size=batch_size,
                    )

            processed += len(non_empty)
            self.stdout.write(f"Processed {processed}/{total} chunks (last id={non_empty[-1].id})")

        self.stdout.write(self.style.SUCCESS(f"Rebuilt {processed} embeddings successfully."))

    def _write_backup(self, raw_path: str) -> None:
        base_dir = Path(settings.BASE_DIR).resolve()
        path = (base_dir / raw_path).resolve()
        try:
            path.relative_to(base_dir)
        except ValueError as exc:
            raise CommandError("--backup-path must stay below backend/") from exc
        if path.exists():
            raise CommandError(f"Backup already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            rows = AIEmbedding.objects.order_by("id").values_list(
                "id", "chunk_id", "embedding_model", "embedding_vector"
            )
            for embedding_id, chunk_id, model, vector in rows.iterator(chunk_size=100):
                handle.write(
                    json.dumps(
                        {
                            "id": embedding_id,
                            "chunk_id": chunk_id,
                            "embedding_model": model,
                            "embedding_vector": (
                                [float(value) for value in vector] if vector is not None else None
                            ),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Backed up {count} embeddings to {path}"))
