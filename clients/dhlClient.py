import requests
import os
import base64
from dotenv import load_dotenv
load_dotenv()

class DhlClient:
    def __init__(self):
        self.dhl_token_url = 'https://api.dhlecs.com/auth/v4/accesstoken'
        self.dhl_client_id = os.getenv("DHL_CLIENT_ID")
        self.dhl_client_secret = os.getenv("DHL_CLIENT_SECRET")

    def get_dhl_access_token(self):
        response = requests.post(self.dhl_token_url, {
            "client_id": self.dhl_client_id,
            "client_secret": self.dhl_client_secret,
            "grant_type": "client_credentials"
        })

        json = response.json()
        
        return json.get("access_token")

    def create_sr_label(self, order_data):
        access_token = self.get_dhl_access_token()
        url = "https://api.dhlecs.com/shipping/v4/label?format=PNG"

        response = requests.post(url, json=order_data, headers={
            "Authorization": f"Bearer {access_token}"
        })

        print(response.text)

        json = response.json()
        labels = json.get("labels")
        label_data = labels[0].get("labelData")
        tracking_number = labels[0].get("dhlPackageId")

        return label_data, tracking_number
