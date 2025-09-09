import requests
import pandas as pd
from io import StringIO


class QueryDB:
    def __init__(self, tinybird_token: str):
        self.headers = {
            "Authorization": f"Bearer {tinybird_token}",
            "Accept": "application/json",
        }
        self.url = "https://api.us-west-2.aws.tinybird.co/v0/sql"

    def query_db(self, sql):
        params = {"q": sql}
        response = requests.get(self.url, headers=self.headers, params=params)
        df = pd.read_csv(StringIO(response.text))
        return df
