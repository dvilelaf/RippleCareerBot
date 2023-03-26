import re
import requests
from bs4 import BeautifulSoup
import json
import twitter
import os
import time


JOB_ENDPOINT = "https://ripple.com/careers/all-jobs"
JOB_HTML_CLASS = "headline4"
LOCATION_HTML_CLASS = "lg:body1"
JOB_LINK_REGEX = r'"absolute_url":"https:\/\/ripple\.com\/careers\/all-jobs\/job\/(\d+)\?gh_jid='
DB_FILE = "ripple_jobs.json"

twitter_api = None

def tweet_update(message):
    """Post update to Twitter"""
    global twitter_api

    if twitter_api is None:

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        twitter_api = twitter.Api(
            consumer_key = config['credentials']['twitter']['consumer_key'],
            consumer_secret = config['credentials']['twitter']['consumer_secret'],
            access_token_key = config['credentials']['twitter']['access_token_key'],
            access_token_secret = config['credentials']['twitter']['access_token_secret']
        )

    return twitter_api.PostUpdate(message)


def get_job_ids():
    """Search for job ids"""
    page = requests.get(JOB_ENDPOINT)
    matches = re.findall(JOB_LINK_REGEX, page.text, flags=0)
    return set(matches)


def load_db():
    """Read from file"""
    if not os.path.exists(DB_FILE):
        return set()

    with open(DB_FILE, "r") as in_file:
        return set(json.load(in_file))


def write_db(job_ids):
    """Write to file"""
    with open(DB_FILE, "w") as out_file:
        json.dump(job_ids, out_file)


def get_job_data(job_id):
    """Scrape the web and get the job details"""
    page = requests.get(f"{JOB_ENDPOINT}/job/{job_id}/")
    soup = BeautifulSoup(page.content, 'html.parser')

    return {
        "job": soup.find_all(class_=JOB_HTML_CLASS)[0].text.strip(),
        "locations": [location.text.strip() for location in soup.find_all(class_=LOCATION_HTML_CLASS)]
    }


def main():
    """Main"""
    # Get the new job ids
    current_job_ids = get_job_ids()
    previous_job_ids = load_db()
    new_job_ids = current_job_ids.difference(previous_job_ids)

    # Tweet loop
    for job_id in new_job_ids:
        job = get_job_data(job_id)
        print(f"Tweeting job {job_id}")
        tweet_update(f"New open position at Ripple:\n\n- {job['job']} @ {' - '.join(job['locations'])}\n{JOB_ENDPOINT}/job/{job_id}/")
        time.sleep(3)

    # Save all job ids to file
    all_job_ids = previous_job_ids.union(current_job_ids)
    write_db(list(all_job_ids))


if __name__=='__main__':
    main()
