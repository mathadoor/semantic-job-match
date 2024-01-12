from apify_client import ApifyClient
import json

# APIFY INPUT
# with open('./app_config.json', 'r') as f:
#     config = json.load(f)
#
# ACTOR_ID = config["APIFY"]["ACTOR"]["ID"]


class ApiFyActor:
    """
    A simple ApiFy Actor wrapper class

    This class is used to make calls the Apify Actor.

    Methods
    -------
        run: Calls the Apify Actor and fetches the scraped data

    """

    def __init__(self, api_token, config):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        self.actor_id = config["ID"]

    def run(self, params):
        """
        Calls the Apify Actor and fetches the scraped data

        Args
        ----
            params (dict): A dictionary containing the query parameters

        Returns
        -------
            items: A list of scraped job postings

        """
        run = self.client.actor(self.actor_id).call(run_input=params)
        items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
        return items
