import requests
import pandas as pd
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, HEADERS, BASE_URL, OUTPUT_FILE, MAX_PAGES
import time


jobs = []


def is_hr_job(text):
    text = text.lower()
    return any(keyword in text for keyword in JOB_KEYWORDS)


def crawl_page(page):
    url = f"{BASE_URL}/jobs?page={page}"
    print(f"Crawling: {url}")

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # job_cards = soup.select("div.col-span-1.bg-white.rounded-lg.border")
    # print("Job cards found:", len(job_cards))
    # print(job_cards[0].prettify())

    job_cards = soup.find_all("div", attrs={"data-cy": "listing-cards-components"})

    for job in job_cards:
        title_tag = job.find("a", attrs={"data-cy": "listing-title-link"})
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag["href"]

        company_tag = job.select_one("p.text-blue-700")
        company = company_tag.get_text(strip=True) if company_tag else ""

        category_tag = job.select_one("p.text-gray-500")
        category = category_tag.get_text(strip=True) if category_tag else ""

        posted_tag = job.select_one("div.border-t p.text-gray-700")
        posted = posted_tag.get_text(strip=True) if posted_tag else ""

        summary_candidates = job.select("p.text-gray-700")
        summary = summary_candidates[-1].get_text(strip=True) if len(summary_candidates) > 1 else ""

        tags = job.select("div.text-gray-500 span")
        location = tags[0].get_text(strip=True) if len(tags) > 0 else ""
        job_type = tags[1].get_text(strip=True) if len(tags) > 1 else ""

        search_text = f"{title} {category} {summary}"

        if is_hr_job(search_text):
            jobs.append({
                "Title": title,
                "Company": company,
                "Category": category,
                "Location": location,
                "Job Type": job_type,
                "Posted": posted,
                "Summary": summary,
                "Link": link
            })


def save_to_excel():
    df = pd.DataFrame(jobs)
    df.drop_duplicates(subset=["Link"], inplace=True)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} HR jobs to {OUTPUT_FILE}")


if __name__ == "__main__":
    for page in range(1, MAX_PAGES + 1):
        crawl_page(page)
        time.sleep(3)  # polite crawling

    save_to_excel()