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
    <body style="background:#F5FBFA;padding:32px 0;">
  <div style="max-width:420px;margin:auto;background:#fff;border-radius:12px;box-shadow:0 4px 16px #0001;padding:28px 32px;font-family:sans-serif;border:1px solid #D9E7E4;">
    <h2 style="color:#2E3C3A;font-size:1.5rem;margin-bottom:12px;text-align:left;">🔐 Recuperación de contraseña</h2>
    <p style="color:#4C9A92;font-size:1.1rem;">Tu código OTP es:</p>
    <div style="margin:22px 0 18px 0;text-align:center;">
      <span style="display:inline-block;font-size:2.4rem;font-weight:bold;color:#F28C8C;letter-spacing:4px;border-radius:8px;background:#F5FBFA;padding:12px 36px;box-shadow:0 1px 6px #D9E7E475;">{otp_code}</span>
    </div>
    <p style="color:#6C7A78;font-size:1rem;margin-bottom:18px;text-align:center;">Este código caduca en 10 minutos.</p>
    <hr style="border: none; border-top: 1px solid #D9E7E4; margin:24px 0;">
    <p style="color:#6C7A78;font-size:0.98rem;text-align:center;">Si no solicitaste este cambio, puedes ignorar este correo. <br><span style="color:#52C88C;font-size:0.97rem;">Mantén tu cuenta segura.</span></p>
  </div>
</body>
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
