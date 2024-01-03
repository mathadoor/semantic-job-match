from apify_client import ApifyClient
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import os
import re

# ENVIRONMENT VARIABLES
APIFY_TOKEN = os.environ["apify_token"]
ELASTIC_PASSWORD = os.environ["ELASTIC_PASSWORD"]

# APIFY INPUT
ACTOR_ID = "SpK8RxKhIgV6BWOz9"

TITLES = [
    "Machine Learning Engineer",
    "Data Scientist",
    "MLOps Engineer",
    "Data Analyst",
    "Data Engineer"
]

NUM_PAGES = 1
MAX_CONCURRENCY = 10

BASE_QUERIES = {
    "maxPagesPerQuery": NUM_PAGES,
    "csvFriendlyOutput": False,
    "countryCode": "ca",
    "languageCode": "",
    "maxConcurrency": MAX_CONCURRENCY,
    "saveHtml": False,
    "saveHtmlToKeyValueStore": False,
    "includeUnfilteredResults": False,
}
QUERY_URL = "https://www.google.ca/search?q=JOB&ibp=htl;jobs&uule=w+CAIQICIGQ2FuYWRh"

# ELASTIC INPUT
ELASTIC_HOST = 'http://localhost:9200'
INDEX_NAME = 'jobs'

# PROCESS QUERIES TO CREATE A QUERY FOR EACH SEARCHED TITLE
processed_titles = ["%20".join(title.split()) for title in TITLES]
query_urls = [re.sub("JOB", title, QUERY_URL) for title in processed_titles]

# PREPARE QUERIES
queries = []
for query_url in query_urls:
    query = BASE_QUERIES.copy()
    query["queries"] = query_url
    queries.append(query)

# Initialize the ApifyClient with your API token
client = ApifyClient(APIFY_TOKEN)

items = []
# Run the Actor and wait for it to finish
for query in queries:
    run = client.actor(ACTOR_ID).call(run_input=query)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

# Initialize the Elastic Search Client and Add the Scraped Records to the Index
es = Elasticsearch(ELASTIC_HOST, basic_auth=("elastic", ELASTIC_PASSWORD))

# CREATE an Index to Store the Jobs
if not IndicesClient(es).exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)

start_id = 1
for item in items:
    for _, job_data in enumerate(item['googleJobs']):
        es.index(
            index=INDEX_NAME,
            id=str(start_id),
            document=job_data,
        )
        start_id += 1
