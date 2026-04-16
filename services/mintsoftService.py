from mappers.MintCountryMap import MINT_COUNTRY_MAP
from mappers.StateMapper import STATE_CODE_MAP
from clients.mintsoftClient import MintsoftOrderClient
import base64
from dotenv import load_dotenv
load_dotenv()

class MintsoftService:

    def __init__(self):
        self.client = MintsoftOrderClient()

    def fetch_packed_sr_orders(self):
        packed_orders = self.client.get_orders()
        dhl_sr_orders = []

        dhl_products = {
            "DHL SmartMail Parcel / Parcel Plus Ground":     {"orderedProductId": "GND", "service": "DELCON"},
            "DHL SmartMail Parcel / Parcel Plus Expedited":  {"orderedProductId": "EXP", "service": "DELCON"},
            "DHL SmartMail Parcel Expedited Max":            {"orderedProductId": "PLM", "service": "DELCON"},
            "DHL Parcel Ground With Signature":              {"orderedProductId": "GND", "service": "SIGCON"},
        }

        for order in packed_orders:
            courier_service = order.get("CourierServiceName")
            
            if courier_service in dhl_products:
                order_data = [
                    {
                        "OrderId": order.get("ID")
                    },
                    {
                        "pickup": "5402456", # MUST
                        "distributionCenter": "USDFW1", # MUST
                        "orderedProductId": dhl_products[courier_service]["orderedProductId"], # MUST
                        "consigneeAddress": { # MUST
                            "name": f"{order.get("FirstName") or ''} {order.get('LastName') or ''}",
                            "companyName": order.get("CompanyName"),
                            "address1": order.get("Address1"),
                            "city": order.get("Town"),
                            "state": STATE_CODE_MAP.get(order.get("County"), "Unknown"),
                            "country": MINT_COUNTRY_MAP.get(order.get("CountryId"), "Unknown"),
                            "postalCode": order.get("PostCode"),
                            "email": order.get("Email") or "None",
                            "phone": order.get("Phone")
                        },
                        "returnAddress": {
                            "name": "The 5411 Distribution",
                            "companyName": "The 5411 Distribution",
                            "address1": "1613 Hutton Drive",
                            "address2": "Suite 100",
                            "city": "Carrollton",
                            "state": "TX",
                            "country": "US",
                            "postalCode": "75006",
                        },
                        "packageDetail": { 
                            "packageId": order.get("OrderNumber").replace(" ", "_")[:30], # Limite de 30 caracteres por API
                            "packageDescription": order.get("OrderNumber"),
                            "weight": {
                                "value": order.get("TotalWeight"), # MUST - "TotalWeight"
                                "unitOfMeasure": "LB" # MUST - "LB"
                            },
                            "service": dhl_products[courier_service]["service"], #MUST - Para que se cree con Signature Requirement
                        },
                }]
                dhl_sr_orders.append(order_data)

        print(f'Hay un total de {len(dhl_sr_orders)} ordenes para procesar')
        return dhl_sr_orders
    
    def add_label_and_despatch(self, order_id: int, order_label: str, tracking_number: str):
        order_id = order_id.get("OrderId")
        label_payload = {
            "Base64Data": order_label,
            "FileName": "Shipping Label",
            "Comment": "Test",
            "OrderDocumentTypeId": 0,
            "OrderDocumentPaperSize": "1"
        }

        print(f"Agregando label a la Orden {order_id}")
        self.client.add_order_documents(order_id, label_payload)

        print(f"Label agregada, marcando Orden {order_id} como Despachada")
        self.client.mark_order_despatched(order_id, tracking_number)

        return order_id, order_label

        
            