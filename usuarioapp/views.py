# usuarioapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from usuarioapp.models import Usuario, Empresa, Perfil
from usuarioapp.serializers import UsuarioSerializer
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from firebase_admin import auth
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings


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
            return Response({
                "message": "Usuario creado correctamente",
                "id": str(usuario.id)
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

        serializer = UsuarioSerializer(usuario)
        return Response({
            "message": "Inicio de sesión exitoso",
            "usuario": serializer.data
        }, status=status.HTTP_200_OK)

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

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Usuario actualizado correctamente",
                "usuario": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        """Actualización parcial (alternativa explícita a PUT)"""
        return self.put(request, id)

    def delete(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        usuario.delete()
        return Response({"message": "Usuario eliminado"}, status=status.HTTP_204_NO_CONTENT)

    
class ResetPasswordAPI(APIView):
    """
    Permite restablecer la contraseña de un usuario mediante su email.
    No requiere autenticación previa (el frontend debe controlar seguridad adicional).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        nueva_clave = request.data.get("nueva_clave")

        # Validar campos
        if not email or not nueva_clave:
            return Response(
                {"error": "Se requieren los campos 'email' y 'nueva_clave'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario
        usuario = Usuario.objects(email=email).first()
        if not usuario:
            return Response(
                {"error": "No existe ningún usuario registrado con ese correo."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Actualizar contraseña
        usuario.clave_hash = nueva_clave
        usuario.save()

        return Response(
            {
                "message": "Contraseña restablecida correctamente.",
                "usuario_id": str(usuario.id)
            },
            status=status.HTTP_200_OK
        )
