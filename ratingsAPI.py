import json
import requests
from authority import Authority
from google.cloud import storage


class RatingsAPI:

    BASE_URL = "https://ratings.food.gov.uk/"
    END_POINTS = {"authorities": "authorities/json"}
    header = {"x-api-version": 2}

    def get_authority_details(self):
        return requests.get(f'{self.BASE_URL}{self.END_POINTS["authorities"]}', self.header)

    def extract_relevant_authority_details(self):
        authority_details = self.get_authority_details()

        authority_list = []
        for authority_detail in authority_details.json()["ArrayOfWebLocalAuthorityAPI"]["WebLocalAuthorityAPI"]:
            if authority_detail["FileName"] is not None:
                authority = Authority(authority_detail['Name'], authority_detail["FileName"].replace(".xml", ".json"))
                authority_list.append(authority)

        print(authority_list)
        return authority_list

    def write_data_to_cloud_storage(self, authority):

        storage_client = storage.Client.from_service_account_json("credentials.json")
        bucket = storage_client.bucket("hygiene_data")
        blob = bucket.blob(f"{authority.name}.json")

        with blob.open('w') as f:
            f.write(json.dumps(authority.hygiene_ratings_json))
            authority.hygiene_ratings_json = None
            print(authority.name)



    def get_authority_hygiene_data(self):
        authorities = self.extract_relevant_authority_details()
        for authority in authorities:
            authority_ratings = requests.get(authority.file_url)
            authority.hygiene_ratings_json = json.loads(authority_ratings.content)["FHRSEstablishment"]["EstablishmentCollection"]
            self.write_data_to_cloud_storage(authority)
