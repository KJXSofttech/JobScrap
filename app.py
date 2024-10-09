from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Set up Chrome WebDriver
chrome_driver_path = "/usr/local/bin/chromedriver"  # Adjust the path to your chromedriver
service = Service(chrome_driver_path)
options = Options()

# Add headless mode for running without a GUI
options.add_argument('--incognito')
#options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36")

@app.route('/scrape_jobs', methods=['POST'])
def scrape_jobs():
    input_data = request.json
    job_title = input_data.get('job', 'Data Scientist')  # Default to 'Data Scientist' if not provided
    location = input_data.get('location', 'Mumbai')  # Default to 'Mumbai' if not provided
    experience = input_data.get('experience', '5')  # Default to '5' years if not provided

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Correct URL to filter by job title, location, and experience
        base_url = f"https://www.naukri.com/{job_title.replace(' ', '-')}-jobs-in-{location}?experience={experience}"
        page = 1
        all_jobs_data = []
        job_count = 0  # Counter to stop after 200 jobs

        wait = WebDriverWait(driver, 20)

        while job_count < 40:
            # Modify the URL for pagination
            if page == 1:
                page_url = base_url
            else:
                page_url = f"https://www.naukri.com/{job_title.replace(' ', '-')}-jobs-in-{location}-{page}?experience={experience}"

            driver.get(page_url)

            # Wait for the job listings to load
            try:
                wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.srp-jobtuple-wrapper'))
                )
            except Exception as e:
                print(f"No job listings found on page {page}. Stopping pagination.")
                break

            # Find all job listings
            jobs = driver.find_elements(By.CSS_SELECTOR, 'div.srp-jobtuple-wrapper')

            # If no jobs are found, break the loop
            if not jobs:
                print(f"No more jobs found on page {page}. Ending.")
                break

            job_data_list = []

            for job in jobs:
                try:
                    if job_count >= 200:
                        break  # Stop after scraping 200 jobs

                    # Extract basic details from the job card
                    job_title = job.find_element(By.CSS_SELECTOR, 'a.title').text
                    company_name = job.find_element(By.CSS_SELECTOR, 'a.comp-name').text

                    try:
                        rating_element = job.find_elements(By.CSS_SELECTOR, 'a.rating')
                        ratings = rating_element[0].text if rating_element else "No rating"
                    except:
                        ratings = "No rating"

                    try:
                        experience = job.find_element(By.CSS_SELECTOR, 'span.expwdth').text
                    except:
                        experience = "Not specified"

                    try:
                        salary = job.find_element(By.CSS_SELECTOR, 'span.sal').text
                    except:
                        salary = "Not disclosed"

                    try:
                        location = job.find_element(By.CSS_SELECTOR, 'span.locWdth').text
                    except:
                        location = "Location not specified"

                    try:
                        job_description_summary = job.find_element(By.CSS_SELECTOR, 'span.job-desc').text
                    except:
                        job_description_summary = "No description"

                    skills_elements = job.find_elements(By.CSS_SELECTOR, 'ul.tags-gt li')
                    skills = [skill.text for skill in skills_elements] if skills_elements else []

                    posting_date = job.find_element(By.CSS_SELECTOR, 'span.job-post-day').text
                    job_link = job.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')

                    # Open job detail page in a new tab to scrape more details
                    driver.execute_script("window.open(arguments[0], '_blank');", job_link)
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(3)  # Wait for the detailed job page to load

                    # Scrape additional details using WebDriverWait and CSS Selectors
                    try:
                        role = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.styles_details__Y424J span a'))).text
                    except:
                        role = "Not available"

                    try:
                        industry_type = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.styles_details__Y424J:nth-child(2) span a'))).text
                    except:
                        industry_type = "Not available"

                    try:
                        department = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.styles_details__Y424J:nth-child(3) span a'))).text
                    except:
                        department = "Not available"

                    try:
                        employment_type = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.styles_details__Y424J:nth-child(4) span'))).text
                    except:
                        employment_type = "Not available"

                    try:
                        role_category = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.styles_details__Y424J:nth-child(5) span'))).text
                    except:
                        role_category = "Not available"

                    try:
                        education_ug = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[@class='styles_details__Y424J'][1]/span"))).text
                    except:
                        education_ug = "Not available"

                    try:
                        education_pg = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[@class='styles_details__Y424J'][2]/span"))).text
                    except:
                        education_pg = "Not available"

                    try:
                        about_company = wait.until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'section.styles_about-company__lOsvW div.styles_detail__U2rw4'))).text
                    except:
                        about_company = "Not available"

                    # Extract detailed job description
                    try:
                        job_desc_section = driver.find_element(By.CSS_SELECTOR, 'div.styles_JDC__dang-inner-html__h0K4t').text
                    except:
                        job_desc_section = "Not available"

                    # Create job dictionary with all details
                    job_data = {
                        "Job Title": job_title,
                        "Company Name": company_name,
                        "Ratings": ratings,
                        "Experience": experience,
                        "Salary": salary,
                        "Location": location,
                        "Job Description (Summary)": job_description_summary,
                        "Skills": skills,
                        "Posting Date": posting_date,
                        "Job Link": job_link,
                        "Job Details": {
                            "Job Description": job_desc_section,
                            "Role": role,
                            "Industry Type": industry_type,
                            "Department": department,
                            "Employment Type": employment_type,
                            "Role Category": role_category,
                            "Education": {
                                "UG": education_ug,
                                "PG": education_pg
                            },
                            "About Company": about_company,
                        }
                    }

                    # Add the job data to the list
                    job_data_list.append(job_data)
                    job_count += 1  # Increment the job count

                    # Close the detailed job tab and switch back to the listing tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)

                except Exception as e:
                    print(f"Error extracting data for a job: {e}")

            # Add the current page's jobs to the all_jobs_data list
            all_jobs_data.extend(job_data_list)

            print(f"Scraped page {page} successfully.")
            page += 1
            time.sleep(2)  # Optional: add a short delay between page loads

        return jsonify(all_jobs_data)

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)