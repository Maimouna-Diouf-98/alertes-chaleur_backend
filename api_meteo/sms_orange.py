# api_meteo/sms_twilio.py

from twilio.rest import Client
import os

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_TOKEN)

def envoyer_sms(numero, message):
    try:
        # Nettoyage du numéro (on suppose un numéro local de 9 chiffres)
        if numero.startswith("+"):
            to_number = numero
        else:
            to_number = f"+221{numero[-9:]}"  # Numéro Sénégal format international

        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=to_number
        )
        print("[SMS Twilio envoyé]:", sms.sid)
        return True
    except Exception as e:
        print("[ERREUR Twilio]", e)
        return False
