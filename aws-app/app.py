"""
    This file contains the code for the AWS Lambda function that scrapes job
    postings and adds them to the open search database.
"""

# Library Imports
from chalice import Chalice, Cron, IAMAuthorizer, AuthResponse
from opensearchpy import OpenSearch
from opensearchpy.client import IndicesClient
from chalicelib.ApifyScraper import ApiFyActor
import hashlib
from dotenv import load_dotenv
import boto3
import logging
import re
import os
import json

# Global Variables

# load config
file_path = os.path.join(os.path.dirname(__file__), "chalicelib/app_config.json")
with open(file_path, 'r') as f:
    config = json.load(f)

# RESOURCE VARIABLES
_JOBS_BUCKET = None
_SCRAPER = None
_OS_CLIENT = None
_SSM = None

# LOAD SECRETS
load_dotenv()

# Run the app
app = Chalice(app_name=config["INFRA"]["CHALICE"]["APP_NAME"])

authorizer = IAMAuthorizer()


# Helper Functions

def get_ssm_client():
    """ Helper Function to create an AWS SSM Client"""

    global _SSM
    if _SSM is None:
        _SSM = boto3.client("ssm")

    return _SSM


def gen_queries():
    """
    Helper Function to create a query for each searched title

    The parameters used are set at the top of the page as constants.

    Returns
    -------
        queries: A list of queries for each searched title in Titles
    """
    # PROCESS QUERIES TO CREATE A QUERY FOR EACH SEARCHED TITLE
    search_config = config["APIFY"]["SEARCH"]
    processed_titles = ["%20".join(title.split()) for title in search_config["TITLES"]]
    query_urls = [re.sub("JOB", title, search_config["QUERY_URL"]) for title in processed_titles]

    # PREPARE QUERIES
    queries = []
    for query_url in query_urls:
        query = search_config["BASE_QUERIES"].copy()
        query["queries"] = query_url
        queries.append(query)

    return queries


def get_bucket():
    """ Helper Function to create a job postings bucket"""
    global _JOBS_BUCKET
    s3 = boto3.resource("s3")

    # Check if the bucket already exists
    jobs_bucket_name = config["INFRA"]["AWS"]["S3"]["JOBS_BUCKET"]
    _JOBS_BUCKET = s3.Bucket(jobs_bucket_name)
    if _JOBS_BUCKET.creation_date is None:
        _JOBS_BUCKET = s3.create_bucket(Bucket=jobs_bucket_name)

    return _JOBS_BUCKET


def get_opensearch_client():
    """ Helper Function to create an open search database"""

    global _OS_CLIENT
    if _OS_CLIENT is None:
        if "opensearch_user" not in os.environ:
            ssm = get_ssm_client()
            auth = (ssm.get_parameter(Name="opensearch_user", WithDecryption=True)["Parameter"]["Value"].strip(),
                    ssm.get_parameter(Name="opensearch_pwd", WithDecryption=True)["Parameter"]["Value"].strip())
        else:
            auth = (os.environ['opensearch_user'],
                    os.environ['opensearch_pwd'])
        opensearch_config = config["OPENSEARCH"]

        _OS_CLIENT = OpenSearch(
            hosts=[{'host': opensearch_config["HOST"], 'port': 443}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            use_ssl=True,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

        # CREATE INDEX IF IT DOES NOT EXIST
        index_name = opensearch_config["INDEX"]
        if not IndicesClient(_OS_CLIENT).exists(index=index_name):
            _OS_CLIENT.indices.create(index=index_name)

    return _OS_CLIENT


def get_scraper():
    """ Helper Function to create a job scraper"""

    global _SCRAPER
    if _SCRAPER is None:
        if "brave_apify_token" not in os.environ:
            ssm = get_ssm_client()
            apify_token = ssm.get_parameter(Name="brave_apify_token", WithDecryption=True)["Parameter"]["Value"]
        else:
            apify_token = os.environ["brave_apify_token"]
        _SCRAPER = ApiFyActor(apify_token.strip(), config["APIFY"]["ACTOR"])

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
    index_name = config["OPENSEARCH"]["INDEX"]
    if client.exists(index=index_name, id=uuid):
        return

    # ADD THE JOB POSTING TO THE DATABASE
    client.index(index=index_name, id=uuid, body=posting)


# @app.route('/')
# def index():
#     responses = []
#     for query in gen_queries():
#         responses.append(get_scraper().run(query))
#
#     return responses
# Lambda Functions
# @app.schedule(Cron(25, 3, '?', '*', '*', '*').to_string())
def scheduled_job_scrape(context):
    """ Function to scrape job postings and add them to the database"""

    # SCRAPE JOB POSTINGS
    app.log.info("Starting Job Scraping Posting")
    for posting in scrape_jobs():
        add_job(posting)

    app.log.info("Finished posting the jobs to OpenSearch.")


# @app.route('/scrape_jobs', authorizer=authorizer)
#@app.lambda_function(name="scrape_jobs")
def scrape_jobs():
    """ Base Function to scrape jobs and return a list of scraped postings"""

    # SCRAPE JOB POSTINGS
    responses = scrape_postings()
    app.log.info("Finished Job Scraping Postings. Posting them to OpenSearch now.")

    postings = []

    # ADD JOB POSTINGS TO DATABASE
    for response in responses:
        for posting in response['googleJobs']:
            postings.append(posting)

    return postings

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
if __name__ == "__main__":
    scheduled_job_scrape(None)
