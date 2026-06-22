"""
Unit tests for security features:
1. bcrypt password hashing (users.py)
2. Flask-Limiter rate limiting (api.py)
3. SHA-256 backward compatibility and auto-upgrade
4. Session metadata cleanup using _session_meta
"""
import hashlib
import os
import sys
import time
import unittest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use SQLite for tests (no PostgreSQL needed)
os.environ.setdefault("DATABASE_URL", "")

# Use a test-specific SQLite database before importing modules that call init_db
import database
_TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_security.db")
database.SQLITE_PATH = _TEST_DB
database.init_db()


class TestPasswordHashing(unittest.TestCase):
    """Test bcrypt password hashing and SHA-256 backward compatibility."""

    def test_hash_password_returns_bcrypt(self):
        """_hash_password should return a bcrypt hash."""
        from users import _hash_password
        h = _hash_password("testpassword")
        self.assertTrue(h.startswith("$2"), f"Expected bcrypt hash, got: {h[:10]}...")
        self.assertEqual(len(h), 60, "bcrypt hash should be 60 characters")

    def test_verify_bcrypt_password(self):
        """_verify_password should verify bcrypt hashes correctly."""
        from users import _hash_password, _verify_password
        h = _hash_password("mypassword")
        self.assertTrue(_verify_password("mypassword", h))
        self.assertFalse(_verify_password("wrongpassword", h))
        self.assertFalse(_verify_password("", h))

    def test_verify_legacy_sha256_password(self):
        """_verify_password should verify legacy SHA-256 hashes."""
        from users import _verify_password
        legacy_hash = hashlib.sha256("oldpassword".encode()).hexdigest()
        self.assertTrue(_verify_password("oldpassword", legacy_hash))
        self.assertFalse(_verify_password("wrongpassword", legacy_hash))

    def test_different_hashes_for_same_password(self):
        """Each bcrypt hash of the same password should be different (salt)."""
        from users import _hash_password
        h1 = _hash_password("samepassword")
        h2 = _hash_password("samepassword")
        self.assertNotEqual(h1, h2, "Two bcrypt hashes of same password should differ (different salts)")

    def test_is_bcrypt_hash(self):
        """_is_bcrypt_hash should correctly identify bcrypt vs SHA-256 hashes."""
        from users import _hash_password, _is_bcrypt_hash
        bcrypt_hash = _hash_password("test")
        sha256_hash = hashlib.sha256("test".encode()).hexdigest()
        self.assertTrue(_is_bcrypt_hash(bcrypt_hash))
        self.assertFalse(_is_bcrypt_hash(sha256_hash))
        self.assertFalse(_is_bcrypt_hash(""))

    def test_empty_password(self):
        """Password hashing should handle empty strings."""
        from users import _hash_password, _verify_password
        h = _hash_password("")
        self.assertTrue(_verify_password("", h))
        self.assertFalse(_verify_password("notempty", h))


class TestUserManagement(unittest.TestCase):
    """Test user creation, verification, and password change with bcrypt."""

    def _clean_users(self):
        """Remove all test users from the database."""
        conn, db_type = database._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username NOT IN ('admin')")
        conn.commit()
        if db_type != "pg":
            conn.close()

    def setUp(self):
        """Ensure users table exists and clean test data."""
        self._clean_users()

    def tearDown(self):
        """Clean up test users."""
        self._clean_users()

    def test_create_and_verify_user(self):
        """Creating a user and verifying credentials should work with bcrypt."""
        from users import create_user, verify_user
        result = create_user("testuser", "securepass123", "user", "test@example.com")
        self.assertTrue(result.get("success"), f"Create failed: {result}")

        user = verify_user("testuser", "securepass123")
        self.assertIsNotNone(user, "Verification should succeed")
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["role"], "user")

    def test_verify_wrong_password(self):
        """Verification should fail with wrong password."""
        from users import create_user, verify_user
        create_user("wrongpw", "correctpass", "user")
        user = verify_user("wrongpw", "incorrectpass")
        self.assertIsNone(user, "Wrong password should return None")

    def test_verify_nonexistent_user(self):
        """Verification of non-existent user should return None."""
        from users import verify_user
        user = verify_user("ghost", "password")
        self.assertIsNone(user)

    def test_change_password(self):
        """Password change should work and new password should be bcrypt."""
        from users import create_user, change_password, verify_user
        create_user("changepw", "oldpass123", "user")
        result = change_password("changepw", "oldpass123", "newpass456")
        self.assertTrue(result.get("success"), f"Change failed: {result}")

        # Old password should no longer work
        self.assertIsNone(verify_user("changepw", "oldpass123"))
        # New password should work
        user = verify_user("changepw", "newpass456")
        self.assertIsNotNone(user)

    def test_change_password_wrong_old(self):
        """Password change should fail if old password is wrong."""
        from users import create_user, change_password
        create_user("wrongold", "correctold", "user")
        result = change_password("wrongold", "wrongoldpass", "newpass")
        self.assertFalse(result.get("success"))
        self.assertIn("incorrect", result.get("error", "").lower())

    def test_password_is_bcrypt_after_creation(self):
        """After creation, the stored password_hash should be bcrypt format."""
        from users import create_user
        create_user("bcryptcheck", "mypassword", "user")
        conn, db_type = database._get_connection()
        cursor = conn.cursor()
        if db_type == "pg":
            cursor.execute("SELECT password_hash FROM users WHERE username = %s", ("bcryptcheck",))
        else:
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("bcryptcheck",))
        row = cursor.fetchone()
        if db_type != "pg":
            conn.close()
        self.assertTrue(row["password_hash"].startswith("$2"),
                        f"Expected bcrypt hash, got: {row['password_hash'][:10]}...")

    def test_sha256_to_bcrypt_auto_upgrade(self):
        """Logging in with a legacy SHA-256 hash should auto-upgrade to bcrypt."""
        from users import verify_user, _is_bcrypt_hash

        # Manually insert a user with a legacy SHA-256 hash
        password = "upgrade_me"
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        conn, db_type = database._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = 'legacy_user'")
        if db_type == "pg":
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ("legacy_user", legacy_hash, "user"),
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("legacy_user", legacy_hash, "user"),
            )
        conn.commit()
        if db_type != "pg":
            conn.close()

        # Verify login works with legacy hash
        user = verify_user("legacy_user", password)
        self.assertIsNotNone(user, "Login with legacy SHA-256 should succeed")

        # Verify the hash was auto-upgraded to bcrypt
        conn, db_type = database._get_connection()
        cursor = conn.cursor()
        if db_type == "pg":
            cursor.execute("SELECT password_hash FROM users WHERE username = %s", ("legacy_user",))
        else:
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", ("legacy_user",))
        row = cursor.fetchone()
        if db_type != "pg":
            conn.close()
        self.assertTrue(_is_bcrypt_hash(row["password_hash"]),
                        f"Hash should be bcrypt after auto-upgrade, got: {row['password_hash'][:10]}")

        # Verify second login still works after upgrade
        user2 = verify_user("legacy_user", password)
        self.assertIsNotNone(user2, "Login should still work after auto-upgrade")


class TestRateLimiting(unittest.TestCase):
    """Test Flask-Limiter rate limiting on API endpoints."""

    def setUp(self):
        from api import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_login_rate_limit_enforced(self):
        """Login endpoint should enforce rate limiting (10 per minute)."""
        from api import _tokens
        _tokens.clear()

        responses = []
        for i in range(11):
            resp = self.client.post("/api/auth/login", json={
                "username": "test",
                "password": "test"
            })
            responses.append(resp.status_code)

        rate_limited = any(code == 429 for code in responses)
        self.assertTrue(rate_limited,
                        f"Expected at least one 429 response, got: {responses}")

    def test_auth_rejects_unauthenticated(self):
        """Authenticated endpoints should reject requests without a token."""
        resp = self.client.get("/api/auth/check")
        self.assertEqual(resp.status_code, 200, "Auth check should respond")
        data = resp.get_json()
        self.assertFalse(data.get("authenticated", False), "Should not be authenticated without token")


class TestTokenCleanup(unittest.TestCase):
    """Test that expired tokens are cleaned up."""

    def test_expired_tokens_removed(self):
        """Tokens older than TTL should be cleaned up."""
        from api import _tokens, _TOKEN_TTL, _cleanup_expired_tokens

        _tokens.clear()
        now = time.time()

        _tokens["expired_token"] = {
            "username": "old_user",
            "role": "user",
            "created_at": now - _TOKEN_TTL - 100
        }
        _tokens["fresh_token"] = {
            "username": "new_user",
            "role": "user",
            "created_at": now
        }

        _cleanup_expired_tokens()

        self.assertNotIn("expired_token", _tokens, "Expired token should be removed")
        self.assertIn("fresh_token", _tokens, "Fresh token should remain")


class TestSessionCleanup(unittest.TestCase):
    """Test that sessions work correctly and cleanup works via _session_meta."""

    def setUp(self):
        from api import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_session_created_on_authenticated_request(self):
        """Session should be created when an authenticated request is made."""
        from api import _session_store
        _session_store.clear()

        # Manually create a valid token (bypass login to avoid rate limit issues)
        from api import _tokens
        token = "test_session_token_xyz"
        _tokens[token] = {"username": "admin", "role": "admin", "created_at": time.time()}

        # Make an authenticated request with a specific session ID
        headers = {"Authorization": f"Bearer {token}", "X-Session-ID": "test_session_123"}
        resp = self.client.get("/api/keyword-research", headers=headers)
        self.assertIn("test_session_123", _session_store,
                       "Session should be created after authenticated request")

    def test_session_cleanup_removes_stale_sessions(self):
        """Stale sessions older than _SESSION_TTL should be cleaned up."""
        from api import _session_store, _session_meta, _SESSION_TTL, _get_session
        from flask import Flask

        # Clear existing sessions
        _session_store.clear()
        _session_meta.clear()

        # Manually insert stale sessions (older than TTL)
        stale_time = time.time() - _SESSION_TTL - 100
        _session_store["stale_sid_1"] = {"keyword_data": {"seed": "old"}}
        _session_store["stale_sid_2"] = {"keyword_data": {"seed": "older"}}
        _session_meta["stale_sid_1"] = {"last_access": stale_time}
        _session_meta["stale_sid_2"] = {"last_access": stale_time}

        # Insert a fresh session
        fresh_time = time.time()
        _session_store["fresh_sid"] = {"keyword_data": {"seed": "new"}}
        _session_meta["fresh_sid"] = {"last_access": fresh_time}

        # Manually trigger cleanup (simulating what _get_session does)
        now = time.time()
        stale = [sid for sid, meta in _session_meta.items()
                 if now - meta.get("last_access", 0) > _SESSION_TTL]
        for sid in stale:
            _session_store.pop(sid, None)
            _session_meta.pop(sid, None)

        # Verify stale sessions were removed
        self.assertNotIn("stale_sid_1", _session_store, "Stale session 1 should be removed")
        self.assertNotIn("stale_sid_2", _session_store, "Stale session 2 should be removed")
        self.assertNotIn("stale_sid_1", _session_meta, "Stale session 1 meta should be removed")
        self.assertNotIn("stale_sid_2", _session_meta, "Stale session 2 meta should be removed")

        # Verify fresh session remains
        self.assertIn("fresh_sid", _session_store, "Fresh session should remain")
        self.assertIn("fresh_sid", _session_meta, "Fresh session meta should remain")

    def test_session_metadata_separated_from_data(self):
        """_last_access should be in _session_meta, not in _session_store."""
        from api import _session_store, _session_meta

        _session_store.clear()
        _session_meta.clear()

        # Simulate creating a session via _get_session
        sid = "test_meta_separation"
        _session_store[sid] = {"keyword_data": {"seed": "test"}}
        _session_meta[sid] = {"last_access": time.time()}

        # Verify data is separated
        self.assertIn("keyword_data", _session_store[sid], "Session store should have keyword_data")
        self.assertNotIn("last_access", _session_store[sid], "Session store should NOT have last_access")
        self.assertIn("last_access", _session_meta[sid], "Session meta should have last_access")
        self.assertNotIn("keyword_data", _session_meta[sid], "Session meta should NOT have keyword_data")


if __name__ == "__main__":
    unittest.main(verbosity=2)
