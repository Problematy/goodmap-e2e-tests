"""
Navigation Bar Tests

Tests navigation bar functionality on mobile devices including:
- Hamburger menu alignment with logo
- Left menu visibility and positioning
"""

import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL, MOBILE_DEVICES, UI_VERTICAL_ALIGNMENT_TOLERANCE


class TestNavigationBarForSmallDevices:
    """Test suite for navigation bar on mobile devices"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to home page before each test"""
        page.goto(BASE_URL)
        yield

    @pytest.mark.parametrize("device_name", list(MOBILE_DEVICES.keys()))
    def test_hamburger_menu_vertically_centered_with_logo(
        self, page: Page, device_name: str
    ):
        """
        Verify hamburger menu is vertically centered with the logo on mobile devices.

        Tests on: iphone-6, ipad-2, samsung-s10
        """
        device = MOBILE_DEVICES[device_name]

        # Set viewport for mobile device
        page.set_viewport_size(device["viewport"])

        # Get logo position and center
        logo = page.locator('.navbar-brand')
        logo_box = logo.bounding_box()
        assert logo_box is not None, "Logo not found"

        logo_center = logo_box["y"] + logo_box["height"] / 2
        print(f"Logo Center: {logo_center}")

        # Check each hamburger menu center position
        hamburgers = page.locator('.navbar-toggler').all()
        for i, hamburger in enumerate(hamburgers):
            hamburger_box = hamburger.bounding_box()
            assert hamburger_box is not None, f"Hamburger {i+1} not found"

            hamburger_center = hamburger_box["y"] + hamburger_box["height"] / 2
            print(f"Hamburger Center {i+1}: {hamburger_center}")

            # Verify vertical alignment within tolerance
            diff = abs(hamburger_center - logo_center)
            assert diff <= UI_VERTICAL_ALIGNMENT_TOLERANCE, \
                f"Hamburger {i+1} not vertically aligned with logo on {device_name}. " \
                f"Difference: {diff}px (tolerance: {UI_VERTICAL_ALIGNMENT_TOLERANCE}px)"

    @pytest.mark.parametrize("device_name", list(MOBILE_DEVICES.keys()))
    def test_left_menu_visible_after_clicking_left_hamburger(
        self, page: Page, device_name: str
    ):
        """
        Verify left menu becomes visible after clicking left hamburger button
        and filter form is positioned below the navbar.

        Tests on: iphone-6, ipad-2, samsung-s10
        """
        device = MOBILE_DEVICES[device_name]

        # Set viewport for mobile device
        page.set_viewport_size(device["viewport"])

        # Verify left panel is not visible initially
        left_panel = page.locator('#left-panel')
        expect(left_panel).not_to_be_visible()

        # Click first (left) hamburger button
        page.locator('.navbar-toggler').first.click()

        # Verify left panel is now visible
        expect(left_panel).to_be_visible()

        # Get filter form position
        filter_form = page.locator('#filter-form')
        expect(filter_form).to_be_visible()

        filter_form_box = filter_form.bounding_box()
        assert filter_form_box is not None, "Filter form not found"
        filter_form_top = filter_form_box["y"]
        print(f"Filter Form Top: {filter_form_top}")

        # Get navbar bottom position
        navbar = page.locator('.navbar')
        navbar_box = navbar.bounding_box()
        assert navbar_box is not None, "Navbar not found"
        navbar_bottom = navbar_box["y"] + navbar_box["height"]
        print(f"Navbar Bottom: {navbar_bottom}")

        # Verify filter form is below navbar
        assert filter_form_top > navbar_bottom, \
            f"Filter form overlaps navbar on {device_name}. " \
            f"Filter top: {filter_form_top}, Navbar bottom: {navbar_bottom}"
