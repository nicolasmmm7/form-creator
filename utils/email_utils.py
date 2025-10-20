import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import random

# ====================================================
# ARCHIVO NUEVO: form-creator/utils/email_utils.py
# ====================================================
# FUNCIÓN: la función envía el OTP, se genera y guarda en (views.py)
# ====================================================
# ¿Por qué está aquí?
#Este módulo centraliza la lógica de envío de correos, la cual podría ser utilizada en diferentes  partes del proyecto.
#Entonces, si llegan a tener algun otro coso que puede ser reutilizado en otras partes, lo pueden agregar a esta carpeta pendejos 


def send_otp_email(recipient_email, otp_code):
    """
    Envía correo con Brevo. Recibe recipient_email (str) y otp_code (str, 6 dígitos).
    Devuelve True si Brevo aceptó el envío, False si hubo error.
    """
    # Configurar SDK de Brevo con tu API Key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "Tu código OTP de recuperación - FormCreator"
    html_content = f"""
    <html>
      <body>
        <h2>🔐 Recuperación de contraseña</h2>
        <p>Tu código OTP es:</p>
        <h1 style='color:#007bff;'>{otp_code}</h1>
        <p>Este código caduca en 10 minutos.</p>
        <p>Si no solicitaste este cambio, ignora este correo.</p>
      </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": recipient_email}],
        sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
        subject=subject,
        html_content=html_content
    )

    try:
        # Llamada al API de Brevo
        api_response = api_instance.send_transac_email(send_smtp_email)
        # Si llega aquí sin excepción => Brevo aceptó la petición de envío
        # api_response contiene info; suele venir messageId
        print("Brevo response:", getattr(api_response, 'messageId', api_response))
        return True
    except ApiException as e:
        # Aquí logueamos el error (en producción guardarlo en logs)
        print("Error al enviar correo con Brevo:", e)
        return False
