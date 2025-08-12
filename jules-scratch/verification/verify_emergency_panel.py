import os
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Construct the full file path
    file_path = '/app/emergency-panel-app/index.html'

    # Navigate to the local HTML file
    page.goto(f'file://{file_path}')

    # Wait for the page to load
    page.wait_for_selector('h1')

    # Take a screenshot
    screenshot_path = 'jules-scratch/verification/emergency-panel.png'
    page.screenshot(path=screenshot_path)

    print(f"Screenshot saved to {screenshot_path}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
