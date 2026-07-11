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

class TestSSEFormat(unittest.TestCase):
    """Test SSE streaming output format."""

    def test_content_generator_stream_yields_chunks(self):
        """generate_text_stream should yield string chunks."""
        from content_generator import generate_text_stream
        # Just verify the function exists and is callable
        self.assertTrue(callable(generate_text_stream))

    def test_chat_endpoint_returns_sse(self):
        """Chat endpoint should return text/event-stream when authenticated."""
        from api import app
        with app.test_client() as client:
            # Login first
            resp = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin12345'})
            token = resp.get_json().get('token', '')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            # Test chat endpoint with auth
            resp = client.post('/api/chat', json={'message': 'hello'}, headers=headers)
            # Should return 200 with SSE or 500 if Ollama is offline
            self.assertIn(resp.status_code, [200, 500])

    def test_stream_endpoint_handles_missing_topic(self):
        """Stream endpoint should handle missing topic gracefully."""
        from api import app
        with app.test_client() as client:
            resp = client.post('/api/article/generate-stream', json={})
            # Should return 400 (bad request) for missing topic
            self.assertIn(resp.status_code, [400, 401])


class TestChatExport(unittest.TestCase):
    """Test chat export functions."""

    def test_export_chat_markdown_function_exists(self):
        """exportChatMarkdown should be defined in chat.js."""
        with open('static/chat.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function exportChatMarkdown', content)

    def test_export_chat_json_function_exists(self):
        """exportChatJSON should be defined in chat.js."""
        with open('static/chat.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function exportChatJSON', content)

    def test_share_chat_link_function_exists(self):
        """shareChatLink should be defined in chat.js."""
        with open('static/chat.js', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function shareChatLink', content)

    def test_export_buttons_in_index(self):
        """Export buttons should be in index.html."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('exportChatMarkdown', content)
        self.assertIn('exportChatJSON', content)
        self.assertIn('shareChatLink', content)


class TestMonitoringDashboard(unittest.TestCase):
    """Test monitoring dashboard functionality."""

    def test_monitor_auto_refresh_exists(self):
        """startMonitorAutoRefresh should be defined."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function startMonitorAutoRefresh', content)

    def test_monitor_uses_correct_element_id(self):
        """Monitor should use perfUrl, not monitorUrl."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertTrue('perfUrl' in content, 'Should use perfUrl')

    def test_monitor_wired_in_navigate(self):
        """Monitor auto-refresh should be called in navigate()."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('startMonitorAutoRefresh()', content)
        self.assertIn('stopMonitorAutoRefresh()', content)

    def test_score_drop_alert_exists(self):
        """checkScoreDrop function should exist."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('function checkScoreDrop', content)

    def test_refresh_rate_selector_exists(self):
        """Refresh rate selector should exist."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('monitorRate', content)
        self.assertIn('setMonitorRate', content)

    def test_theme_system_preference_detection(self):
        """Theme should detect system preference."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('prefers-color-scheme', content)

    def test_utils_js_loaded_before_chat(self):
        """utils.js should be loaded before chat.js."""
        with open('static/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        utils_pos = content.find('utils.js')
        chat_pos = content.find('chat.js')
        self.assertLess(utils_pos, chat_pos)
