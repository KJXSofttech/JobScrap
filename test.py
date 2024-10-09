from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Path to ChromeDriver
service = webdriver.chrome.service.Service('/usr/local/bin/chromedriver')

# Initialize the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the job listing page
driver.get('https://www.naukri.com/software-developer-jobs-in-mumbai')

# Set up an explicit wait for the elements to load
wait = WebDriverWait(driver, 30)

# Example of clicking "Next" and looping through multiple pages
for i in range(5):  # Let's say we want to navigate through 5 pages
    try:
        # Scroll to the Next button to ensure it's visible
        next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.styles_btn-secondary__2AsIP')))
        driver.execute_script("arguments[0].scrollIntoView();", next_button)

        # Ensure the "Next" button is not disabled before clicking
        if 'disabled' in next_button.get_attribute('class'):
            print(f"Next button is disabled on page {i + 1}, stopping navigation.")
            break

        # Use JavaScript to click the "Next" button
        driver.execute_script("arguments[0].click();", next_button)

        # Wait for the new page content to load (you can adjust this time based on actual loading speed)
        time.sleep(3)

        # Scrape your data from the page (e.g., job titles, company names, etc.)
        job_titles = driver.find_elements(By.CSS_SELECTOR, 'div.listContainer div.jobTupleHeader span.title')
        for job in job_titles:
            print(job.text)

    except Exception as e:
        print(f"Error navigating to page {i + 1}: {str(e)}")
        break  # Exit the loop if there's an issue

# Close the driver
driver.quit()
