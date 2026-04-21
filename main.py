import os
import requests
import json
from clients.dhlClient import DhlClient
from services.mintsoftService import MintsoftService
from services.mailService import MailService
from datetime import datetime

dhl_client = DhlClient()
mint_service = MintsoftService()
mail_service = MailService()


try:
    # Extraigo ordenes en estado packed que tienen Signature Requirement y preparo la informacion
    packed_orders_withsr = mint_service.fetch_packed_sr_orders()

    if packed_orders_withsr:

        # Recorro el array de ordenes
        for order in packed_orders_withsr: # Cada Orden tiene ID en 0 y la info para DHL en 1
            # Consulta a la API de DHL para crear las labels
            print(f'Creando Label para la orden {order[0].get("OrderId")}')
            label_and_tracking = dhl_client.create_label(order[1])
            order_label = label_and_tracking[0]
            
            tracking_number = label_and_tracking[1]

            validation = mint_service.add_label_and_despatch(order[0], order_label, tracking_number)

            # Si tiene exito agregar la label y marcar la orden como despatched, enviar el mail
            if validation:
                client_name = order[1].get("consigneeAddress", {}).get("name")
                order_number = order[1].get("packageDetail", []).get("packageId")
                
                mail_service.send_label_email(client_name, order_number, tracking_number, order_label)

    
    else:
        print(f"Actulamente no hay ordenes para procesar - Hora actual: {datetime.now()}")

except Exception as e:
    print(e)