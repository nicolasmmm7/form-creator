# usuarioapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from usuarioapp.models import Usuario, Empresa, Perfil, ResetPasswordToken, EmailVerificationToken
from usuarioapp.serializers import UsuarioSerializer
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from firebase_admin import auth
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.conf import settings
import random, string
from django.core.mail import send_mail
from utils.email_utils import send_otp_email, send_verification_email
from django.core.cache import cache  # para guardar temporalmente el OTP

def hello(request):
    """Vista de prueba para verificar que Django funciona"""
    return HttpResponse("<h1>✅ Backend Django funcionando correctamente</h1>")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Vista protegida que requiere autenticación Firebase
    
    ¿Cómo se protege?
    - @permission_classes([IsAuthenticated]) requiere autenticación
    - FirebaseAuthentication (en settings.py) verifica el token
    - Si token válido, request.user contiene el objeto Usuario
    """
    return Response({
        'message': f'Hola {request.user.nombre}',
        'user_data': {
            'email': request.user.email,
            'nombre': request.user.nombre,
            'id': str(request.user.id)
        }
    })


# ==========================================
# ENDPOINT CRÍTICO: Sincronización Firebase → MongoDB
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])  # Público porque el usuario aún no existe en MongoDB
def firebase_auth_sync(request):
    """
    🔥 ENDPOINT CRÍTICO: Sincroniza usuario de Firebase con MongoDB
    
    ¿Cuándo se llama?
    - Cuando usuario inicia sesión con Google (Login.jsx)
    - Cuando usuario se registra con Google (Register.jsx)
    
    ¿Qué hace?
    1. Recibe ID Token de Firebase en el header Authorization
    2. Verifica el token con Firebase Admin SDK
    3. Busca si el usuario ya existe en MongoDB por email
    4. Si existe: actualiza datos (nombre, avatar)
    5. Si NO existe: crea nuevo usuario en MongoDB
    6. Retorna datos completos del usuario para el frontend
    
    FLUJO DETALLADO:
    Frontend → POST /api/auth/firebase/
           ├─ Header: Authorization: Bearer <idToken>
           └─ Body: { nombre: "Juan Pérez" }
    
    Backend → auth.verify_id_token(idToken)  [Firebase Admin SDK]
          → Usuario.objects.get(email=xxx)  [MongoDB]
          → Retorna datos del usuario
    """
    
    print("=" * 80)
    print("🚀 INICIANDO firebase_auth_sync")
    print("=" * 80)
    
    try:
        # ===============================================
        # PASO 1: Extraer y validar el token
        # ===============================================
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f"🔑 Authorization Header: {auth_header[:50]}..." if len(auth_header) > 50 else f"🔑 Authorization Header: {auth_header}")
        
        if not auth_header.startswith('Bearer '):
            print("❌ Error: Falta header Authorization")
            return Response(
                {'error': 'Token de autorización requerido. Header debe ser: Authorization: Bearer <token>'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Extraer token (formato: "Bearer <token>")
        id_token = auth_header.split(' ')[1]
        print(f"🔑 Token extraído (primeros 30 chars): {id_token[:30]}...")
        
        # ===============================================
        # PASO 2: Verificar token con Firebase Admin SDK
        # ===============================================
        print("🔵 Verificando token con Firebase...")
        
        try:
            # ¡ESTE ES EL MOMENTO CLAVE!
            # Firebase Admin SDK verifica:
            # 1. Firma digital del token
            # 2. Fecha de expiración
            # 3. Que el token pertenece a este proyecto
            decoded_token = auth.verify_id_token(id_token)
            
            firebase_uid = decoded_token['uid']
            firebase_email = decoded_token.get('email')
            firebase_picture = decoded_token.get('picture', '')
            
            print(f"✅ Token verificado exitosamente")
            print(f"   ├─ UID: {firebase_uid}")
            print(f"   ├─ Email: {firebase_email}")
            print(f"   └─ Picture: {firebase_picture[:50]}..." if firebase_picture else "   └─ Picture: (no disponible)")
            
        except auth.InvalidIdTokenError as e:
            print(f"❌ Token inválido: {str(e)}")
            return Response(
                {'error': 'Token de Firebase inválido'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except auth.ExpiredIdTokenError:
            print("❌ Token expirado")
            return Response(
                {'error': 'Token expirado. Por favor inicia sesión nuevamente.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(f"❌ Error al verificar token: {str(e)}")
            return Response(
                {'error': f'Error al verificar token: {str(e)}'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Extraer datos adicionales del body
        data = request.data
        firebase_name = data.get('nombre', firebase_email.split('@')[0])
        print(f"📝 Nombre desde request: {firebase_name}")
        
        # ===============================================
        # PASO 3: Buscar o crear usuario en MongoDB
        # ===============================================
        print(f"🔍 Buscando usuario en MongoDB con email: {firebase_email}")
        
        try:
            # CASO 1: Usuario YA EXISTE (login subsecuente)
            usuario = Usuario.objects.get(email=firebase_email)
            print(f"✅ Usuario encontrado en MongoDB: {usuario.nombre} (ID: {usuario.id})")
            
            # Actualizar datos si cambiaron en Google
            updated = False
            
            if usuario.nombre != firebase_name and firebase_name:
                print(f"   ├─ Actualizando nombre: {usuario.nombre} → {firebase_name}")
                usuario.nombre = firebase_name
                updated = True
            
            # Actualizar avatar si cambió
            if usuario.perfil:
                if usuario.perfil.avatar_url != firebase_picture:
                    print(f"   ├─ Actualizando avatar")
                    usuario.perfil.avatar_url = firebase_picture
                    updated = True
            else:
                # Crear perfil si no existe
                print(f"   ├─ Creando perfil nuevo")
                usuario.perfil = Perfil(
                    avatar_url=firebase_picture,
                    idioma='es',
                    timezone='America/Bogota'
                )
                updated = True
            
            if updated:
                usuario.save()
                print("   └─ Cambios guardados en MongoDB")
            else:
                print("   └─ No hay cambios que guardar")
                
        except Usuario.DoesNotExist:
            # CASO 2: Usuario NUEVO (primer registro)
            print(f"📝 Usuario NO existe. Creando nuevo usuario en MongoDB...")
            
            # Crear perfil con datos de Google
            perfil = Perfil(
                avatar_url=firebase_picture,
                idioma='es',
                timezone='America/Bogota'
            )
            print(f"   ├─ Perfil creado")
            
            # Crear empresa por defecto o desde request
            if data.get('empresa'):
                empresa_data = data.get('empresa')
                empresa = Empresa(
                    nombre=empresa_data.get('nombre', 'sin_empresa'),
                    telefono=empresa_data.get('telefono'),
                    nit=empresa_data.get('nit')
                )
                print(f"   ├─ Empresa desde request: {empresa.nombre}")
            else:
                empresa = Empresa(nombre='sin_empresa')
                print(f"   ├─ Empresa por defecto: sin_empresa")
            
            # Crear usuario en MongoDB
            usuario = Usuario(
                nombre=firebase_name,
                email=firebase_email,
                clave_hash=firebase_uid,  # ← IMPORTANTE: UID de Firebase como identificador
                fecha_registro=datetime.utcnow(),
                perfil=perfil,
                empresa=empresa
            )
            usuario.save()
            print(f"   └─ ✅ Usuario creado con ID: {usuario.id}")
        
        # ===============================================
        # PASO 4: Preparar respuesta para el frontend
        # ===============================================
        print("📦 Preparando respuesta...")
        
        user_data = {
            'id': str(usuario.id),
            'nombre': usuario.nombre,
            'email': usuario.email,
            'fecha_registro': usuario.fecha_registro.isoformat(),
            'perfil': {
                'avatar_url': usuario.perfil.avatar_url if usuario.perfil else None,
                'idioma': usuario.perfil.idioma if usuario.perfil else 'es',
                'timezone': usuario.perfil.timezone if usuario.perfil else 'America/Bogota'
            },
            'empresa': {
                'nombre': usuario.empresa.nombre if usuario.empresa else None,
                'telefono': usuario.empresa.telefono if usuario.empresa else None,
                'nit': usuario.empresa.nit if usuario.empresa else None,
            } if usuario.empresa else None,
            'firebase_uid': firebase_uid
        }
        
        print("=" * 80)
        print("✅ SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        
        return Response({
            'success': True,
            'user': user_data,
            'message': 'Usuario sincronizado correctamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ ERROR GENERAL en firebase_auth_sync")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==========================================
# ENDPOINT: Registro y listado de usuarios
# ==========================================
class UsuarioListCreateAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Listar todos los usuarios"""
        usuarios = Usuario.objects()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Crear nuevo usuario (registro tradicional con email/password)"""
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()

            # === Generar y enviar OTP de verificación de email ===
            otp_code = ''.join(random.choices(string.digits, k=6))
            EmailVerificationToken.objects(email=usuario.email).delete()  # borrar tokens anteriores
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            EmailVerificationToken(email=usuario.email, token=otp_code, expires_at=expires_at).save()

            enviado = send_verification_email(usuario.email, otp_code)
            if not enviado:
                print(f"⚠️ No se pudo enviar correo de verificación a {usuario.email}, pero el usuario fue creado.")

            return Response({
                "message": "Usuario creado. Se envió un código de verificación a tu correo.",
                "id": str(usuario.id),
                "email": usuario.email,
                "requiere_verificacion": True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# ENDPOINT: Login tradicional (email/password)
# ==========================================
class UsuarioLoginAPI(APIView):
    """POST: autenticar usuario con email y clave_hash"""

    def post(self, request):
        email = request.data.get("email")
        clave = request.data.get("clave_hash")

        if not email or not clave:
            return Response({"error": "Email y clave son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        usuario = Usuario.objects(email=email, clave_hash=clave).first()
        if not usuario:
            return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_401_UNAUTHORIZED)

        # === Bloquear login si el email no está verificado ===
        # Nota: usuarios antiguos no tienen el campo email_verificado en MongoDB,
        # por lo que solo bloqueamos si el campo EXISTE y es False (usuarios nuevos).
        raw_doc = usuario.to_mongo()
        if 'email_verificado' in raw_doc and not raw_doc['email_verificado']:
            return Response({
                "error": "Tu correo electrónico no ha sido verificado. Revisa tu bandeja de entrada.",
                "codigo": "EMAIL_NO_VERIFICADO",
                "email": usuario.email
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = UsuarioSerializer(usuario)
        return Response({
            "message": "Inicio de sesión exitoso",
            "usuario": serializer.data
        }, status=status.HTTP_200_OK)


# ==========================================
# ENDPOINT: Verificación de email por OTP (POST)
# ==========================================
class EmailVerificationAPI(APIView):
    """
    Flujo de verificación de correo al registrarse:
    1. POST con action="verificar"  -> verifica el código OTP y activa la cuenta
    2. POST con action="reenviar"   -> reenvía un nuevo código OTP al correo
    """
    permission_classes = [AllowAny]

    def post(self, request):
        action = request.data.get("action")

        # --- 1️⃣ Verificar código OTP ---
        if action == "verificar":
            email = request.data.get("email")
            token = request.data.get("token")

            if not email or not token:
                return Response({"error": "Email y código son requeridos."}, status=400)

            # Buscar token
            token_doc = EmailVerificationToken.objects(email=email, token=token).first()
            if not token_doc:
                return Response({"error": "Código inválido."}, status=400)

            # Verificar expiración
            if token_doc.expires_at < datetime.utcnow():
                token_doc.delete()
                return Response({"error": "El código ha expirado. Solicita uno nuevo."}, status=400)

            # Marcar email como verificado
            usuario = Usuario.objects(email=email).first()
            if not usuario:
                return Response({"error": "Usuario no encontrado."}, status=404)

            usuario.email_verificado = True
            usuario.save()

            # Eliminar token usado
            token_doc.delete()

            return Response({"message": "¡Correo verificado exitosamente! Ya puedes iniciar sesión."}, status=200)

        # --- 2️⃣ Reenviar código ---
        elif action == "reenviar":
            email = request.data.get("email")

            if not email:
                return Response({"error": "Debe ingresar un correo."}, status=400)

            usuario = Usuario.objects(email=email).first()
            if not usuario:
                return Response({"error": "No existe un usuario con ese correo."}, status=404)

            if usuario.email_verificado:
                return Response({"message": "Este correo ya está verificado."}, status=200)

            # Generar nuevo token
            otp_code = ''.join(random.choices(string.digits, k=6))
            EmailVerificationToken.objects(email=email).delete()
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            EmailVerificationToken(email=email, token=otp_code, expires_at=expires_at).save()

            enviado = send_verification_email(email, otp_code)
            if not enviado:
                EmailVerificationToken.objects(email=email).delete()
                return Response({"error": "No se pudo enviar el correo. Intenta más tarde."}, status=500)

            return Response({"message": "Nuevo código enviado al correo."}, status=200)

        else:
            return Response({"error": "Acción no válida."}, status=400)

# ==========================================
# ENDPOINT: Detalle de usuario (GET/PUT/DELETE)
# ==========================================
class UsuarioDetailAPI(APIView):

    def get_object(self, id):
        try:
            return Usuario.objects.get(id=ObjectId(id))
        except Usuario.DoesNotExist:
            return None

    def get(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    def put(self, request, id):
        """Permite actualización total o parcial de usuario"""
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # 💡 Importante: `partial=True` permite enviar solo algunos campos
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)

        # DEBUG: ver lo que llega desde el cliente
        print("=== UsuarioDetailAPI.put request.data ===")
        print(request.data)

        try:
            if not serializer.is_valid():
                # devolver errores de validación al frontend
                print("=== Serializer errors ===")
                print(serializer.errors)
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # intentar guardar; catch para devolver detalle si falla
            serializer.save()

            # volver a serializar el objeto actualizado (asegura formato consistente)
            usuario_actualizado = Usuario.objects.get(id=usuario.id)
            resp_serializer = UsuarioSerializer(usuario_actualizado)

            return Response({
                "message": "Usuario actualizado correctamente",
                "usuario": resp_serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": "Error al validar/guardar usuario", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, id):
        """Actualización parcial (alternativa explícita a PUT)"""
        return self.put(request, id)

    def delete(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        usuario.delete()
        return Response({"message": "Usuario eliminado"}, status=status.HTTP_204_NO_CONTENT)


# ==========================================
# ENDPOINT: Cambiar contraseña con verificacion de correo (POST)
# ==========================================
class ResetPasswordAPI(APIView):
    """
    Flujo de recuperación de contraseña con verificación por correo:
    1. POST /reset-password/solicitar/  -> envía un código al email
    2. POST /reset-password/confirmar/  -> verifica el código y cambia la clave
    """
    permission_classes = [AllowAny]

    def post(self, request):
        action = request.data.get("action")

        # --- 1️⃣ Solicitar código ---
        if action == "solicitar":
            email = request.data.get("email")

            if not email:
                return Response({"error": "Debe ingresar un correo."}, status=400)

            usuario = Usuario.objects(email=email).first()
            if not usuario:
                return Response({"error": "No existe un usuario con ese correo."}, status=404)

            # Generar token aleatorio
            token = ''.join(random.choices(string.digits, k=6))

            # Guardar token en BD (borrando anteriores)
            ResetPasswordToken.objects(email=email).delete()
           # ResetPasswordToken(email=email, token=token).save()

             # Guardar token con expiración (10 minutos)
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            ResetPasswordToken(email=email, token=token, expires_at=expires_at).save()

             # Enviar correo usando Brevo: la función devuelve True/False
            enviado = send_otp_email(email, token)
            if not enviado:
                # Si falla el envío, elimina el token y devuelve error
                ResetPasswordToken.objects(email=email).delete()
                return Response({"error": "No se pudo enviar el correo. Intenta más tarde."}, status=500)

            return Response({"message": "Código enviado al correo."}, status=200)

        # --- 2️⃣ Confirmar cambio de contraseña ---
        elif action == "confirmar":
            email = request.data.get("email")
            token = request.data.get("token")
            nueva_clave = request.data.get("nueva_clave")

            if not all([email, token, nueva_clave]):
                return Response({"error": "Faltan campos requeridos."}, status=400)

            # Buscar token
            token_doc = ResetPasswordToken.objects(email=email, token=token).first()
            if not token_doc:
                return Response({"error": "Código inválido."}, status=400)
            
            # Verificar expiración
            if token_doc.expires_at < datetime.utcnow():
                token_doc.delete()
                return Response({"error": "El código ha expirado."}, status=400)

            # Cambiar contraseña
            usuario = Usuario.objects(email=email).first()
            if not usuario:
                return Response({"error": "Usuario no encontrado."}, status=404)

            usuario.clave_hash = nueva_clave
            usuario.save()

            # Eliminar token para evitar reuso
            token_doc.delete()

            return Response({"message": "Contraseña actualizada correctamente."}, status=200)

        else:
            return Response({"error": "Acción no válida."}, status=400)
