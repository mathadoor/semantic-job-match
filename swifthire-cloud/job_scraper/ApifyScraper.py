from apify_client import ApifyClient

# APIFY INPUT
ACTOR_ID = "SpK8RxKhIgV6BWOz9"


class ApiFyActor:
    """
    A simple ApiFy Actor wrapper class

    This class is used to make calls the Apify Actor.

    Methods
    -------
        run: Calls the Apify Actor and fetches the scraped data

    """

    def __init__(self, api_token, actor_id=ACTOR_ID):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        self.actor_id = actor_id

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
