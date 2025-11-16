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


# 🆕 NUEVA FUNCIÓN PARA ENVIAR COPIA DE RESPUESTAS
def send_form_responses_copy(recipient_email, form_title, respuestas_list):
    """
    Envía una copia de las respuestas del formulario al correo del usuario.
    
    Args:
        recipient_email (str): Email del destinatario
        form_title (str): Título del formulario
        respuestas_list (list): Lista de diccionarios con formato:
            [{"pregunta": "¿Pregunta?", "respuesta": "Respuesta del usuario"}, ...]
    
    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Construir el HTML de las respuestas
    respuestas_html = ""
    for idx, item in enumerate(respuestas_list, 1):
        pregunta = item.get("pregunta", f"Pregunta {idx}")
        respuesta = item.get("respuesta", "Sin respuesta")
        
        respuestas_html += f"""
        <div style="background:#F5FBFA;padding:16px;border-radius:8px;margin-bottom:16px;border-left:4px solid #4C9A92;">
            <p style="color:#2E3C3A;font-weight:600;margin:0 0 8px 0;font-size:1.05rem;">{idx}. {pregunta}</p>
            <p style="color:#6C7A78;margin:0;font-size:1rem;line-height:1.5;">{respuesta}</p>
        </div>
        """

    subject = f"📋 Copia de tus respuestas: {form_title}"
    html_content = f"""
    <body style="background:#F5FBFA;padding:32px 0;">
        <div style="max-width:600px;margin:auto;background:#fff;border-radius:12px;box-shadow:0 4px 16px #0001;padding:28px 32px;font-family:sans-serif;border:1px solid #D9E7E4;">
            <h2 style="color:#2E3C3A;font-size:1.6rem;margin-bottom:8px;text-align:left;">📋 Copia de tus respuestas</h2>
            <p style="color:#4C9A92;font-size:1.1rem;margin-bottom:24px;">Formulario: <strong>{form_title}</strong></p>
            
            <div style="margin:24px 0;">
                {respuestas_html}
            </div>

            <hr style="border: none; border-top: 1px solid #D9E7E4; margin:24px 0;">
            <p style="color:#6C7A78;font-size:0.95rem;text-align:center;">
                Gracias por completar este formulario. Esta es una copia automática de tus respuestas.
            </p>
            <p style="color:#52C88C;font-size:0.9rem;text-align:center;margin-top:8px;">
                FormCreator - Sistema de gestión de formularios
            </p>
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
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("✅ Copia de respuestas enviada. MessageId:", getattr(api_response, 'messageId', api_response))
        return True
    except ApiException as e:
        print("❌ Error al enviar copia de respuestas con Brevo:", e)
        return False