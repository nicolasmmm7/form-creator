# firebase_auth/authentication.py
import firebase_admin
import os
from firebase_admin import credentials, auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from usuarioapp.models import Usuario
from core.firebase_config import firebase_auth as auth

# ==========================================
# INICIALIZACIÓN DE FIREBASE ADMIN SDK
# ==========================================
# Este código se ejecuta UNA SOLA VEZ cuando Django inicia
# Firebase Admin SDK permite verificar tokens desde el servidor


class FirebaseAuthentication(BaseAuthentication):
    """
    Clase de autenticación personalizada para Django REST Framework
    
    ¿Cómo funciona?
    1. Django REST Framework llama automáticamente a authenticate() en cada request
    2. Extrae el token JWT del header Authorization
    3. Verifica el token con Firebase usando auth.verify_id_token()
    4. Si es válido, busca el usuario en MongoDB
    5. Retorna el usuario para que esté disponible en request.user
    """
    
    def authenticate(self, request):
        """
        Método principal de autenticación
        Retorna tupla (usuario, token) si autenticación exitosa
        Retorna None si no hay token (permite endpoints públicos)
        Lanza AuthenticationFailed si token inválido
        """
        # Extraer header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # Si no hay header, este endpoint es público
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Extraer el token (formato: "Bearer <token>")
        id_token = auth_header.split(' ')[1]
        
        try:
            # ===============================================
            # VERIFICACIÓN DEL TOKEN CON FIREBASE
            # ===============================================
            # Esta llamada verifica:
            # 1. Que el token fue emitido por Firebase
            # 2. Que no ha expirado (tokens expiran en 1 hora)
            # 3. Que no ha sido revocado
            # 4. Que la firma es válida
            decoded_token = auth.verify_id_token(id_token)
            
            # Extraer información del token
            uid = decoded_token['uid']              # ID único de Firebase
            email = decoded_token.get('email')      # Email del usuario
            
            # ===============================================
            # BUSCAR USUARIO EN MONGODB
            # ===============================================
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                # Si el usuario no existe en MongoDB, autenticación falla
                raise AuthenticationFailed('Usuario no registrado en el sistema')
            
            # Retornar usuario y token decodificado
            # request.user será el objeto Usuario
            # request.auth será el token decodificado
            return (usuario, decoded_token)
            
        except auth.ExpiredIdTokenError:
            raise AuthenticationFailed('Token expirado. Por favor inicia sesión nuevamente.')
        except auth.RevokedIdTokenError:
            raise AuthenticationFailed('Token revocado. Por favor inicia sesión nuevamente.')
        except auth.InvalidIdTokenError:
            raise AuthenticationFailed('Token inválido.')
        except Exception as e:
            raise AuthenticationFailed(f'Error de autenticación: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Retorna el tipo de autenticación para el header WWW-Authenticate
        """
        return 'Bearer'
