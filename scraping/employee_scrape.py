import sqlite3
from playwright.sync_api import sync_playwright
import re
import datetime  # To track timestamps

# ✅ List of valid countries (for filtering)
VALID_COUNTRIES = {
    "India", "United States of America", "Ireland", "Canada", "Portugal", "United Kingdom", "Poland", "Colombia",
    "Mexico", "Brazil", "Japan", "Malaysia", "Australia", "Singapore", "Czechia", "Türkiye", "Hungary", "China",
    "Germany", "Indonesia", "Israel", "Greece", "United Arab Emirates", "Denmark", "Argentina", "Belgium",
    "Netherlands", "Philippines", "Saudi Arabia", "Sweden", "Hong Kong", "Romania", "Taiwan", "Thailand",
    "Norway", "Ukraine", "Bulgaria", "Chile", "Latvia", "Pakistan", "Vietnam", "Kazakhstan", "Spain",
    "Austria", "Azerbaijan", "France", "Italy", "Morocco", "Qatar", "Serbia", "Costa Rica", "Dominican Republic",
    "Egypt", "Finland", "Georgia", "Jordan", "Korea, Republic of", "New Zealand", "Nigeria", "Peru"
}

# ✅ Step 1: Set up SQLite Database
def setup_database():
    conn = sqlite3.connect("mastercard_jobs.db")
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            job_count INTEGER,
            timestamp TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database & Table Ready.")

# ✅ Step 2: Scrape and Store Data in Database
def scrape_and_store_mastercard_job_counts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Change to False for debugging
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

        # ✅ Expand 'Location' filter if needed
        try:
            location_category_button = page.query_selector("button#LocationAccordion")
            if location_category_button:
                location_category_button.click()
                page.wait_for_load_state("networkidle")
                print("✅ Expanded 'Location' filter.")
        except Exception:
            print("⚠️ Could not expand 'Location' category. Proceeding without it.")

        # ✅ Extract all job counts (including categories, cities, etc.)
        raw_job_counts = {}

        # Find location elements
        location_elements = page.query_selector_all("span.result-text")  # Location names
        count_elements = page.query_selector_all("span.result-jobs-count")  # Job counts

        if not location_elements or not count_elements:
            print("⚠️ No location/job count elements found! Check the selectors.")

        for location, count_element in zip(location_elements, count_elements):
            try:
                location_name = location.inner_text().strip()
                job_count_text = count_element.inner_text().strip()
                job_count_match = re.search(r"\d+", job_count_text)

                if job_count_match:
                    raw_job_counts[location_name] = int(job_count_match.group())
                else:
                    print(f"⚠️ No valid job count found for: {location_name}")

            except Exception as e:
                print(f"Error extracting job count for {location.inner_text()}: {e}")

        browser.close()

        # ✅ Step 3: Filter for ONLY country-based job counts AFTER extraction
        country_job_counts = {k: v for k, v in raw_job_counts.items() if k in VALID_COUNTRIES}

        # ✅ Store Data in SQLite Database
        store_data_in_database(country_job_counts)

# ✅ Step 4: Insert Scraped Data into SQLite
def store_data_in_database(data):
    conn = sqlite3.connect("mastercard_jobs.db")
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for country, job_count in data.items():
        cursor.execute("INSERT INTO job_counts (country, job_count, timestamp) VALUES (?, ?, ?)", 
                       (country, job_count, timestamp))

    conn.commit()
    conn.close()
    print("✅ Data Stored in Database.")

# ✅ Step 5: Query Data (Optional)
def fetch_latest_job_counts():
    conn = sqlite3.connect("mastercard_jobs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT country, job_count, timestamp FROM job_counts ORDER BY timestamp DESC LIMIT 10")
    results = cursor.fetchall()

    conn.close()
    return results

# ✅ Run Everything
setup_database()
scrape_and_store_mastercard_job_counts()

# ✅ Print Latest Job Counts
latest_data = fetch_latest_job_counts()
print("\n📊 Latest Job Data:")
for row in latest_data:
    print(row)



