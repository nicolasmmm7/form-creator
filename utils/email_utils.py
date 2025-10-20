import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import random

# ====================================================
# ARCHIVO NUEVO: form-creator/utils/email_utils.py
# ====================================================
# FUNCIÓN: Enviar correo con código OTP usando Brevo (Sendinblue)
# ====================================================
# ¿Por qué está aquí?
#Este módulo centraliza la lógica de envío de correos, la cual podría ser utilizada en diferentes  partes del proyecto.
#Entonces, si llegan a tener algun otro coso que puede ser reutilizado en otras partes, lo pueden agregar a esta carpeta pendejos 



def send_otp_email(recipient_email):
    otp_code = str(random.randint(100000, 999999))

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "Tu código OTP de recuperación"
    html_content = f"""
    <html>
      <body>
        <h2>🔐 Recuperación de contraseña</h2>
        <p>Tu código OTP es:</p>
        <h1 style='color:#007bff;'>{otp_code}</h1>
        <p>Este código caduca en 10 minutos.</p>
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
        response = api_instance.send_transac_email(send_smtp_email)
        print("Correo enviado:", response)
        return otp_code
    except ApiException as e:
        print(f"Error al enviar correo: {e}")
        return None
