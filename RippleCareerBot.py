import urllib.request
import json
import os.path
import twitter

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen


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


def findMatchingClosingBrace(string, firstPos):

    found = False
    pos = firstPos
    i = 1

    while (not found):

        openPos = string.find('{', pos+1)
        closePos = string.find('}', pos+1)

        if (openPos == -1 and closePos == -1):
            return -1
        elif (openPos == -1 or (openPos != -1 and (openPos > closePos))):
            i-=1
            pos = closePos
        elif (closePos == -1 or closePos != -1 and (openPos < closePos)):
            i+=1
            pos = openPos

        if (i == 0):
            found = True

    return pos


def main():

    # Download HTML
    webUrl = urllib.request.urlopen('https://www.ripple.com/company/careers/all-jobs')
    html = webUrl.read().decode('utf-8')

    # Load jobs json
    dataStart = html.find('{', html.find('ghjb_json'))
    dataEnd = findMatchingClosingBrace(html, dataStart)
    data = json.loads(html[dataStart:dataEnd+1])

    # Keep only relevant data, ordered by department
    departments = {}

    for job in data['jobs']:

        for department in job['departments']:

            if department['name'] not in departments:

                departments[department['name']] = []

            departments[department['name']].append({
                'title': job['title'],
                'absolute_url': job['absolute_url'],
                'id': job['id'],
                'location': job['location'],
                'updated_at': job['updated_at']
            })


    # Check if jobDB exists and load it
    jobDBFileExists = False
    jobDB = []

    if os.path.exists('jobDB.json'):
        with open('jobDB.json') as jsonFile:
            jobDBFileExists = True
            jobDB = json.load(jsonFile)

    # Build new jobIDs data
    jobIDs = []
    newJobs = []

    for department in sorted(departments.keys()):
        for job in departments[department]:
            jobIDs.append(job['id'])

            if jobDBFileExists and job['id'] not in jobDB:
                newJobs.append(job)
                jobDB.append(job['id'])

    # Create a Twitter update for every new job
    for job in newJobs:
        postTwitterUpdate(f"New open position at Ripple:\n\n- {job['title']} ({job['location']['name']})\n\nMore details at: {job['absolute_url']}")

    # Update jobDB
    with open('jobDB.json', 'w') as outfile:
        if jobDBFileExists:
            json.dump(jobDB, outfile, indent=4)
        else:
            json.dump(jobIDs, outfile, indent=4)


if __name__=='__main__':

    main()