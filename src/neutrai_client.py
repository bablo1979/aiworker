import requests
from config import Config
import time

class NeutraAIClient:
    def __init__(self, cfg: Config):
        self.config = cfg
        self.access_token = None
        self.expires_at = 0  # timestamp unix

    def auth(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        host = self.config.get_required('KEYCLOAK_URI')
        client_id = self.config.get_required('NEUTRAI_CLIENT_ID')
        client_secret = self.config.get_required('NEUTRAI_SECRET')

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        response = requests.post(host, data=data, headers=headers)
        response.raise_for_status()
        payload = response.json()

        self.access_token = payload["access_token"]
        self.expires_at = time.time() + payload["expires_in"] - 5

    def get_token(self):
        if self.access_token is None or time.time() >= self.expires_at:
            self.auth()
        return self.access_token


    def get_dispute_info(self,**kwargs):
        token = self.get_token()
        headers = kwargs.pop("headers", {})
        dispute_uuid = kwargs.pop("dispute_uuid", None)
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {token}"
        method = "GET"
        base_url = self.config.get_required('NEUTRAI_URI')
        url = f"{base_url}/api/dispute/{dispute_uuid}"
        response = requests.request(method, url, headers=headers, **kwargs)
        return response.json()

    def store_questions(self, **kwargs):
        token = self.get_token()
        headers = kwargs.pop("headers", {})
        dispute_uuid = kwargs.pop("dispute_uuid", None)
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {token}"
        method = "POST"
        base_url = self.config.get_required('NEUTRAI_URI')
        url = f"{base_url}/api/dispute/{dispute_uuid}/questions"
        data = kwargs.pop("questions", None)
        data['owner_uuid'] = kwargs.pop("owner_uuid", None)
        response = requests.request(method, url, headers=headers, json=data, **kwargs)
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())
        return response.status_code==200

