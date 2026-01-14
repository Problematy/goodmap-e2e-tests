"""
Test suite for language switching functionality.

Tests that changing the language:
- Updates menu items
- Updates UI text (e.g., "report a problem" link)
- Updates page URLs (e.g., About page)
"""

import pytest
from playwright.sync_api import Page, expect

from tests.conftest import BASE_URL, MARKER_LOAD_TIMEOUT


class TestLanguageSwitching:
    """Test suite for language switching functionality"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to home page before each test"""
        page.goto(BASE_URL, wait_until="domcontentloaded")
        return

    def test_default_language_is_english(self, page: Page):
        """Verify default language is English with correct menu items"""
        # Check language button shows 'en'
        lang_button = page.get_by_role(
            "button", name="Language switch icon, used to change the language"
        )
        expect(lang_button).to_contain_text("en")

        # Check English menu items
        expect(page.get_by_role("link", name="Map", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="About")).to_be_visible()

    def test_switch_to_polish_changes_menu_items(self, page: Page):
        """Verify switching to Polish changes menu items"""
        # Click language switcher
        lang_button = page.get_by_role(
            "button", name="Language switch icon, used to change the language"
        )
        lang_button.click()

        # Select Polish
        page.get_by_role("link", name="polski").click()

        # Wait for page to reload
        page.wait_for_load_state("domcontentloaded")

        # Verify language button shows 'pl'
        expect(lang_button).to_contain_text("pl")

        # Check Polish menu items
        expect(page.get_by_role("link", name="Mapa")).to_be_visible()
        expect(page.get_by_role("link", name="O nas")).to_be_visible()

    def test_switch_to_polish_changes_popup_text(self, page: Page):
        """Verify switching to Polish changes popup UI text"""
        # Switch to Polish first
        lang_button = page.get_by_role(
            "button", name="Language switch icon, used to change the language"
        )
        lang_button.click()
        page.get_by_role("link", name="polski").click()
        page.wait_for_load_state("domcontentloaded")

        # Click marker cluster to expand
        page.locator(".leaflet-marker-icon").first.click()

        # Wait for markers to appear
        markers = page.locator(".leaflet-marker-icon")
        expect(markers).to_have_count(2, timeout=MARKER_LOAD_TIMEOUT)

        # Click rightmost marker to open popup
        page.evaluate(
            """
            () => {
                const markers = document.querySelectorAll('.leaflet-marker-icon');
                let rightmostMarker = null;
                let maxX = -Infinity;

                markers.forEach(marker => {
                    const rect = marker.getBoundingClientRect();
                    if (rect.x > maxX) {
                        maxX = rect.x;
                        rightmostMarker = marker;
                    }
                });

                if (rightmostMarker) {
                    rightmostMarker.click();
                }
            }
        """
        )

        # Verify popup is visible
        popup = page.locator(".leaflet-popup-content")
        expect(popup).to_be_visible()

        # Verify "report a problem" is in Polish
        expect(popup.get_by_text("zgłoś problem")).to_be_visible()

    def test_about_page_url_changes_with_language(self, page: Page):
        """Verify About page URL changes based on language"""
        # English About link should point to /blog/page/about
        about_link_en = page.get_by_role("link", name="About")
        expect(about_link_en).to_have_attribute("href", "/blog/page/about")

        # Switch to Polish
        lang_button = page.get_by_role(
            "button", name="Language switch icon, used to change the language"
        )
        lang_button.click()
        page.get_by_role("link", name="polski").click()
        page.wait_for_load_state("domcontentloaded")

        # Polish About link should point to /blog/page/o-nas
        about_link_pl = page.get_by_role("link", name="O nas")
        expect(about_link_pl).to_have_attribute("href", "/blog/page/o-nas")

    def test_switch_back_to_english_restores_menu(self, page: Page):
        """Verify switching back to English restores original menu items"""
        # Switch to Polish
        lang_button = page.get_by_role(
            "button", name="Language switch icon, used to change the language"
        )
        lang_button.click()
        page.get_by_role("link", name="polski").click()
        page.wait_for_load_state("domcontentloaded")

        # Verify Polish
        expect(page.get_by_role("link", name="Mapa")).to_be_visible()

        # Switch back to English
        lang_button.click()
        page.get_by_role("link", name="English").click()
        page.wait_for_load_state("domcontentloaded")

        # Verify English restored
        expect(lang_button).to_contain_text("en")
        expect(page.get_by_role("link", name="Map", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="About")).to_be_visible()
