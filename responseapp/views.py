from django.shortcuts import render

# responseapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import serializers
from bson import ObjectId
from .models import RespuestaFormulario, Respondedor
from .serializers import RespuestaFormularioSerializer
from formapp.models import Formulario


def is_admin_of_form(user, form):
    """
    Helper: compara user con form.administrador.
    Ajusta según cómo tengas tu modelo Usuario.
    """
    try:
        if not user or not getattr(user, "is_authenticated", False):
            return False
        # si administrador se guarda como referencia a Usuario (mongoengine Document),
        # comparar por id o por email según tu implementación.
        admin = getattr(form, "administrador", None)
        if not admin:
            return False
        # comparación robusta:
        try:
            # si user tiene id (string o ObjectId)
            user_id = getattr(user, "id", None) or getattr(user, "pk", None) or getattr(user, "_id", None)
            if user_id and str(user_id) == str(getattr(admin, "id", admin)):
                return True
        except Exception:
            pass
        # o comparar por email
        if getattr(user, "email", None) and getattr(admin, "email", None):
            return user.email == admin.email
    except Exception:
        return False
    return False


class RespuestaListCreateAPI(APIView):
    """
    GET: listar respuestas (filtro ?formulario=<id>) -> solo admin del formulario
    POST: crear respuesta para un formulario
    """
    permission_classes = [permissions.AllowAny]  # validación interna (requerir_login) será chequeada

    def get(self, request):
        form_id = request.GET.get("formulario")
        if not form_id:
            return Response({"error": "Query param 'formulario' es requerido para listar respuestas."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            form = Formulario.objects.get(id=ObjectId(form_id))
        except Exception:
            return Response({"error": "Formulario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # validar que quien solicita sea el administrador del formulario (o staff si lo deseas)
        """if not is_admin_of_form(request.user, form):   ESTA SE DEBE PONER PERO NO MIENTRAS SEA DE PRUEBA
            return Response({"error": "No autorizado. Solo el administrador puede listar respuestas."},
                            status=status.HTTP_403_FORBIDDEN)"""
        if not is_admin_of_form(request.user, form):
            # ⚠️ Si el formulario no es privado, permite listar aunque no sea admin  MIENTRAS QUE SEA DE PRUEBA 
            #DEJAR ESTE METODO PARA TRAER LOS FORMULARIOS SIN AUTENTIFICARSE COMO ADMIN
            if getattr(form.configuracion, "privado", False):
                return Response({"error": "No autorizado. Solo el administrador puede listar respuestas."},
                                status=status.HTTP_403_FORBIDDEN)

        respuestas = RespuestaFormulario.objects(formulario=form)
        # serializar manualmente (podrías crear un serializer read-only si quieres)
        out = []
        for r in respuestas:
            out.append({
                "id": str(r.id),
                "formulario": str(r.formulario.id),
                "respondedor": {
                    "id": str(r.respondedor.id),
                    "ip_address": r.respondedor.ip_address,
                    "email": r.respondedor.email,
                    "nombre": r.respondedor.nombre
                },
                "fecha_envio": r.fecha_envio,
                "tiempo_completacion": r.tiempo_completacion,
                "respuestas": [
                    {"pregunta_id": rp.pregunta_id, "tipo": rp.tipo, "valor": rp.valor} for rp in r.respuestas
                ]
            })
        return Response(out, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crear una respuesta.
        Payload ejemplo:
        {
          "formulario": "<form_objectid_string>",
          "respondedor": { "email": "x@x.com", "nombre": "Juan" },  # opcional si auth está disponible
          "tiempo_completacion": 45,
          "respuestas": [
             {"pregunta_id": 1, "tipo": "texto_libre", "valor": ["respuesta"]},
             {"pregunta_id": 2, "tipo": "checkbox", "valor": ["op1","op3"]},
             ...
          ]
        }
        """
        serializer = RespuestaFormularioSerializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as ve:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # comprobar requisito de login del formulario
        form = serializer.validated_data.get("_form_obj")  # attach en validate()
        config = getattr(form, "configuracion", None)
        if config and getattr(config, "requerir_login", False):
            # pedir que request.user esté autenticado o que se provea un respondedor con email/google_id
            user_authenticated = getattr(request, "user", None) and getattr(request.user, "is_authenticated", False)
            payload_respondedor = request.data.get("respondedor")
            if not user_authenticated and not payload_respondedor:
                return Response({"error": "Este formulario requiere autenticación para responder."},
                                status=status.HTTP_403_FORBIDDEN)

        try:
            rf = serializer.save()
            return Response({
                "message": "Respuesta guardada correctamente.",
                "id": str(rf.id)
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RespuestaDetailAPI(APIView):
    """
    GET /api/respuestas/<id>/ -> detalle (solo admin del formulario)
    DELETE -> eliminar (solo admin)
    """
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return RespuestaFormulario.objects.get(id=ObjectId(id))
        except Exception:
            return None

    def get(self, request, id):
        r = self.get_object(id)
        if not r:
            return Response({"error": "Respuesta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # comprobar permiso admin sobre el formulario
        """if not is_admin_of_form(request.user, r.formulario):  DEJAR ESTE DESPUES DE HACER LAS PRUEBAS
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)"""
        if not is_admin_of_form(request.user, r.formulario):
            if getattr(r.formulario.configuracion, "privado", False):
                return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)


        out = {
            "id": str(r.id),
            "formulario": str(r.formulario.id),
            "respondedor": {
                "id": str(r.respondedor.id),
                "ip_address": r.respondedor.ip_address,
                "email": r.respondedor.email,
                "nombre": r.respondedor.nombre
            },
            "fecha_envio": r.fecha_envio,
            "tiempo_completacion": r.tiempo_completacion,
            "respuestas": [
                {"pregunta_id": rp.pregunta_id, "tipo": rp.tipo, "valor": rp.valor} for rp in r.respuestas
            ]
        }
        return Response(out, status=status.HTTP_200_OK)

    def delete(self, request, id):
        r = self.get_object(id)
        if not r:
            return Response({"error": "Respuesta no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        if not is_admin_of_form(request.user, r.formulario):
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        r.delete()
        return Response({"message": "Respuesta eliminada."}, status=status.HTTP_204_NO_CONTENT)

#agregado: para editar respuestas-----------------------------
    def put(self, request, id):
        r = self.get_object(id)
        if not r:
            return Response({"error": "Respuesta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        form = r.formulario
        if not getattr(form.configuracion, "permitir_edicion", False):
            return Response({"error": "Edición no permitida."}, status=status.HTTP_403_FORBIDDEN)

        user = getattr(request, "user", None)
        owner_match = False
        if user and getattr(user, "is_authenticated", False):
            if getattr(r.respondedor, "email", None) and getattr(user, "email", None) == r.respondedor.email:
                owner_match = True

        if getattr(form.configuracion, "requerir_login", False) and not owner_match and not is_admin_of_form(user, form):
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RespuestaFormularioSerializer(instance=r, data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
            rf = serializer.save()
            return Response({"message": "Respuesta actualizada.", "id": str(rf.id)}, status=status.HTTP_200_OK)
        except serializers.ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)