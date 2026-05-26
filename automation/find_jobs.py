import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.options import Options


def scrape_naukri_jobs(keyword, location_name):
    

    # Chrome Options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Open Chrome Browser
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    # Open Website
    driver.get("https://www.naukri.com")


    wait = WebDriverWait(driver, 10)


    ## SEARCH KEYWORD

    keyword_box = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//input[contains(@class,"suggestor-input")]'
            )
        )
    )

    keyword_box.send_keys(keyword)

    time.sleep(2)

    keyword_box.send_keys(Keys.TAB)


    # SEARCH LOCATION

    location_box = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//input[contains(@placeholder,"Enter location")]'
            )
        )
    )

    location_box.click()

    time.sleep(1)

    location_box.send_keys(location_name)

    time.sleep(2)

    location_box.send_keys(Keys.RETURN)

    # Wait for Jobs
    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//a[contains(@class,"title")]'
            )
        )
    )

    # Get All Jobs
    jobs = driver.find_elements(
        By.XPATH,
        '//a[contains(@class,"title")]'
    )

    print("Total Jobs Found:", len(jobs))

    # Store All Jobs
    all_jobs = []


    # LOOP JOBS
    for i in range(min(5, len(jobs))):

        try:

            # Refresh Jobs
            jobs = driver.find_elements(
                By.XPATH,
                '//a[contains(@class,"title")]'
            )

            # Click Job
            jobs[i].click()

            time.sleep(5)

            # Switch Tab
            driver.switch_to.window(
                driver.window_handles[1]
            )

            # Apply Link
            apply_link = driver.current_url

            time.sleep(3)

            # DEFAULT VALUES
            job_title = ""
            company = ""
            location = "India"
            experience = ""
            job_type = []
            work_mode = "Work from Office"
            vacancies = ""
            description = ""
            skills = []
            min_salary = "Not Disclosed"
            max_salary = "Not Disclosed"

            application_deadline = (
                datetime.now() +
                relativedelta(months=1)
            ).strftime("%d/%m/%Y")

            # JOB TITLE

            try:
                job_title = driver.find_element(
                    By.XPATH,
                    '//*[@id="job_header"]/div[1]/div[1]/header/h1'
                ).text

                # if "python" not in job_title.lower():

                #     driver.close()

                #     driver.switch_to.window(
                #         driver.window_handles[0]
                #     )

                #     continue

            except Exception as e:
                print("Job Title Error:", e)


            # COMPANY

            try:
                company = driver.find_element(
                    By.XPATH,
                    '//*[@id="job_header"]/div[1]/div[1]/div/a'
                ).text
            except Exception as e:
                print("Company Error:", e)


            # LOCATION

            try:
                location = driver.find_element(
                    By.CLASS_NAME,
                    'styles_jhc__loc___Du2H'
                ).text

                if location == "":
                    location = "India"

            except Exception as e:
                print("Location Error:", e)

            # EXPERIENCE

            try:
                experience = driver.find_element(
                    By.XPATH,
                    '//*[@id="job_header"]/div[1]/div[2]/div[1]/div[1]/span'
                ).text
            except Exception as e:
                print("Experience Error:", e)


            # JOB TYPE

            try:

                drive_element = driver.find_element(
                    By.CLASS_NAME,
                    "styles_other-details__oEN4O"
                )

                all_divs = drive_element.find_elements(
                    By.CLASS_NAME,
                    "styles_details__Y424J"
                )

                fourth_div = all_divs[3]

                raw_info = fourth_div.get_attribute(
                    "innerHTML"
                )

                final_text = raw_info.split(
                    "<span><span>"
                )[1].split("</span>")[0]

                job_type = [
                    final_text.split(",")[0].strip()
                ]

            except Exception as e:
                print("Job Type Error:", e)

            # WORK MODE

            try:

                element = driver.find_element(
                    By.CLASS_NAME,
                    'styles_jhc__wfhmode__iQwF4'
                )

                text = element.text.strip()

                if text:
                    work_mode = text.lower()

            except:
                pass


            # VACANCIES

            try:
                vacancies = driver.find_element(
                    By.XPATH,
                    '//*[@id="job_header"]/div[2]/div[1]/span[2]/span'
                ).text
            except Exception as e:
                print("Vacancies Error:", e)

   
            # DESCRIPTION
    
            try:

                description = driver.execute_script(
                    "return arguments[0].innerText;",
                    driver.find_element(
                        By.CLASS_NAME,
                        "styles_JDC__dang-inner-html__h0K4t"
                    )
                )

                description = " ".join(
                    description.split()
                )

            except Exception as e:
                print("Description Error:", e)

            # SKILLS

            try:

                skills_div = driver.find_element(
                    By.CLASS_NAME,
                    "styles_key-skill__GIPn_"
                )

                skill_elements = skills_div.find_elements(
                    By.TAG_NAME,
                    "span"
                )

                for skill in skill_elements:

                    text = skill.text.strip()

                    if text:
                        skills.append(text)

            except Exception as e:
                print("Skills Error:", e)


            # SALARY

            try:

                salary = driver.find_element(
                    By.XPATH,
                    '//*[@id="job_header"]/div[1]/div[2]/div[1]/div[2]/span'
                ).text.strip()

                if "-" in salary:

                    salary_range = salary.split()[0]

                    split_salary = salary_range.split("-")

                    if len(split_salary) == 2:

                        min_salary = int(
                            float(split_salary[0]) * 100000
                        )

                        max_salary = int(
                            float(split_salary[1]) * 100000
                        )

            except Exception as e:
                print("Salary Error:", e)


            # JSON DATA

            job_data = {
                "job_title": job_title,
                "company": company,
                "location": location,
                "experience": experience,
                "job_type": job_type,
                "work_mode": work_mode,
                "vacancies": vacancies,
                "application_deadline": application_deadline,
                "description": description,
                "skills": skills,
                "is_urgent": False,
                "is_remote": False,
                "website_apply": apply_link,
                "min_salary": min_salary,
                "max_salary": max_salary
            }

            # Append Data
            all_jobs.append(job_data)

            # Print Job
            print("\n" + "=" * 50)
            print(json.dumps(job_data, indent=4))
            print("=" * 50)

            # Close Job Tab
            driver.close()

            # Switch Back
            driver.switch_to.window(
                driver.window_handles[0]
            )

            time.sleep(3)

        except Exception as e:

            print("Loop Error:", e)

            try:
                driver.close()
                driver.switch_to.window(
                    driver.window_handles[0]
                )
            except:
                pass


    # SAVE JSON

    with open(
        "jobs.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_jobs,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON file created successfully")


    driver.quit()

    return all_jobs



# FUNCTION CALL

# scrape_naukri_jobs(
#     keyword="Python Developer",
#     location_name="Ahmedabad",
# )