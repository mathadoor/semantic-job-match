"""
    The file tests the job scraping functionality of the app.py file.
"""


def test_apify_actor_connection():
    """Tests the connection to the Apify Actor"""
    import app
    scraper = app.get_scraper()
    assert scraper is not None


def test_opensearch_connection():
    """Tests the connection to the opensearch client"""
    import app
    os_client = app.get_opensearch_client()
    assert os_client is not None
