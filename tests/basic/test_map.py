"""
Map Tests

Tests basic map functionality including filter list and layout.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL


class TestMap:
    """Test suite for map functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to home page before each test"""
        page.goto(BASE_URL)
        yield

    def test_displays_filter_list_with_two_categories_with_5_items(self, page: Page):
        """Verify filter list has correct number of checkboxes and category labels"""
        # Check number of checkboxes
        checkboxes = page.locator('input[type="checkbox"]')
        expect(checkboxes).to_have_count(5)

        # Check number of category labels
        category_labels = page.locator('form span')
        expect(category_labels).to_have_count(2)

    def test_should_not_have_scrollbars(self, page: Page):
        """Verify the page has no horizontal or vertical scrollbars"""
        # Get viewport and document dimensions
        dimensions = page.evaluate("""
            () => {
                return {
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    scrollWidth: document.documentElement.scrollWidth,
                    scrollHeight: document.documentElement.scrollHeight
                };
            }
        """)

        # Assert no scrollbars (scroll dimensions should not exceed viewport)
        assert dimensions["scrollWidth"] <= dimensions["innerWidth"], \
            f"Horizontal scrollbar detected: scrollWidth={dimensions['scrollWidth']}, innerWidth={dimensions['innerWidth']}"

        assert dimensions["scrollHeight"] <= dimensions["innerHeight"], \
            f"Vertical scrollbar detected: scrollHeight={dimensions['scrollHeight']}, innerHeight={dimensions['innerHeight']}"
