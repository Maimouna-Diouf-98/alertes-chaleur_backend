from sms_orange import envoyer_sms

# 🔁 Exemple avec un vrai numéro Orange (hors +221 déjà géré dans la fonction)
if __name__ == "__main__":
    numero = "761208067"  # sans +221 ici
    message = "🔥 Alerte chaleur à Dakar ! Restez hydraté."
    success = envoyer_sms(numero, message)
    if success:
        print("✅ SMS envoyé")
    else:
        print("❌ Échec de l’envoi")
