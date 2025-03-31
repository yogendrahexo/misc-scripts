from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random
import os

def scrape_page(driver, page_num):
    jobs_on_page = []
    
    try:
        url = f'https://www.upwork.com/nx/search/jobs/?q=machine%20learning&page={page_num}'
        print(f"\nScraping page {page_num}...")
        
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        
        # Scroll down a bit to simulate human reading
        for _ in range(3):
            driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
            time.sleep(random.uniform(1, 2))
        
        # Wait for job cards to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-test="JobTile"]'))
            )
        except:
            print(f"No jobs found on page {page_num}, might have reached the end or encountered a CAPTCHA")
            print("Please solve any CAPTCHA manually if present, then press Enter to continue...")
            input()
            
            # Check again after user intervention
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'article[data-test="JobTile"]')
            if not job_cards:
                print("Still no jobs found after waiting. Moving on...")
                return []
        
        # Find all job cards
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'article[data-test="JobTile"]')
        print(f"Found {len(job_cards)} job cards on page {page_num}")
        
        if not job_cards:
            print(f"No jobs found on page {page_num}, might be at the end")
            return []
        
        for card in job_cards:
            try:
                # Scroll to the job card to ensure it's in view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                time.sleep(random.uniform(0.5, 1))
                
                # Extract job details
                title_element = card.find_element(By.CSS_SELECTOR, 'h2.job-tile-title a')
                title = title_element.text
                job_url = title_element.get_attribute('href')
                
                # Posted time
                try:
                    posted = card.find_element(By.CSS_SELECTOR, 'small[data-test="job-pubilshed-date"] span:last-child').text
                except:
                    posted = 'N/A'
                
                # Budget information
                try:
                    budget_type = card.find_element(By.CSS_SELECTOR, 'li[data-test="job-type-label"] strong').text
                except:
                    budget_type = 'N/A'
                
                try:
                    est_budget = card.find_element(By.CSS_SELECTOR, 'li[data-test="is-fixed-price"] strong:last-child').text
                except:
                    est_budget = budget_type
                
                budget_info = {
                    'type': 'Hourly' if 'Hourly' in budget_type else 'Fixed-price' if 'Fixed' in budget_type else 'Unknown',
                    'amount': est_budget
                }
                
                # Experience level
                try:
                    experience = card.find_element(By.CSS_SELECTOR, 'li[data-test="experience-level"] strong').text
                except:
                    experience = 'N/A'
                
                # Duration
                try:
                    duration = card.find_element(By.CSS_SELECTOR, 'li[data-test="duration-label"] strong:last-child').text
                except:
                    duration = 'N/A'
                
                # Description
                try:
                    description = card.find_element(By.CSS_SELECTOR, 'div[data-test="UpCLineClamp JobDescription"] .air3-line-clamp p.mb-0.text-body-sm').text
                except:
                    description = 'N/A'
                
                # Skills
                try:
                    skill_elements = card.find_elements(By.CSS_SELECTOR, 'div[data-test="TokenClamp JobAttrs"] .air3-token-wrap span')
                    skills = [skill.text for skill in skill_elements]
                except:
                    skills = []
                
                job_data = {
                    'title': title,
                    'url': job_url,
                    'posted': posted,
                    'budget': budget_info,
                    'experience_level': experience,
                    'duration': duration,
                    'description': description,
                    'skills': skills,
                    'page_number': page_num
                }
                
                jobs_on_page.append(job_data)
                print(f"Extracted job: {job_data['title']} - Budget: {budget_info['type']} {budget_info['amount']}")
                
                # Add small delay between processing cards
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                print(f"Error extracting job details: {e}")
                continue
        
        return jobs_on_page
        
    except Exception as e:
        print(f"Error on page {page_num}: {str(e)}")
        return jobs_on_page

def scrape_upwork(driver, num_pages=20):
    all_jobs = []
    
    # Try to load existing jobs if any
    try:
        with open('upwork_jobs.json', 'r', encoding='utf-8') as f:
            all_jobs = json.load(f)
            print(f"Loaded {len(all_jobs)} existing jobs")
    except FileNotFoundError:
        print("Starting fresh scrape")
    
    for page_num in range(1, num_pages + 1):
        # Random delay between pages
        if page_num > 1:
            delay = random.uniform(8, 15)
            print(f"Waiting {delay:.2f} seconds before next page...")
            time.sleep(delay)
        
        # Scrape the page
        jobs_on_page = scrape_page(driver, page_num)
        
        if not jobs_on_page:
            print("No more jobs found, stopping")
            break
        
        all_jobs.extend(jobs_on_page)
        
        # Save progress after each page
        with open('upwork_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)
        print(f"Progress saved! Total jobs so far: {len(all_jobs)}")
    
    print(f"\nFinished! Total jobs collected: {len(all_jobs)}")
    return all_jobs
import math
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Upwork jobs.")
    parser.add_argument('n', type=int, help='Number of jobs to aim for (will scrape n/10 pages).')
    args = parser.parse_args()

    num_jobs_target = args.n
    num_pages_to_scrape = math.ceil(num_jobs_target / 10) # Each page has roughly 10 jobs

    print(f"Starting Upwork job scraper using your existing browser profile...")
    print(f"Aiming for approximately {num_jobs_target} jobs, scraping {num_pages_to_scrape} pages.")

    # Set up options to use your existing Brave profile
    options = Options()
    options.binary_location = "/usr/bin/brave-browser"  # Path to Brave
    # Make user-data-dir path relative or configurable if needed
    options.add_argument("--user-data-dir=/home/yogendramanawat/.config/BraveSoftware/Brave-Browser")  # Path to your profile
    options.add_argument("--profile-directory=Default")  # Or the name of your profile folder
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Start the browser
    driver = None # Initialize driver to None
    try:
        driver = webdriver.Chrome(options=options)
        jobs = scrape_upwork(driver, num_pages=num_pages_to_scrape)
        if jobs:
            print("\nSample of first job:")
            print(json.dumps(jobs[0], indent=2))
            print(f"\nTotal jobs collected: {len(jobs)}")
        else:
            print("\nNo jobs were collected.")
    except Exception as e:
        print(f"\nAn error occurred during scraping: {e}")
    finally:
        if driver:
            print("\nScraping process finished or interrupted. Press Enter to close the browser...")
            input()
            driver.quit()
        else:
            print("\nBrowser could not be started.")
