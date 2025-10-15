# ====================================================
# ARCHIVO CORREGIDO: authentication/firebase_auth.py
# ====================================================
# SOLUCIÓN: Agregar logs detallados para debugging

from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from usuarioapp.models import Usuario


class FirebaseAuthentication(BaseAuthentication):
    """
    Clase de autenticación personalizada para Django REST Framework
    """
    
    def authenticate(self, request):
        """
        Método principal de autenticación con LOGS DETALLADOS
        """
        
        # ===============================================
        # PASO 1: Extraer header Authorization
        # ===============================================
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # Si no hay header, este endpoint puede ser público
        if not auth_header:
            return None
        
        # Verificar formato: "Bearer <token>"
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extraer el token
        try:
            id_token = auth_header.split(' ')[1]
        except IndexError:
            raise AuthenticationFailed('Formato de token inválido. Use: Bearer <token>')
        
        # ===============================================
        # PASO 2: Verificar token con Firebase Admin SDK
        # ===============================================
        print("=" * 80)
        print("🔍 FirebaseAuthentication.authenticate() INICIADO")
        print("=" * 80)
        print(f"🔑 Token recibido (primeros 50 chars): {id_token[:50]}...")
        
        try:
            # ⚠️ CRÍTICO: Agregar check_revoked=False para debugging
            decoded_token = auth.verify_id_token(id_token, check_revoked=False)
            
            # Extraer información del token decodificado
            firebase_uid = decoded_token['uid']
            firebase_email = decoded_token.get('email')
            
            print(f"✅ Token verificado exitosamente en FirebaseAuthentication")
            print(f"   ├─ UID: {firebase_uid}")
            print(f"   ├─ Email: {firebase_email}")
            print(f"   ├─ Issuer: {decoded_token.get('iss', 'N/A')}")
            print(f"   └─ Audience (Project ID): {decoded_token.get('aud', 'N/A')}")
            
            if not firebase_email:
                raise AuthenticationFailed('Token no contiene email de usuario')
            
        except auth.ExpiredIdTokenError as e:
            print(f"❌ Token expirado: {str(e)}")
            raise AuthenticationFailed('Token expirado. Por favor inicia sesión nuevamente.')
        
        except auth.RevokedIdTokenError as e:
            print(f"❌ Token revocado: {str(e)}")
            raise AuthenticationFailed('Token revocado. Por favor inicia sesión nuevamente.')
        
        except auth.InvalidIdTokenError as e:
            print(f"❌ Token inválido: {str(e)}")
            print(f"   Detalles del error: {type(e).__name__}")
            raise AuthenticationFailed(f'Token inválido: {str(e)}')
        
        except ValueError as e:
            print(f"❌ ValueError al verificar token: {str(e)}")
            raise AuthenticationFailed(f'Error de validación: {str(e)}')
        
        except Exception as e:
            print(f"❌ Error inesperado al verificar token: {str(e)}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise AuthenticationFailed(f'Error al verificar token: {str(e)}')
        
        # ===============================================
        # PASO 3: Buscar usuario en MongoDB
        # ===============================================
        try:
            usuario = Usuario.objects.get(email=firebase_email)
            print(f"✅ Usuario encontrado en MongoDB: {usuario.nombre}")
            print("=" * 80)
            
        except Usuario.DoesNotExist:
            print(f"❌ Usuario NO encontrado en MongoDB: {firebase_email}")
            print("=" * 80)
            return None
            
        
        except Exception as e:
            print(f"❌ Error al buscar usuario: {str(e)}")
            print("=" * 80)
            return None
        
        # Retornar usuario autenticado
        return (usuario, decoded_token)
    
    def authenticate_header(self, request):
        """
        Retorna el tipo de autenticación para el header WWW-Authenticate
        """
        return 'Bearer'