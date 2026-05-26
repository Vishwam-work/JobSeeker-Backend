from celery import shared_task
from automation.find_jobs import scrape_naukri_jobs

@shared_task
def fetch_jobs_task(keyword, location_name):

    jobs = scrape_naukri_jobs(keyword, location_name)

    return jobs