import requests
import os
from dotenv import load_dotenv
load_dotenv()

from mappers.MintCountryMap import MINT_COUNTRY_MAP

class MintsoftOrderClient:

    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self):
        self.base_url = "https://api.mintsoft.co.uk/api"
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.api_key = self.authenticate()

    def authenticate(self):
        url = f"{self.base_url}/Auth"
        payload = {
            "Username": self.username,
            "Password": self.password
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Mintsoft Auth Failed: {response.status_code} - {response.text}")

        data = response.json()
        print("Mintsoft Auth Successful — API Key Acquired")
        return data

    def _headers(self):
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def create_order(self, order_payload):
        url = f"{self.BASE_URL}/api/Order"
        headers = self._headers()
        r = requests.put(url, json=order_payload, headers=headers)
        r.raise_for_status()
        return r.json()
    
    def get_orders(self):
        url = f"{self.BASE_URL}/api/Order/List"
        params = {
            "OrderStatusId": 20, # Para las que estan en PACKED
            "Limit": 2,
            "ClientID": 3
        }
        response = requests.get(url, headers=self._headers(), params=params)

        return response.json()

    def get_order_statuses(self):
        url = f'{self.BASE_URL}/api/Order/Statuses'

        response = requests.get(url, headers=self._headers())

        return response.json()
    
    def get_countries(self):
        url = f'{self.BASE_URL}/api/RefData/Countries'

        response = requests.get(url, headers=self._headers())

        return response.json()
    
    def add_order_documents(self, order_id, label_payload):
        url = f'{self.BASE_URL}/api/Order/{order_id}/Documents?PrintWithOrder=false&DocumentTypeId=5'
        print(order_id)
        response = requests.put(url, headers=self._headers(), json = label_payload, timeout = 30)

        print(response.text)
        return response
    
    def mark_order_despatched(self, order_id, tracking_number):
        url = f'{self.BASE_URL}/api/Order/{order_id}/MarkDespatched?TrackingNumber={tracking_number}'

        response = requests.get(url, headers=self._headers(), timeout = 30)

        print(response.text)
        return response

    