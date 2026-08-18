"""Restore AI embeddings from a backup produced by rebuild_embeddings."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.ai.models import AIChunk, AIEmbedding


class Command(BaseCommand):
    help = "Restore embedding vectors from a gzip JSONL backup below backend/."

    def add_arguments(self, parser):
        parser.add_argument("backup_path")
        parser.add_argument("--batch-size", type=int, default=64)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        if batch_size < 1 or batch_size > 256:
            raise CommandError("--batch-size must be between 1 and 256")

        path = self._resolve_backup(options["backup_path"])
        rows = self._read_rows(path)
        self.stdout.write(f"Backup rows: {len(rows)}")
        if options["dry_run"]:
            return

        restored = 0
        for offset in range(0, len(rows), batch_size):
            batch = rows[offset : offset + batch_size]
            chunk_ids = [row["chunk_id"] for row in batch]
            chunks = AIChunk.objects.in_bulk(chunk_ids)
            missing = sorted(set(chunk_ids) - set(chunks))
            if missing:
                raise CommandError(f"Backup references missing chunk IDs: {missing[:10]}")

            embeddings = [
                AIEmbedding(
                    chunk=chunks[row["chunk_id"]],
                    embedding_model=row["embedding_model"],
                    embedding_vector=row["embedding_vector"],
                )
                for row in batch
            ]
            with transaction.atomic():
                AIEmbedding.objects.bulk_create(
                    embeddings,
                    batch_size=batch_size,
                    update_conflicts=True,
                    update_fields=["embedding_model", "embedding_vector"],
                    unique_fields=["chunk"],
                )
            restored += len(embeddings)
            self.stdout.write(f"Restored {restored}/{len(rows)} embeddings")

        self.stdout.write(self.style.SUCCESS(f"Restored {restored} embeddings successfully."))

    def _resolve_backup(self, raw_path: str) -> Path:
        base_dir = Path(settings.BASE_DIR).resolve()
        path = (base_dir / raw_path).resolve()
        try:
            path.relative_to(base_dir)
        except ValueError as exc:
            raise CommandError("backup_path must stay below backend/") from exc
        if not path.is_file():
            raise CommandError(f"Backup not found: {path}")
        return path

    def _read_rows(self, path: Path) -> list[dict]:
        rows = []
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                row = json.loads(line)
                vector = row.get("embedding_vector")
                if vector is None or len(vector) != settings.VECTOR_DIMENSION:
                    raise CommandError(f"Invalid vector at backup line {line_number}")
                rows.append(row)
        return rows
