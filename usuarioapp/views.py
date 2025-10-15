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
from firebase_auth.authentication import auth
from django.conf import settings
import firebase_admin
from firebase_admin import credentials


def hello(request):
    return HttpResponse("<h1>Hello World</h1>")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Vista protegida que requiere autenticación Firebase
    """
    return Response({
        'message': f'Hola {request.user.nombre}',
        'user_data': {
            'email': request.user.email,
            'nombre': request.user.nombre
        }
    })

# ==========================================
# ENDPOINT: Sincronización Firebase → MongoDB
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])  # Público porque aún no existe el usuario
def firebase_auth_sync(request):
    print("🚀 Entramos en firebase_auth_sync")

    """
    Endpoint crítico: Sincroniza usuario de Firebase con MongoDB
    
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
    """
    try:
        # ===============================================
        # PASO 1: Extraer y validar el token
        # ===============================================
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print("🔑 Authorization Header recibido:", auth_header) # DEBUG
        if not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Token de autorización requerido'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        id_token = auth_header.split(' ')[1]
        print("NECESITO VER ID Token:", id_token)  # DEBUG
        
        # ===============================================
        # PASO 2: Verificar token con Firebase
        # ===============================================
        # Esto garantiza que el token es auténtico y no ha sido modificado
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        firebase_email = decoded_token.get('email')
        
        # Extraer datos adicionales del request body
        data = request.data
        firebase_name = data.get('nombre', '')
        firebase_picture = decoded_token.get('picture', '')
        
        # ===============================================
        # PASO 3: Buscar o crear usuario en MongoDB
        # ===============================================
        try:
            # CASO 1: Usuario YA EXISTE (login subsecuente)
            usuario = Usuario.objects.get(email=firebase_email)
            
            # Actualizar datos si cambiaron en Google
            updated = False
            if usuario.nombre != firebase_name and firebase_name:
                usuario.nombre = firebase_name
                updated = True
            
            # Actualizar avatar si cambió
            if usuario.perfil:
                if usuario.perfil.avatar_url != firebase_picture:
                    usuario.perfil.avatar_url = firebase_picture
                    updated = True
            else:
                # Crear perfil si no existe
                usuario.perfil = Perfil(
                    avatar_url=firebase_picture,
                    idioma='es',
                    timezone='America/Bogota'
                )
                updated = True
            
            if updated:
                usuario.save()
                
        except Usuario.DoesNotExist:
            # CASO 2: Usuario NUEVO (primer registro)
            print(f"📝 Creando nuevo usuario: {firebase_email}")
            
            # Crear perfil con datos de Google
            perfil = Perfil(
                avatar_url=firebase_picture,
                idioma='es',
                timezone='America/Bogota'
            )
            
            # Crear empresa si viene en el request
            empresa = None
            if data.get('empresa'):
                empresa_data = data.get('empresa')
                empresa = Empresa(
                    nombre=empresa_data.get('nombre', 'sin_empresa'),
                    telefono=empresa_data.get('telefono'),
                    nit=empresa_data.get('nit')
                )
            else:
                # Empresa por defecto
                empresa = Empresa(nombre='sin_empresa')
            
            # Crear usuario en MongoDB
            usuario = Usuario(
                nombre=firebase_name or firebase_email.split('@')[0],
                email=firebase_email,
                clave_hash=firebase_uid,  # ← IMPORTANTE: usar UID como identificador
                fecha_registro=datetime.utcnow(),
                perfil=perfil,
                empresa=empresa
            )
            usuario.save()
            print(f"✅ Usuario creado con ID: {usuario.id}")
        
        # ===============================================
        # PASO 4: Preparar respuesta para el frontend
        # ===============================================
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
        
        return Response({
            'success': True,
            'user': user_data,
            'message': 'Usuario sincronizado correctamente'
        }, status=status.HTTP_200_OK)
        
    except auth.InvalidIdTokenError:
        return Response(
            {'error': 'Token de Firebase inválido'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print(f"❌ Error en firebase_auth_sync: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==========================================
# ENDPOINT: Registro y listado de usuarios
# ==========================================
class UsuarioListCreateAPI(APIView):
    permission_classes = [AllowAny]  # Permitir registro sin autenticación
    
    def get(self, request):
        """Listar todos los usuarios"""
        usuarios = Usuario.objects()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Crear nuevo usuario (registro tradicional)"""
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
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Autenticar usuario con email y contraseña"""
        email = request.data.get("email")
        clave = request.data.get("clave_hash")

        if not email or not clave:
            return Response(
                {"error": "Email y clave son requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = Usuario.objects(email=email, clave_hash=clave).first()
        if not usuario:
            return Response(
                {"error": "Credenciales incorrectas"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = UsuarioSerializer(usuario)
        return Response({
            "ok": True,
            "message": "Inicio de sesión exitoso",
            "data": {
                "usuario": serializer.data
            }
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
            return Response(
                {"error": "Usuario no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    def put(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response(
                {"error": "Usuario no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario actualizado correctamente"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response(
                {"error": "Usuario no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        usuario.delete()
        return Response(
            {"message": "Usuario eliminado"}, 
            status=status.HTTP_204_NO_CONTENT
        )
