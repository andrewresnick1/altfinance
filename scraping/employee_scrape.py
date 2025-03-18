from playwright.sync_api import sync_playwright
import re  # For extracting job count numbers

# ✅ Define a list of valid countries
VALID_COUNTRIES = {
    "India", "United States of America", "Ireland", "Canada", "Portugal", "United Kingdom", "Poland", "Colombia", 
    "Mexico", "Brazil", "Japan", "Malaysia", "Australia", "Singapore", "Czechia", "Türkiye", "Hungary", "China",
    "Germany", "Indonesia", "Israel", "Greece", "United Arab Emirates", "Denmark", "Argentina", "Belgium",
    "Netherlands", "Philippines", "Saudi Arabia", "Sweden", "Hong Kong", "Romania", "Taiwan", "Thailand",
    "Norway", "Ukraine", "Bulgaria", "Chile", "Latvia", "Pakistan", "Vietnam", "Kazakhstan", "Spain",
    "Austria", "Azerbaijan", "France", "Italy", "Morocco", "Qatar", "Serbia", "Costa Rica", "Dominican Republic",
    "Egypt", "Finland", "Georgia", "Jordan", "Korea, Republic of", "New Zealand", "Nigeria", "Peru"
}

def scrape_mastercard_job_counts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Debug mode (Change to True later)
        page = browser.new_page()
        page.goto("https://careers.mastercard.com/us/en/search-results", timeout=60000)

        # ✅ Accept Cookies
        try:
            cookie_button = page.query_selector("#onetrust-accept-btn-handler")
            if cookie_button:
                cookie_button.click()
                page.wait_for_load_state("networkidle")
                print("✅ Accepted cookies.")
        except Exception:
            print("No cookie popup detected.")

        # ✅ Find and expand the "Location" filter category
        try:
            location_category_button = page.query_selector("button#LocationAccordion")
            if location_category_button:
                location_category_button.click()
                page.wait_for_load_state("networkidle")
                print("✅ Expanded 'Location' filter.")
        except Exception:
            print("⚠️ Could not expand 'Location' category. Proceeding without it.")

        # ✅ Extract all job counts (including categories, provinces, and countries)
        raw_job_counts = {}

        # Find all location elements
        location_elements = page.query_selector_all("span.result-text")  # Location names
        count_elements = page.query_selector_all("span.result-jobs-count")  # Job counts

        if not location_elements or not count_elements:
            print("⚠️ No location/job count elements found! Check the selectors.")

        for location, count_element in zip(location_elements, count_elements):
            try:
                # ✅ Extract location name
                location_name = location.inner_text().strip()

                # ✅ Extract job count (using regex to get numbers)
                job_count_text = count_element.inner_text().strip()
                job_count_match = re.search(r"\d+", job_count_text)

                if job_count_match:
                    raw_job_counts[location_name] = int(job_count_match.group())
                else:
                    print(f"⚠️ No valid job count found for: {location_name}")

            except Exception as e:
                print(f"Error extracting job count for {location.inner_text()}: {e}")

        browser.close()

        # ✅ Step 2: Filter for ONLY country-based job counts AFTER extraction
        country_job_counts = {k: v for k, v in raw_job_counts.items() if k in VALID_COUNTRIES}

        return country_job_counts

# Run scraper
job_count_by_location = scrape_mastercard_job_counts()
print(job_count_by_location)  # ✅ Print only jobs per country
