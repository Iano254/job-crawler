import requests
import pandas as pd
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, USER_AGENT, OUTPUT_FILE

jobs = []

def keyword_match(text):
    text = text.lower()
    return any(keyword in text for keyword in JOB_KEYWORDS)


def crawl_job_site(url):
    print(f"Crawling: {url}")

    response = requests.get(url, headers=USER_AGENT, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ⚠️ THIS PART IS SITE-SPECIFIC
    listings = soup.select(".job-listing")  # example selector

    for job in listings:
        title = job.select_one(".job-title").get_text(strip=True)
        company = job.select_one(".company").get_text(strip=True)
        location = job.select_one(".location").get_text(strip=True)
        link = job.select_one("a")["href"]

        description = job.get_text(" ", strip=True)

        if keyword_match(title + " " + description):
            jobs.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Link": link
            })


def save_to_excel():
    df = pd.DataFrame(jobs)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} jobs to {OUTPUT_FILE}")


if _name_ == "_main_":
    job_sites = [
        "https://example.com/jobs",
        # add more sites here
    ]

    for site in job_sites:
        crawl_job_site(site)

    save_to_excel()