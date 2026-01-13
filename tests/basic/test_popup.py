"""
Popup Tests

Tests popup functionality including content display and CTA buttons.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL, MARKER_LOAD_TIMEOUT
from tests.helpers import verify_popup_content, EXPECTED_PLACE_ZWIERZYNIECKA, get_rightmost_marker


class TestPopupOnDesktop:
    """Test suite for popup functionality on desktop"""

    def test_displays_popup_title_subtitle_categories_and_cta(
        self, page: Page, window_open_stub
    ):
        """
        Verify popup displays title, subtitle, categories, and CTA button correctly.

        Note: There's a TODO/BUG in the original test - problem form testing is
        skipped because the close button may be hidden when form is opened on desktop.
        """
        page.goto(BASE_URL)

        # Click first marker to trigger cluster expansion
        first_marker = page.locator('.leaflet-marker-icon').first
        first_marker.click()

        # Wait for markers to appear (should be 2 after cluster expansion)
        markers = page.locator('.leaflet-marker-icon')
        expect(markers).to_have_count(2, timeout=MARKER_LOAD_TIMEOUT)

        # Click the rightmost marker
        # Note: Using evaluate to find rightmost marker since we don't have data-testid
        page.evaluate("""
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
        """)

        # Verify popup content
        popup = page.locator('.leaflet-popup-content')
        expect(popup).to_be_visible()

        verify_popup_content(page, EXPECTED_PLACE_ZWIERZYNIECKA)

        # Verify close button and click it
        close_button = page.locator('.leaflet-popup-close-button')
        expect(close_button).to_be_visible()
        close_button.click()

        # Verify popup is closed
        expect(popup).not_to_be_visible()
