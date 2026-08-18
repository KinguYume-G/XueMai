from unittest.mock import Mock, patch
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from apps.ai.clients.ollama_client import OllamaClient
from apps.ai.services.rag_engine import RAGEngine
from apps.ai.services.file_processor import FileProcessor


class OllamaClientTests(SimpleTestCase):
    @patch("apps.ai.clients.ollama_client.requests.post")
    def test_qwen_reasoning_is_disabled_for_final_answer_api(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"message": {"content": "answer"}}
        post.return_value = response

        client = OllamaClient(model="qwen3:8b")
        result = client.chat_completion([{"role": "user", "content": "hello"}])

        self.assertEqual(result, "answer")
        self.assertIs(post.call_args.kwargs["json"]["think"], False)


class RAGEngineTests(SimpleTestCase):
    def test_retrieve_enforces_active_shared_documents(self):
        engine = object.__new__(RAGEngine)
        engine._retrieve_from_pgvector = Mock(return_value=[])

        engine.retrieve("question", filters={"doc_type": "course"})

        filters = engine._retrieve_from_pgvector.call_args.args[2]
        self.assertEqual(filters["is_active"], True)
        self.assertEqual(filters["system_documents_only"], True)
        self.assertEqual(filters["doc_type"], "course")

    def test_legacy_rag_query_uses_current_client_interface(self):
        engine = object.__new__(RAGEngine)
        engine.retrieve = Mock(return_value=[])
        client = Mock()
        client.chat_completion.return_value = "grounded answer"

        result = engine.rag_query("question", client)

        self.assertEqual(result, "grounded answer")
        client.chat_completion.assert_called_once()


class FileProcessorTests(SimpleTestCase):
    def test_rejects_legacy_doc_format(self):
        upload = SimpleUploadedFile("resume.doc", b"legacy", content_type="application/msword")
        with self.assertRaisesMessage(ValueError, "不支持"):
            FileProcessor.validate_file(upload)

    def test_rejects_mismatched_mime(self):
        upload = SimpleUploadedFile("resume.pdf", b"not-a-pdf", content_type="text/plain")
        with self.assertRaisesMessage(ValueError, "MIME"):
            FileProcessor.validate_file(upload)

    def test_processes_csv_bytes_stream(self):
        result = FileProcessor.process_file_from_stream(BytesIO(b"name,score\nAlice,95\n"), "csv")
        self.assertIn("Alice | 95", result["extracted_text"])
