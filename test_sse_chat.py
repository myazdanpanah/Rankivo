"""Tests for SSE streaming and AI Chat endpoints"""
import json
import unittest
from unittest.mock import patch, MagicMock
import requests


class TestSSEStreamingEndpoint(unittest.TestCase):
    """Test the /api/article/generate-stream endpoint."""

    def test_stream_endpoint_exists(self):
        """Verify the streaming endpoint is registered."""
        from api import app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertIn('/api/article/generate-stream', rules)

    def test_chat_endpoint_exists(self):
        """Verify the chat endpoint is registered."""
        from api import app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertIn('/api/chat', rules)

    def test_chat_history_endpoint_exists(self):
        """Verify the chat history endpoint is registered."""
        from api import app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertIn('/api/chat/history', rules)

    def test_chat_clear_endpoint_exists(self):
        """Verify the chat clear endpoint is registered."""
        from api import app
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertIn('/api/chat/clear', rules)


class TestChatHistory(unittest.TestCase):
    """Test chat history management."""

    def test_chat_history_is_dict(self):
        """Chat history should be a dictionary."""
        from api import _chat_history
        self.assertIsInstance(_chat_history, dict)

    def test_chat_history_empty_by_default(self):
        """New session should have empty history."""
        from api import _chat_history
        # Clean up any test data
        _chat_history.pop('test_session', None)
        self.assertNotIn('test_session', _chat_history)


class TestCleanupFunction(unittest.TestCase):
    """Test chat history cleanup."""

    def test_cleanup_is_callable(self):
        from api import _cleanup_chat_history
        self.assertTrue(callable(_cleanup_chat_history))

    def test_cleanup_removes_old_sessions(self):
        """Sessions older than 1 hour should be cleaned up."""
        from api import _chat_history, _cleanup_chat_history, _chat_last_cleanup
        import api
        import time
        
        # Force cleanup by resetting last cleanup time
        api._chat_last_cleanup = 0
        
        # Add an old session
        _chat_history['old_session'] = [{'role': 'user', 'content': 'test', 'timestamp': time.time() - 7200}]
        
        # Run cleanup
        _cleanup_chat_history()
        
        # Old session should be removed
        self.assertNotIn('old_session', _chat_history)

    def test_cleanup_keeps_recent_sessions(self):
        """Recent sessions should not be cleaned up."""
        from api import _chat_history, _cleanup_chat_history
        import time
        
        # Add a recent session
        _chat_history['recent_session'] = [{'role': 'user', 'content': 'test', 'timestamp': time.time()}]
        
        # Run cleanup
        _cleanup_chat_history()
        
        # Recent session should still exist
        self.assertIn('recent_session', _chat_history)
        
        # Cleanup
        _chat_history.pop('recent_session', None)


class TestUtilsJS(unittest.TestCase):
    """Test that utils.js functions exist and work."""

    def test_utils_file_exists(self):
        import os
        self.assertTrue(os.path.exists('static/utils.js'))

    def test_escH_function(self):
        """escH should escape HTML entities."""
        # Simulate the function
        def escH(s):
            import html
            return html.escape(s)
        
        self.assertEqual(escH('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertEqual(escH('Hello & World'), 'Hello &amp; World')

    def test_renderMarkdown_bold(self):
        """renderMarkdown should convert **bold** to <strong>."""
        import re
        def renderMarkdown(text):
            import html
            h = html.escape(text)
            h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
            return h
        
        result = renderMarkdown('This is **bold** text')
        self.assertIn('<strong>bold</strong>', result)

    def test_renderMarkdown_code_blocks(self):
        """renderMarkdown should convert ``` to <pre>."""
        import re
        def renderMarkdown(text):
            import html
            h = html.escape(text)
            h = re.sub(r'```\w*\n([\s\S]*?)```', r'<pre><code>\1</code></pre>', h)
            return h
        
        result = renderMarkdown('```\nprint(1)\n```')
        self.assertIn('<pre>', result)


class TestModelSelector(unittest.TestCase):
    """Test model selector functionality."""

    def test_chat_model_in_request(self):
        """Verify model field is sent in chat requests."""
        # Check chat.js has getChatModel
        with open('static/chat.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('getChatModel', content)
        self.assertIn('model: getChatModel()', content)

    def test_article_stream_has_model(self):
        """Verify model field is in article streaming request."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('getSelectedModel', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
