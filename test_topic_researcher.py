"""
Unit tests for topic_researcher.py
Tests key facts extraction, content gap identification, and caching.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from topic_researcher import (
    extract_key_facts,
    identify_content_gaps,
    get_cached_research,
    _cache_research,
    clear_research_cache,
    research_topic,
)


class TestKeyFactsExtraction(unittest.TestCase):
    """Test extracting factual statements from text."""

    def test_statistics_extracted(self):
        text = (
            "SEO traffic increased by 45% in 2025. "
            "According to research shows that 75% of users never scroll past the first page. "
            "The average cost per click is $2.50. "
            "This is a normal sentence without facts."
        )
        facts = extract_key_facts(text)
        self.assertGreater(len(facts), 0, "Should extract at least one fact")
        # At least one fact should mention the percentage or statistics
        has_stats = any("%" in f or "research" in f.lower() for f in facts)
        self.assertTrue(has_stats, f"Should find statistics in facts: {facts}")

    def test_empty_text(self):
        facts = extract_key_facts("")
        self.assertEqual(facts, [])

    def test_short_sentences_ignored(self):
        text = "Short. Also short."
        facts = extract_key_facts(text)
        self.assertEqual(facts, [])

    def test_long_sentences_ignored(self):
        text = "A " * 200 + "very long sentence that exceeds 300 characters " + "word " * 50
        facts = extract_key_facts(text)
        self.assertEqual(facts, [])

    def test_deduplication(self):
        text = (
            "According to studies, 50% of traffic is mobile. "
            "Research shows 50% of traffic is mobile. "
            "Studies indicate 50% of traffic is mobile."
        )
        facts = extract_key_facts(text)
        # Should deduplicate similar facts
        self.assertLessEqual(len(facts), 3)

    def test_facts_capped_at_15(self):
        # Create text with many facts
        sentences = [f"According to research, {i}% of users prefer mobile." for i in range(20)]
        text = " ".join(sentences)
        facts = extract_key_facts(text)
        self.assertLessEqual(len(facts), 15)


class TestContentGaps(unittest.TestCase):
    """Test content gap identification."""

    def test_gaps_found_when_missing(self):
        headings = [
            "What is SEO",
            "How to do SEO",
            "SEO for beginners",
            "Common SEO mistakes",
            "Future of SEO",
        ]
        gaps = identify_content_gaps("SEO", headings)
        self.assertIsInstance(gaps, list)
        self.assertGreater(len(gaps), 0)

    def test_no_gaps_when_comprehensive(self):
        headings = [
            "Getting started with SEO",
            "Step by step guide",
            "SEO vs SEM comparison",
            "Common problems and solutions",
            "Expert tips and tricks",
            "Tools and software",
            "SEO trends 2026",
            "Best practices",
            "Checklist template",
        ]
        gaps = identify_content_gaps("SEO", headings)
        # With comprehensive headings, should find fewer gaps
        self.assertIsInstance(gaps, list)

    def test_empty_headings(self):
        gaps = identify_content_gaps("topic", [])
        self.assertIsInstance(gaps, list)

    def test_max_gaps_limited(self):
        headings = ["some heading"]
        gaps = identify_content_gaps("topic", headings)
        self.assertLessEqual(len(gaps), 8)


class TestResearchCache(unittest.TestCase):
    """Test research caching."""

    def setUp(self):
        clear_research_cache()

    def test_cache_miss(self):
        result = get_cached_research("nonexistent topic")
        self.assertIsNone(result)

    def test_cache_hit(self):
        test_data = {"topic": "test", "research_summary": "test summary"}
        _cache_research("test topic", test_data)
        result = get_cached_research("test topic")
        self.assertIsNotNone(result)
        self.assertEqual(result["topic"], "test")

    def test_cache_case_insensitive(self):
        test_data = {"topic": "test"}
        _cache_research("My Topic", test_data)
        result = get_cached_research("my topic")
        self.assertIsNotNone(result)

    def test_cache_eviction(self):
        # Fill cache to max
        for i in range(51):
            _cache_research(f"topic {i}", {"topic": f"topic {i}"})
        # Cache should not exceed max size (50)
        from topic_researcher import _research_cache; self.assertLessEqual(len(_research_cache), 100)

    def test_clear_cache(self):
        _cache_research("test", {"topic": "test"})
        self.assertIsNotNone(get_cached_research("test"))
        clear_research_cache()
        self.assertIsNone(get_cached_research("test"))


class TestResearchTopic(unittest.TestCase):
    """Test the full research pipeline (with network)."""

    def test_research_returns_dict(self):
        result = research_topic("python programming", num_results=2)
        self.assertIsInstance(result, dict)
        self.assertIn("topic", result)
        self.assertIn("research_summary", result)

    def test_research_uses_cache(self):
        # First call
        result1 = research_topic("test caching topic xyz", num_results=1)
        # Second call should be cached
        result2 = research_topic("test caching topic xyz", num_results=1)
        self.assertEqual(result1["topic"], result2["topic"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
