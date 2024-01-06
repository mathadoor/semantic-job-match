from chalice import Chalice
from opensearchpy import OpenSearch
from opensearchpy.client import IndicesClient
from job_scraper.ApifyScraper import ApiFyActor
import hashlib
import boto3
import logging

import re
import os

app = Chalice(app_name='swifthire-cloud')

_TITLES = [
    "Machine Learning Engineer",
    # "Data Scientist",
    # "MLOps Engineer",
    # "Data Analyst",
    # "Data Engineer"
]

_JOBS_BUCKET_NAME = "swifthire-media-bucket-0"
_JOBS_BUCKET = None
_SCRAPER = None
_OS_CLIENT = None

_NUM_PAGES = 1
_MAX_CONCURRENCY = 10

BASE_QUERIES = {
    "maxPagesPerQuery": _NUM_PAGES,
    "csvFriendlyOutput": False,
    "countryCode": "ca",
    "languageCode": "",
    "maxConcurrency": _MAX_CONCURRENCY,
    "saveHtml": False,
    "saveHtmlToKeyValueStore": False,
    "includeUnfilteredResults": False,
}

_QUERY_URL = "https://www.google.ca/search?q=JOB&ibp=htl;jobs&uule=w+CAIQICIGQ2FuYWRh"

# ELASTIC INPUT
OPENSEARCH_HOST = 'search-swift-hire-dev-jfmldmym4cfbiwdhwmtuqq6ihy.us-west-2.es.amazonaws.com'
INDEX_NAME = 'jobs_harpreet_matharoo'


def gen_queries():
    """
    Helper Function to create a query for each searched title

    The parameters used are set at the top of the page as constants.

    Returns
    -------
        queries: A list of queries for each searched title in Titles
    """
    # PROCESS QUERIES TO CREATE A QUERY FOR EACH SEARCHED TITLE
    processed_titles = ["%20".join(title.split()) for title in _TITLES]
    query_urls = [re.sub("JOB", title, _QUERY_URL) for title in processed_titles]

    # PREPARE QUERIES
    queries = []
    for query_url in query_urls:
        query = BASE_QUERIES.copy()
        query["queries"] = query_url
        queries.append(query)

    return queries


def get_bucket():
    """ Helper Function to create a job postings bucket"""
    global _JOBS_BUCKET
    s3 = boto3.resource("s3")

    # Check if the bucket already exists
    _JOBS_BUCKET = s3.Bucket(_JOBS_BUCKET_NAME)
    if _JOBS_BUCKET.creation_date is None:
        _JOBS_BUCKET = s3.create_bucket(Bucket=_JOBS_BUCKET_NAME)

    return _JOBS_BUCKET


def get_opensearch_client():
    """ Helper Function to create an open search database"""

    global _OS_CLIENT
    if _OS_CLIENT is None:
        auth = (os.environ['opensearch_user'],
                os.environ['opensearch_pwd'])

        _OS_CLIENT = OpenSearch(
            hosts=[{'host': OPENSEARCH_HOST, 'port': 443}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            use_ssl=True,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

        # CREATE INDEX IF IT DOES NOT EXIST
        if not IndicesClient(_OS_CLIENT).exists(index=INDEX_NAME):
            _OS_CLIENT.indices.create(index=INDEX_NAME)

    return _OS_CLIENT


def get_scraper():
    """ Helper Function to create a job scraper"""

    global _SCRAPER
    if _SCRAPER is None:
        _SCRAPER = ApiFyActor(os.environ["brave_apify_token"])

    return _SCRAPER


def scrape_postings():
    """ Helper Function to scrape job postings"""
    responses = []
    for query in gen_queries():
        responses += get_scraper().run(query)

    return responses


def get_uuid(posting, hash_type="SHA256"):
    """ Helper Function to create a unique id for each job posting

    Args:
        posting (dict): A job posting
        hash_type (str): The type of hash to use. The current options are MD5, SHA1, SHA224, SHA256, SHA384, SHA512
    """
    encoded_job = posting["title"].encode()
    if hash_type == "MD5":
        ret = hashlib.md5(encoded_job)
    elif hash_type == "SHA1":
        ret = hashlib.sha1(encoded_job)
    elif hash_type == "SHA224":
        ret = hashlib.sha224(encoded_job)
    elif hash_type == "SHA256":
        ret = hashlib.sha256(encoded_job)
    else:  # SHA512
        ret = hashlib.sha512(encoded_job)

    return ret.hexdigest()


def add_job(posting):
    """ Helper Function to add a job posting to the opensearch database

    Args:
        posting (dict): A job posting
    """
    # CREATE A UNIQUE ID FOR THE JOB POSTING
    uuid = get_uuid(posting)

    # CHECK IF THE JOB POSTING ALREADY EXISTS
    client = get_opensearch_client()
    if client.exists(index=INDEX_NAME, id=uuid):
        return

    # ADD THE JOB POSTING TO THE DATABASE
    client.index(index=INDEX_NAME, id=uuid, body=posting)


# @app.route('/')
# def index():
#     responses = []
#     for query in gen_queries():
#         responses.append(get_scraper().run(query))
#
#     return responses

@app.schedule('rate(4 hour)')
def scheduled_job_scrape():
    """ Function to scrape job postings and add them to the database"""

    # SCRAPE JOB POSTINGS
    responses = scrape_postings()

    # ADD JOB POSTINGS TO DATABASE
    for response in responses:
        for posting in response['googleJobs']:
            add_job(posting)


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
# if __name__ == "__main__":
#     scheduled_job_scrape()
