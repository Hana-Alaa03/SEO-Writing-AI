import unittest
from datetime import datetime

from src.utils.seo_utils import (
    finalize_article_title,
    keyword_implies_title_freshness,
    normalize_title_year,
    title_needs_freshness_year,
)


class TestTitleYearNormalization(unittest.TestCase):
  def test_normalize_replaces_stale_year(self):
    year = str(datetime.now().year)
    self.assertEqual(
      normalize_title_year("افضل شركة تصميم مواقع 2024 في السعودية"),
      f"افضل شركة تصميم مواقع {year} في السعودية",
    )

  def test_normalize_replaces_year_placeholder(self):
    year = str(datetime.now().year)
    self.assertEqual(
      normalize_title_year("Top agencies [year]"),
      f"Top agencies {year}",
    )

  def test_finalize_adds_year_for_commercial_ranking_keyword(self):
    year = str(datetime.now().year)
    title = finalize_article_title(
      "افضل شركة تصميم مواقع في السعودية: حلول احترافية",
      keyword="افضل شركة تصميم مواقع في السعودية",
      intent="commercial",
      content_type="brand_commercial",
      raw_title="افضل شركة تصميم مواقع في السعودية",
    )
    self.assertIn(year, title)
    self.assertNotIn("2024", title)
    self.assertNotIn("2025", title)

  def test_finalize_normalizes_existing_year_before_brand_suffix(self):
    year = str(datetime.now().year)
    title = finalize_article_title(
      "افضل شركة تصميم مواقع 2023 | Creative Minds",
      keyword="افضل شركة تصميم مواقع في السعودية",
      intent="commercial",
      content_type="brand_commercial",
      raw_title="افضل شركة تصميم مواقع في السعودية",
    )
    self.assertIn(f"{year} | Creative Minds", title)
    self.assertNotIn("2023", title)

  def test_finalize_does_not_add_year_for_conceptual_informational(self):
    year = str(datetime.now().year)
    title = finalize_article_title(
      "SEO vs SEM: Complete Guide",
      keyword="seo vs sem",
      intent="informational",
      content_type="informational",
      raw_title="seo vs sem",
    )
    self.assertNotIn(year, title)

  def test_keyword_implies_freshness_for_arabic_best(self):
    self.assertTrue(keyword_implies_title_freshness("افضل شركة تصميم مواقع"))

  def test_title_needs_freshness_when_raw_title_has_year(self):
    self.assertTrue(
      title_needs_freshness_year(
        keyword="guide to widgets",
        intent="informational",
        content_type="informational",
        raw_title="Widget guide 2022",
      )
    )


if __name__ == "__main__":
  unittest.main()
