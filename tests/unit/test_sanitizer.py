"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: Input Sanitizer
Tests security middleware sanitization rules.
=============================================================================
"""

import pytest
from api.app.middleware.sanitizer import sanitize_string, DANGEROUS_PATTERNS, MAX_STRING_LENGTH


class TestSanitizeString:
    """Tests for the sanitize_string utility function."""

    def test_normal_string_unchanged(self):
        result = sanitize_string("Hello World")
        assert result == "Hello World"

    def test_empty_string(self):
        assert sanitize_string("") == ""

    def test_none_returns_none(self):
        assert sanitize_string(None) is None

    def test_html_escaped(self):
        result = sanitize_string('<script>alert("xss")</script>')
        assert "<script>" not in result
        assert "&lt;" in result

    def test_quotes_escaped(self):
        result = sanitize_string('value" onclick="bad')
        assert '"' not in result

    def test_null_bytes_removed(self):
        result = sanitize_string("hello\x00world")
        assert "\x00" not in result
        assert "helloworld" in result

    def test_truncation_at_max_length(self):
        long_string = "A" * (MAX_STRING_LENGTH + 100)
        result = sanitize_string(long_string)
        assert len(result) == MAX_STRING_LENGTH


class TestDangerousPatterns:
    """Tests that dangerous patterns are correctly detected."""

    def test_script_tag_detected(self):
        assert any(p.search("<script>alert(1)</script>") for p in DANGEROUS_PATTERNS)

    def test_javascript_uri_detected(self):
        assert any(p.search("javascript:void(0)") for p in DANGEROUS_PATTERNS)

    def test_event_handler_detected(self):
        assert any(p.search('onclick = "evil()"') for p in DANGEROUS_PATTERNS)

    def test_path_traversal_detected(self):
        assert any(p.search("../../etc/passwd") for p in DANGEROUS_PATTERNS)

    def test_sql_injection_detected(self):
        assert any(p.search("; DROP TABLE users;") for p in DANGEROUS_PATTERNS)

    def test_template_injection_detected(self):
        assert any(p.search("${process.env.SECRET}") for p in DANGEROUS_PATTERNS)

    def test_normal_input_not_flagged(self):
        safe_inputs = [
            "Hello World",
            "https://www.youtube.com/watch?v=abc123",
            "abcdef1234567890" * 4,
            "user@example.com",
        ]
        for inp in safe_inputs:
            matches = [p.search(inp) for p in DANGEROUS_PATTERNS]
            assert not any(matches), f"False positive for: {inp}"
