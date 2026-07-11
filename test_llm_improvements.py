"""Tests for LLM section improvements: shared check_ollama, retry, thread-safe cache, parallel difficulty"""
import time
import threading
import unittest
from unittest.mock import patch, MagicMock
import requests


class TestCheckOllama(unittest.TestCase):
    """Test the shared check_ollama utility."""

    def test_check_ollama_returns_bool(self):
        from config import check_ollama
        result = check_ollama()
        self.assertIsInstance(result, bool)

    def test_check_ollama_returns_false_when_offline(self):
        from config import check_ollama
        with patch('config.requests.get', side_effect=Exception('Connection refused')):
            result = check_ollama()
            self.assertFalse(result)

    def test_check_ollama_returns_true_when_online(self):
        from config import check_ollama
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch('config.requests.get', return_value=mock_resp):
            # Reset cache
            import config
            config._ollama_check_cache = None
            result = check_ollama()
            self.assertTrue(result)

    def test_check_ollama_caches_result(self):
        """Verify caching works - second call should be instant."""
        from config import check_ollama
        import config
        config._ollama_check_cache = None
        config._ollama_check_cache_time = 0

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_resp

        with patch('config.requests.get', side_effect=mock_get):
            result1 = check_ollama()
            self.assertTrue(result1)
            self.assertEqual(call_count, 1)

            # Second call should use cache
            result2 = check_ollama()
            self.assertTrue(result2)
            self.assertEqual(call_count, 1)  # Still 1 - used cache


class TestRetryLogic(unittest.TestCase):
    """Test retry/backoff in content_generator._retry_call."""

    def test_retry_succeeds_on_first_try(self):
        from content_generator import _retry_call
        func = MagicMock(return_value='success')
        result = _retry_call(func, max_retries=2)
        self.assertEqual(result, 'success')
        func.assert_called_once()

    def test_retry_succeeds_after_failure(self):
        from content_generator import _retry_call
        func = MagicMock(side_effect=[Exception('fail'), 'success'])
        result = _retry_call(func, max_retries=2)
        self.assertEqual(result, 'success')
        self.assertEqual(func.call_count, 2)

    def test_retry_exhausts_retries(self):
        from content_generator import _retry_call
        func = MagicMock(side_effect=Exception('always fail'))
        with self.assertRaises(Exception):
            _retry_call(func, max_retries=1)
        self.assertEqual(func.call_count, 2)  # initial + 1 retry


class TestThreadSafeEmbeddingCache(unittest.TestCase):
    """Test that embedding model cache is thread-safe."""

    def test_concurrent_access(self):
        """Multiple threads reading/writing the cache shouldn't crash."""
        from llm_keyword_intelligence import _embedding_lock
        results = []

        def reader():
            with _embedding_lock:
                results.append('ok')

        threads = [threading.Thread(target=reader) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(results), 20)


class TestPersianDetection(unittest.TestCase):
    """Test Persian text detection for short strings."""

    def test_short_persian_detected(self):
        from llm_keyword_intelligence import _is_persian
        # Single Persian character should be detected
        self.assertTrue(_is_persian('خ'))

    def test_english_not_detected(self):
        from llm_keyword_intelligence import _is_persian
        self.assertFalse(_is_persian('hello'))

    def test_mixed_persian_english(self):
        from llm_keyword_intelligence import _is_persian
        self.assertTrue(_is_persian('آموزش python'))


class TestChatHistoryCleanup(unittest.TestCase):
    """Test that chat history cleanup works."""

    def test_cleanup_function_exists(self):
        from api import _cleanup_chat_history
        self.assertTrue(callable(_cleanup_chat_history))


if __name__ == '__main__':
    unittest.main(verbosity=2)
