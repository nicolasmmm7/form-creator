from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from formapp.models import Formulario, ConfiguracionFormulario
from formapp.serializers import FormularioSerializer
from utils.email_utils import send_form_invitation
from mongoengine.errors import DoesNotExist


class FormularioListCreateAPI(APIView):
    """GET: listar formularios (con filtro opcional ?admin=ID)
       POST: crear nuevo formulario"""

    def get(self, request):
        admin_id = request.GET.get("admin")  # ?admin=<id_usuario>
        if admin_id:
            formularios = Formulario.objects(administrador=admin_id)
        else:
            formularios = Formulario.objects()

        serializer = FormularioSerializer(formularios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FormularioSerializer(data=request.data)
        if serializer.is_valid():
            formulario = serializer.save()
            return Response({
                "message": "Formulario creado correctamente",
                "id": str(formulario.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormularioDetailAPI(APIView):
    """GET, PUT, DELETE por ID"""

    def get_object(self, id):
        try:
            return Formulario.objects.get(id=ObjectId(id))
        except Formulario.DoesNotExist:
            return None

    def get(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormularioSerializer(formulario)
        return Response(serializer.data)

    def put(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormularioSerializer(formulario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Formulario actualizado correctamente"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        formulario.delete()
        return Response({"message": "Formulario eliminado"}, status=status.HTTP_204_NO_CONTENT)


class FormularioAccesoAPI(APIView):
    """
    Verifica si un usuario tiene acceso para responder un formulario.
    GET: /api/formularios/{id}/verificar-acceso/?email=user@example.com
    """

    def get_object(self, id):
        try:
            return Formulario.objects.get(id=ObjectId(id))
        except Formulario.DoesNotExist:
            return None

    def get(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({
                "error": "Formulario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

        # Obtener el email del usuario desde los query params o desde Firebase auth
        email = request.GET.get('email')
        
        # Si no viene el email en los params, intentar obtenerlo del usuario autenticado
        # Asumiendo que tienes el email en request.user (ajusta según tu implementación de Firebase)
        if not email and hasattr(request, 'user') and hasattr(request.user, 'email'):
            email = request.user.email

        # Verificar si el formulario requiere login
        if formulario.configuracion and formulario.configuracion.requerir_login:
            if not email:
                return Response({
                    "tiene_acceso": False,
                    "razon": "Se requiere iniciar sesión para acceder a este formulario",
                    "requerir_login": True
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Verificar acceso usando el método del modelo
            tiene_acceso = formulario.usuario_puede_responder(email)
            
            if not tiene_acceso:
                return Response({
                    "tiene_acceso": False,
                    "razon": "No tienes autorización para acceder a este formulario privado",
                    "requerir_login": True,
                    "es_publico": formulario.configuracion.es_publico
                }, status=status.HTTP_403_FORBIDDEN)

            return Response({
                "tiene_acceso": True,
                "requerir_login": True,
                "es_publico": formulario.configuracion.es_publico,
                "formulario": {
                    "id": str(formulario.id),
                    "titulo": formulario.titulo,
                    "descripcion": formulario.descripcion
                }
            }, status=status.HTTP_200_OK)
        
        # Si no requiere login, todos tienen acceso
        return Response({
            "tiene_acceso": True,
            "requerir_login": False,
            "formulario": {
                "id": str(formulario.id),
                "titulo": formulario.titulo,
                "descripcion": formulario.descripcion
            }
        }, status=status.HTTP_200_OK)


class FormularioAgregarUsuarioAPI(APIView):
    """
    Agrega un usuario a la lista de usuarios autorizados de un formulario privado.
    POST: /api/formularios/{id}/agregar-usuario/
    Body: { "email": "usuario@example.com" }
    """

    def get_object(self, id):
        try:
            return Formulario.objects.get(id=ObjectId(id))
        except Formulario.DoesNotExist:
            return None

    def post(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({
                "error": "Formulario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get('email')
        if not email:
            return Response({
                "error": "El campo 'email' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el email tenga formato correcto
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                "error": "Formato de email inválido"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Normalizar email
        email = email.lower().strip()

        # Verificar que el formulario tenga configuración
        if not formulario.configuracion:
            formulario.configuracion = ConfiguracionFormulario()

        # Agregar el email si no existe
        if not formulario.configuracion.usuarios_autorizados:
            formulario.configuracion.usuarios_autorizados = []

        if email in formulario.configuracion.usuarios_autorizados:
            return Response({
                "message": "El usuario ya está en la lista de autorizados"
            }, status=status.HTTP_200_OK)

        formulario.configuracion.usuarios_autorizados.append(email)
        formulario.save()

        return Response({
            "message": "Usuario agregado correctamente",
            "email": email,
            "total_usuarios": len(formulario.configuracion.usuarios_autorizados)
        }, status=status.HTTP_200_OK)


class FormularioRemoverUsuarioAPI(APIView):
    """
    Remueve un usuario de la lista de usuarios autorizados de un formulario privado.
    DELETE: /api/formularios/{id}/remover-usuario/
    Body: { "email": "usuario@example.com" }
    """

    def get_object(self, id):
        try:
            return Formulario.objects.get(id=ObjectId(id))
        except Formulario.DoesNotExist:
            return None

    def delete(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({
                "error": "Formulario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

        email = request.data.get('email')
        if not email:
            return Response({
                "error": "El campo 'email' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Normalizar email
        email = email.lower().strip()

        # Verificar que el formulario tenga configuración y usuarios
        if not formulario.configuracion or not formulario.configuracion.usuarios_autorizados:
            return Response({
                "error": "Este formulario no tiene usuarios autorizados"
            }, status=status.HTTP_400_BAD_REQUEST)

        if email not in formulario.configuracion.usuarios_autorizados:
            return Response({
                "error": "El usuario no está en la lista de autorizados"
            }, status=status.HTTP_404_NOT_FOUND)

        formulario.configuracion.usuarios_autorizados.remove(email)
        formulario.save()

        return Response({
            "message": "Usuario removido correctamente",
            "email": email,
            "total_usuarios": len(formulario.configuracion.usuarios_autorizados)
        }, status=status.HTTP_200_OK)


class FormularioListarUsuariosAPI(APIView):
    """
    Lista todos los usuarios autorizados de un formulario privado.
    GET: /api/formularios/{id}/usuarios-autorizados/
    """

    def get_object(self, id):
        try:
            return Formulario.objects.get(id=ObjectId(id))
        except Formulario.DoesNotExist:
            return None

    def get(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({
                "error": "Formulario no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)

        usuarios = []
        if formulario.configuracion and formulario.configuracion.usuarios_autorizados:
            usuarios = formulario.configuracion.usuarios_autorizados

        return Response({
            "formulario_id": str(formulario.id),
            "titulo": formulario.titulo,
            "es_publico": formulario.configuracion.es_publico if formulario.configuracion else True,
            "usuarios_autorizados": usuarios,
            "total": len(usuarios)
        }, status=status.HTTP_200_OK)
    

class EnviarInvitacionesAPI(APIView):
    """
    POST: Enviar invitaciones por email a usuarios autorizados
    """
    
    def post(self, request, form_id):
        print(f"🔔 Solicitud de invitaciones para formulario: {form_id}")
        
        try:
            # Importar aquí para evitar errores de importación circular
            from utils.email_utils import send_form_invitation
            
            # Obtener el formulario
            try:
                form = Formulario.objects.get(id=ObjectId(form_id))
            except DoesNotExist:
                print(f"❌ Formulario {form_id} no encontrado")
                return Response(
                    {"error": "Formulario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validar que el usuario sea el administrador
            user_id = request.data.get("user_id")
            admin_id = str(form.administrador.id) if form.administrador else None
            
            print(f"👤 Usuario solicitante: {user_id}")
            print(f"👤 Administrador del form: {admin_id}")
            
            if str(user_id) != admin_id:
                return Response(
                    {"error": "No tienes permiso para enviar invitaciones"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener usuarios autorizados
            usuarios = []
            if hasattr(form, 'configuracion') and form.configuracion:
                usuarios = getattr(form.configuracion, 'usuarios_autorizados', [])
            
            print(f"📧 Usuarios autorizados: {usuarios}")
            
            if not usuarios:
                return Response(
                    {"error": "No hay usuarios autorizados en este formulario"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Construir el enlace del formulario
            # 🔗 Para desarrollo local
            form_link = f"https://form-creator-rosy.vercel.app/form/{form_id}/answer"
            
            # 🔗 Para producción (descomentar cuando esté desplegado)
            # origin = request.META.get('HTTP_ORIGIN', 'https://tudominio.com')
            # form_link = f"{origin}/form/{form_id}/answer"
            
            print(f"🔗 Link del formulario: {form_link}")
            
            # Enviar emails
            enviados = 0
            fallidos = []
            
            for email in usuarios:
                print(f"📤 Enviando invitación a: {email}")
                try:
                    exito = send_form_invitation(
                        recipient_email=email,
                        form_title=form.titulo,
                        form_description=form.descripcion or "",
                        form_link=form_link
                    )
                    
                    if exito:
                        enviados += 1
                        print(f"✅ Invitación enviada a {email}")
                    else:
                        fallidos.append(email)
                        print(f"❌ Falló el envío a {email}")
                except Exception as e:
                    print(f"❌ Error enviando a {email}: {e}")
                    fallidos.append(email)
            
            resultado = {
                "message": f"Invitaciones enviadas: {enviados}/{len(usuarios)}",
                "enviados": enviados,
                "total": len(usuarios),
                "fallidos": fallidos
            }
            
            print(f"📊 Resultado final: {resultado}")
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("❌ Error general al enviar invitaciones:")
            traceback.print_exc()
            return Response(
                {"error": f"Error interno: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )