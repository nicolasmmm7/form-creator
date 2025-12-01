from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import serializers
from bson import ObjectId
from .models import RespuestaFormulario, Respondedor
from .serializers import RespuestaFormularioSerializer
from formapp.models import Formulario
from mongoengine.errors import DoesNotExist


def is_admin_of_form(user, form):
    """
    Helper: compara user con form.administrador.
    """
    try:
        if not user or not getattr(user, "is_authenticated", False):
            return False
        admin = getattr(form, "administrador", None)
        if not admin:
            return False
        try:
            user_id = getattr(user, "id", None) or getattr(user, "pk", None) or getattr(user, "_id", None)
            if user_id and str(user_id) == str(getattr(admin, "id", admin)):
                return True
        except Exception:
            pass
        if getattr(user, "email", None) and getattr(admin, "email", None):
            return user.email == admin.email
    except Exception:
        return False
    return False


class RespuestaListCreateAPI(APIView):
    """
    GET: listar respuestas (filtro ?formulario=<id>)
    POST: crear respuesta para un formulario
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        form_id = request.GET.get("formulario")
        if not form_id:
            return Response({"error": "Query param 'formulario' es requerido para listar respuestas."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            form = Formulario.objects.get(id=ObjectId(form_id))
        except Exception:
            return Response({"error": "Formulario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin_of_form(request.user, form):
            if getattr(form.configuracion, "privado", False):
                return Response({"error": "No autorizado. Solo el administrador puede listar respuestas."},
                                status=status.HTTP_403_FORBIDDEN)

        respuestas = RespuestaFormulario.objects(formulario=form)
        out = []
        for r in respuestas:
            try:
                resp = r.respondedor
                resp_info = {
                    "id": str(resp.id) if resp else None,
                    "ip_address": getattr(resp, "ip_address", None),
                    "email": getattr(resp, "email", None),
                    "nombre": getattr(resp, "nombre", None),
                }
            except DoesNotExist:
                resp_info = {
                    "id": None, 
                    "ip_address": None, 
                    "email": None, 
                    "nombre": None,
                }
            
            out.append({
                "id": str(r.id),
                "formulario": str(r.formulario.id),
                "respondedor": resp_info,
                "fecha_envio": r.fecha_envio,
                "tiempo_completacion": r.tiempo_completacion,
                "navegador": getattr(r, "navegador", "Desconocido"),      # ✅ Desde respuesta
                "dispositivo": getattr(r, "dispositivo", "Desconocido"),  # ✅ Desde respuesta
                "respuestas": [
                    {"pregunta_id": rp.pregunta_id, "tipo": rp.tipo, "valor": rp.valor} for rp in r.respuestas
                ]
            })
        return Response(out, status=status.HTTP_200_OK)

    def post(self, request):
        import traceback

        serializer = RespuestaFormularioSerializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as ve:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Comprobar requisito de login
        form = serializer.validated_data.get("_form_obj")
        config = getattr(form, "configuracion", None)
        if config and getattr(config, "requerir_login", False):
            user_authenticated = getattr(request, "user", None) and getattr(request.user, "is_authenticated", False)
            payload_respondedor = request.data.get("respondedor")
            if not user_authenticated and not payload_respondedor:
                return Response({"error": "Este formulario requiere autenticación para responder."},
                                status=status.HTTP_403_FORBIDDEN)

        try:
            # 🆕 Detectar dispositivo desde User-Agent (como fallback)
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
                dispositivo_fallback = "Móvil"
            elif "tablet" in user_agent or "ipad" in user_agent:
                dispositivo_fallback = "Tablet"
            else:
                dispositivo_fallback = "Desktop"
            
            # Pasar dispositivo al serializer
            serializer.context["dispositivo"] = dispositivo_fallback
            
            print("📊 Datos recibidos del frontend:")
            print(f"  - Tiempo completación: {request.data.get('tiempo_completacion')} segundos")
            print(f"  - Navegador: {request.data.get('respondedor', {}).get('navegador', 'N/A')}")
            print(f"  - Dispositivo: {request.data.get('respondedor', {}).get('dispositivo', dispositivo_fallback)}")
            
            rf = serializer.save()
            
            return Response({
                "message": "Respuesta guardada correctamente.",
                "id": str(rf.id),
                "tiempo_completacion": rf.tiempo_completacion  # 🆕 Para verificar
            }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RespuestaDetailAPI(APIView):
    """
    GET /api/respuestas/<id>/ -> detalle
    DELETE -> eliminar
    PUT -> editar respuesta
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
                "nombre": r.respondedor.nombre,
            },
            "fecha_envio": r.fecha_envio,
            "tiempo_completacion": r.tiempo_completacion,
            "navegador": getattr(r, "navegador", "Desconocido"),      # ✅ Desde respuesta
            "dispositivo": getattr(r, "dispositivo", "Desconocido"),  # ✅ Desde respuesta
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

    def put(self, request, id):
        r = self.get_object(id)
        if not r:
            return Response({"error": "Respuesta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        form = r.formulario
        if not getattr(form.configuracion, "permitir_edicion", False):
            return Response({"error": "Edición no permitida."}, status=status.HTTP_403_FORBIDDEN)

        user = getattr(request, "user", None)
        owner_match = False

        try:
            if user and getattr(user, "is_authenticated", False):
                if getattr(r.respondedor, "email", None) and getattr(user, "email", None) == r.respondedor.email:
                    owner_match = True
            if not owner_match and getattr(user, "google_id", None) and getattr(r.respondedor, "google_id", None):
                if str(user.google_id) == str(r.respondedor.google_id):
                    owner_match = True
        except Exception:
            owner_match = False

        payload_respondedor = request.data.get("respondedor") or {}
        payload_email = payload_respondedor.get("email")
        payload_google = payload_respondedor.get("google_id")

        try:
            if payload_email and getattr(r.respondedor, "email", None) and payload_email == r.respondedor.email:
                owner_match = True
            if payload_google and getattr(r.respondedor, "google_id", None) and str(payload_google) == str(r.respondedor.google_id):
                owner_match = True
        except Exception:
            pass

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


class FormularioEstadisticasAPI(APIView):
    """
    GET /api/formularios/<id>/estadisticas/
    Retorna métricas y datos para gráficos.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            form = Formulario.objects.get(id=ObjectId(id))
        except DoesNotExist:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin_of_form(request.user, form):
            pass  # Bypass temporal

        respuestas = RespuestaFormulario.objects(formulario=form)
        total_respuestas = respuestas.count()

        if total_respuestas == 0:
            return Response({
                "total_respuestas": 0,
                "tiempo_promedio": 0,
                "dispositivos": [],
                "navegadores": [],  # 🆕 Nuevo
                "preguntas": [],
                "respuestas_por_fecha": []
            })

        # 1. Tiempo promedio
        tiempos = [r.tiempo_completacion for r in respuestas if r.tiempo_completacion]
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0

        # 2. Dispositivos - ✅ desde RespuestaFormulario
        dispositivos_count = {}
        for r in respuestas:
            dev = getattr(r, "dispositivo", "Desconocido")  # ✅ Desde la respuesta
            dispositivos_count[dev] = dispositivos_count.get(dev, 0) + 1

        dispositivos_data = [
            {"name": k, "value": v} for k, v in dispositivos_count.items()
        ]

        # 🆕 3. Navegadores - ✅ desde RespuestaFormulario
        navegadores_count = {}
        for r in respuestas:
            nav = getattr(r, "navegador", "Desconocido")  # ✅ Desde la respuesta
            navegadores_count[nav] = navegadores_count.get(nav, 0) + 1

        navegadores_data = [
            {"name": k, "value": v} for k, v in navegadores_count.items()
        ]

        # 4. Respuestas por fecha
        fechas_count = {}
        for r in respuestas:
            fecha_str = r.fecha_envio.strftime("%Y-%m-%d")
            fechas_count[fecha_str] = fechas_count.get(fecha_str, 0) + 1
        
        respuestas_por_fecha = [
            {"fecha": k, "cantidad": v} for k, v in sorted(fechas_count.items())
        ]

        # 5. Análisis por pregunta
        preguntas_stats = []
        for p in form.preguntas:
            p_stats = {
                "id": p.id,
                "enunciado": p.enunciado,
                "tipo": p.tipo,
                "total_respuestas": 0,
                "datos": []
            }

            valores = []
            for r in respuestas:
                resp_p = next((rp for rp in r.respuestas if rp.pregunta_id == p.id), None)
                if resp_p and resp_p.valor:
                    valores.extend(resp_p.valor)
            
            p_stats["total_respuestas"] = len(valores)

            if p.tipo in ["opcion_multiple", "checkbox", "escala_numerica"]:
                conteo = {}
                for v in valores:
                    conteo[v] = conteo.get(v, 0) + 1
                p_stats["datos"] = [
                    {"name": k, "value": v} for k, v in conteo.items()
                ]
            elif p.tipo == "texto_libre":
                p_stats["datos"] = [{"texto": v} for v in valores[-20:]]

            preguntas_stats.append(p_stats)

        return Response({
            "total_respuestas": total_respuestas,
            "tiempo_promedio": tiempo_promedio,
            "dispositivos": dispositivos_data,
            "navegadores": navegadores_data,  # 🆕 Nuevo
            "respuestas_por_fecha": respuestas_por_fecha,
            "preguntas": preguntas_stats
        })


class FormularioExportarAPI(APIView):
    """
    GET /api/formularios/<id>/exportar/
    Descarga un CSV con todas las respuestas.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        import csv
        from django.http import HttpResponse

        try:
            form = Formulario.objects.get(id=ObjectId(id))
        except DoesNotExist:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin_of_form(request.user, form):
            pass  # Bypass temporal

        respuestas = RespuestaFormulario.objects(formulario=form)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="respuestas_{id}.csv"'

        writer = csv.writer(response)
        
        # Headers - 🆕 Agregado Navegador
        headers = ["Fecha", "Dispositivo", "Navegador", "Tiempo (s)", "Email", "Nombre"]
        pregunta_map = {}
        
        for p in form.preguntas:
            headers.append(p.enunciado)
            pregunta_map[p.id] = len(headers) - 1
        
        writer.writerow(headers)

        # Rows
# Rows
        for r in respuestas:
            row = [""] * len(headers)
            row[0] = r.fecha_envio.strftime("%Y-%m-%d %H:%M:%S")
            row[1] = getattr(r, "dispositivo", "Desconocido")  # ✅ Desde respuesta
            row[2] = getattr(r, "navegador", "Desconocido")    # ✅ Desde respuesta
            row[3] = r.tiempo_completacion
            row[4] = r.respondedor.email if r.respondedor else ""
            row[5] = r.respondedor.nombre if r.respondedor else ""

            for rp in r.respuestas:
                idx = pregunta_map.get(rp.pregunta_id)
                if idx:
                    val = rp.valor
                    if isinstance(val, list):
                        val = ", ".join(val)
                    row[idx] = val
            
            writer.writerow(row)

        return response