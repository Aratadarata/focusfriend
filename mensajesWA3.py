# mensajes whatsapp copy 3

import requests


def register_message(numero, payload):
    api_url = "https://script.google.com/macros/s/AKfycbyoBhxuklU5D3LTguTcYAS85klwFINHxxd-FroauC4CmFVvS0ua/exec"
    token = "GA230509132842"
    payload["token_qr"] = token
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print(f"Message sent to {numero}")
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


token = "GA230509132842"
numero = "5215520945995"
payload = {"op": "registermessage", "token_qr": token, "mensajes": [
    {"numero": numero, "mensaje": "pruebas desde python 26072022"}]}

register_message(numero, payload)
