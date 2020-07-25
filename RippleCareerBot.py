import requests
from bs4 import BeautifulSoup
import twitter
import os.path
import time
import json

TwitterApi = None


def postTwitterUpdate(message):

    global TwitterApi

    if TwitterApi is None:

        with open('config.json', 'r') as configFile:
            config = json.load(configFile)

        TwitterApi = twitter.Api(consumer_key        = config['credentials']['twitter']['consumer_key'],
                                 consumer_secret     = config['credentials']['twitter']['consumer_secret'],
                                 access_token_key    = config['credentials']['twitter']['access_token_key'],
                                 access_token_secret = config['credentials']['twitter']['access_token_secret'])

    return TwitterApi.PostUpdate(message)


def getOpenPositions():
    page = requests.get('https://boards.greenhouse.io/ripple/')
    soup = BeautifulSoup(page.content, 'html.parser')

    departments = {}

    categories = soup.find_all(class_='level-0')

    for category in categories:

        categoryName = category.find('h2').text.strip()
        departments[categoryName] = []

        jobs = category.find_all(class_='opening')

        for job in jobs:

            jobName = job.find('a').text.strip()
            jobLink = 'https://boards.greenhouse.io' + job.find('a', href=True)['href']
            jobID = jobLink.split('/')[-1]
            jobLocation = job.find(class_='location').text.strip()

            departments[categoryName].append({'name': jobName,
                                              'location': jobLocation,
                                              'link': jobLink,
                                              'id': jobID})
    return departments


def main():

    openPositions = getOpenPositions()
    oldPositionsFileName = 'TweetedRippleOpenPositions.log'

    if os.path.exists(oldPositionsFileName):
        with open(oldPositionsFileName, 'r') as DBfile:
            oldPositionIDs = [int(i) for i in DBfile.readlines()]

        with open(oldPositionsFileName, 'a') as DBfile:
            for department in openPositions.values():
                for job in department:
                    if int(job['id']) not in oldPositionIDs:
                        postTwitterUpdate(f"New open position at Ripple:\n\n- {job['name']} ({job['location']})\n\nMore details at: {job['link']}")
                        DBfile.write(job['id'] + '\n')
                        time.sleep(3)
    else:
        with open(oldPositionsFileName, 'w') as DBfile:
            for department in openPositions.values():
                for job in department:
                    DBfile.write(job['id'] + '\n')


if __name__=='__main__':
    main()