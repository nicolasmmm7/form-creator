# responseapp/serializers.py
from rest_framework import serializers
from bson import ObjectId
from datetime import datetime
from .models import Respondedor, RespuestaFormulario, RespuestaPregunta
from formapp.models import Formulario
from formapp.serializers import PreguntaSerializer  # opcional para validaciones coherentes

#obtener ip del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RespuestaPreguntaSerializer(serializers.Serializer):
    pregunta_id = serializers.IntegerField(required=True)
    tipo = serializers.CharField(required=True)
    valor = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=True
    )

    def validate(self, data):
        # validaciones básicas de forma (tipo y valor)
        tipo = data.get("tipo")
        valor = data.get("valor") or []

        if tipo == "texto_libre":
            if len(valor) != 1:
                raise serializers.ValidationError("texto_libre debe traer exactamente un valor en 'valor'.")
        elif tipo in ("opcion_multiple", "radio"):
            if len(valor) != 1:
                raise serializers.ValidationError("opcion_multiple/radio deben tener un único valor (en una lista).")
        elif tipo == "checkbox":
            if len(valor) < 1:
                raise serializers.ValidationError("checkbox debe contener al menos una opción seleccionada.")
        elif tipo == "escala_numerica":
            if len(valor) != 1:
                raise serializers.ValidationError("escala_numerica debe reportar un único valor numérico.")
            # el valor será validado numéricamente más abajo con los límites del formulario
        else:
            raise serializers.ValidationError({"tipo": f"Tipo de respuesta '{tipo}' no soportado."})

        return data


class RespondedorSerializer(serializers.Serializer):
    # usado cuando el respondent se manda explícitamente (ej: auth no integrada aún)
    ip_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    google_id = serializers.IntegerField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    foto_perfil = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def create_or_get(self, validated_data, request=None):
        print("🟢 create_or_get() - validated_data:", validated_data)

        """
        Busca o crea un Respondedor:
         - Prioridad: google_id -> email -> ip
        """
        if request is not None and not validated_data.get("ip_address"):
            validated_data["ip_address"] = get_client_ip(request)

        #Normalizar tipos (para evitar error de validacion en MongoEngine)
        for field in ["google_id", "email", "nombre", "foto_perfil", "ip_address"]:
            val = validated_data.get(field)
            if val is None or val == "":
                validated_data[field] = None
            elif not isinstance(val, str):
                validated_data[field]=str(val)

        # buscar por google_id
        google_id = validated_data.get("google_id")
        if google_id:
            r = Respondedor.objects(google_id=validated_data["google_id"]).first()
            if r:
                print("⚠️ Reusando respondedor (google_id)")
                # actualizar últimos campos mínimos
                if validated_data.get("nombre"):
                    r.nombre = validated_data.get("nombre")
                if validated_data.get("email"):
                    r.email = validated_data.get("email")
                r.ultimo_login = datetime.utcnow()
                r.save()
                return r

        # buscar por email
        email = validated_data.get("email")
        if email:
            r = Respondedor.objects(email=validated_data["email"]).first()
            if r:
                print("⚠️ Reusando respondedor (email existente):", r.email)
                r.ultimo_login = datetime.utcnow()
                if validated_data.get("nombre"):
                    r.nombre = validated_data.get("nombre")
                r.save()
                return r
            else: 
                print ("Creando respondedor nuevo (email proporcionado):", validated_data.get("email"))
                new_r = Respondedor(**validated_data)
                new_r.save()
                print("respondedor creado (por email): ", new_r.id)
                return new_r
            
        # fallback por IP
        ip = validated_data.get("ip_address")
        if ip:
            r = Respondedor.objects(ip_address=ip).first()
            if r:
                print("⚠️ Reusando respondedor (IP existente):", ip)
                r.ultimo_login = datetime.utcnow()
                if validated_data.get("nombre"):
                    r.nombre = validated_data.get("nombre")

                r.save()
                return r
            
        

        # crear nuevo
        print("🆕 Creando nuevo respondedor sin email, google o ip:", validated_data)
        r = Respondedor(**validated_data)
        r.save()
        print("✅ Respondedor guardado:", r.id)
        return r


class RespuestaFormularioSerializer(serializers.Serializer):
    formulario = serializers.CharField(required=True)  # ObjectId string
    respondedor = RespondedorSerializer(required=False, allow_null=True)
    fecha_envio = serializers.DateTimeField(required=False)
    tiempo_completacion = serializers.IntegerField(required=False, allow_null=True)
    respuestas = RespuestaPreguntaSerializer(many=True, required=True)

    def validate_formulario_exists(self, formulario_id):
        try:
            form = Formulario.objects.get(id=ObjectId(formulario_id))
            return form
        except Exception:
            raise serializers.ValidationError({"formulario": "Formulario no encontrado."})

    def validate(self, data):
        """
        Validaciones cruzadas:
         - que la estructura de respuestas cubra preguntas requeridas
         - que los valores respeten opciones/validaciones del formulario
        """
        formulario_id = data.get("formulario")
        form = self.validate_formulario_exists(formulario_id)
        preguntas_form = {p.id: p for p in getattr(form, "preguntas", [])}

        respuestas = data.get("respuestas", [])

        # chequeo duplicados de pregunta_id en las respuestas
        ids = [r["pregunta_id"] for r in respuestas]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Las respuestas contienen preguntas duplicadas.")
        
        if form.configuracion and form.configuracion.fecha_limite:
             if datetime.utcnow() > form.configuracion.fecha_limite:
                raise serializers.ValidationError({
            "formulario": "Este formulario ya no acepta respuestas (fecha límite superada)."
        })

        # revisar que todas las preguntas requeridas estén presentes
        for p in preguntas_form.values():
            if getattr(p, "obligatorio", False):
                if p.id not in ids:
                    raise serializers.ValidationError({
                        "respuestas": f"Falta la respuesta a la pregunta obligatoria id={p.id}."
                    })

        # validar cada respuesta contra la definición de la pregunta
        for r in respuestas:
            pid = r["pregunta_id"]
            if pid not in preguntas_form:
                raise serializers.ValidationError({"respuestas": f"Pregunta id={pid} no pertenece al formulario."})
            pregunta = preguntas_form[pid]
            tipo_preg = pregunta.tipo
            valores = r.get("valor", [])

            # validations by type
            if tipo_preg == "texto_libre":
                # obtener validaciones si existen
                valid = getattr(pregunta, "validaciones", None)
                text = valores[0] if valores else ""
                if valid:
                    min_len = getattr(valid, "longitud_minima", None)
                    max_len = getattr(valid, "longitud_maxima", None)
                    if min_len is not None and len(text) < min_len:
                        raise serializers.ValidationError({
                            "respuestas": f"Respuesta a pregunta {pid} menor que longitud_minima {min_len}."
                        })
                    if max_len is not None and len(text) > max_len:
                        raise serializers.ValidationError({
                            "respuestas": f"Respuesta a pregunta {pid} excede longitud_maxima {max_len}."
                        })

            elif tipo_preg in ("opcion_multiple", "radio", "checkbox"):
                opciones = [o.texto for o in getattr(pregunta, "opciones", [])]
                # verificar que cada valor exista en las opciones
                for sel in valores:
                    if sel not in opciones:
                        raise serializers.ValidationError({
                            "respuestas": f"Valor '{sel}' no es una opción válida para la pregunta {pid}."
                        })

                if tipo_preg in ("opcion_multiple", "radio") and len(valores) != 1:
                    raise serializers.ValidationError({
                        "respuestas": f"Pregunta {pid} espera un único valor."
                    })

            elif tipo_preg == "escala_numerica":
                valid = getattr(pregunta, "validaciones", None)
                try:
                    num = int(valores[0])
                except Exception:
                    raise serializers.ValidationError({
                        "respuestas": f"Respuesta para pregunta {pid} debe ser numérica."
                    })
                if valid:
                    vmin = getattr(valid, "valor_minimo", None)
                    vmax = getattr(valid, "valor_maximo", None)
                    if vmin is not None and num < vmin:
                        raise serializers.ValidationError({
                            "respuestas": f"Respuesta para pregunta {pid} menor que valor_minimo {vmin}."
                        })
                    if vmax is not None and num > vmax:
                        raise serializers.ValidationError({
                            "respuestas": f"Respuesta para pregunta {pid} mayor que valor_maximo {vmax}."
                        })
            else:
                raise serializers.ValidationError({"respuestas": f"Tipo de pregunta {tipo_preg} no soportado."})

        # attach form to validated data for use in create()
        data["_form_obj"] = form
        return data

    def create(self, validated_data):

        """
        Crear Respondedor (o reusar) y crear RespuestaFormulario.
        """
        print("💡 Entrando a create_or_get con:", validated_data)


        from datetime import datetime
        request = self.context.get("request", None)

        form = validated_data.pop("_form_obj", None)
        respondedor_data = validated_data.pop("respondedor", None) or {}
        print("🧩 RESPONDEDOR_DATA:", respondedor_data)

        tiempo = validated_data.get("tiempo_completacion", None)

        # determino IP
        ip = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

        # Prepare dict para buscar/crear Respondedor
        resp_valid = dict(respondedor_data)  # copia
        if ip and not resp_valid.get("ip_address"):
            resp_valid["ip_address"] = ip

        # try to detect from request.user (si tu auth lo permite)
        if request and getattr(request, "user", None) and getattr(request.user, "is_authenticated", False):
            # Si request.user tiene email o google id, preferir eso:
            if getattr(request.user, "email", None):
                resp_valid["email"] = request.user.email
            # si tu User model tiene un campo google_id, mapearlo:
            if getattr(request.user, "google_id", None):
                resp_valid["google_id"] = request.user.google_id
            if getattr(request.user, "first_name", None):
                resp_valid["nombre"] = getattr(request.user, "first_name")

        # crear/obtener respondedor
        resp_serializer = RespondedorSerializer(data=resp_valid)
        resp_serializer.is_valid(raise_exception=False)
        resp_validated = getattr(resp_serializer, "validated_data", {}) or {}
        respondedor_obj = resp_serializer.create_or_get(resp_validated, request=request)

        # ver si el formulario no permite múltiples respuestas
        exists = None
        config = getattr(form, "configuracion", None)
        if config and getattr(config, "una_respuesta", False):
            #si tenemos identificacion fiable se busca por eso
            if resp_validated.get("google_id"):
                respondedor = Respondedor.objects(google_id=resp_validated["google_id"]).first()
                if respondedor:
                    exists = RespuestaFormulario.objects(formulario=form, respondedor=respondedor).first()

            elif resp_validated.get("email"):
                respondedor = Respondedor.objects(email=resp_validated["email"]).first()
                if respondedor:
                    exists = RespuestaFormulario.objects(formulario=form, respondedor=respondedor).first()
            else:
                #Anonymous: buscar por IP
                if respondedor_obj and getattr(respondedor_obj, "ip_address", None):
                    respondedor = Respondedor.objects(ip_address=respondedor_obj.ip_address).first()
                    if respondedor:
                        exists = RespuestaFormulario.objects(formulario=form, respondedor=respondedor).first()

            if exists:
                #si permite editar, actualizamos la respuesta existente
                if getattr(config,  "permitir_edicion", False):
                    exists.respuestas = [
                        RespuestaPregunta(
                            pregunta_id = r["pregunta_id"],
                            tipo = r["tipo"],
                            valor = r.get("valor", [])
                        )
                        for r in validated_data.get("respuestas", [])
                    ]

                    exists.tiempo_completacion = tiempo
                    exists.fecha_envio = datetime.utcnow()
                    exists.save()
                    return exists
                    
                # si no permite edicion ---> error 
                raise serializers.ValidationError({
                    "non_field_errors": "Ya existe una respuesta registrada para este formulario"
                })
            

            # si respondedor fue creado solo por IP, podría haber existencias con ese mismo IP
            #if respondedor_obj and respondedor_obj.ip_address:
                # Buscar manualmente todas las respuestas y comparar
                #respuestas_ip = RespuestaFormulario.objects(formulario=form)
                #for r in respuestas_ip:
                   # if r.respondedor and r.respondedor.ip_address == respondedor_obj.ip_address:
                  #      raise serializers.ValidationError({
                      #      "non_field_errors": "Ya existe una respuesta desde esta IP para el formulario."
           # })

        # construir objetos RespuestaPregunta embebidos
        respuesta_objs = []
        for r in validated_data.get("respuestas", []):
            rp = RespuestaPregunta(
                pregunta_id=r["pregunta_id"],
                tipo=r["tipo"],
                valor=r.get("valor", [])
            )
            respuesta_objs.append(rp)

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor_obj,
            fecha_envio=validated_data.get("fecha_envio", datetime.utcnow()),
            tiempo_completacion=tiempo,
            respuestas=respuesta_objs
        )

        if config and getattr(config, "una_respuesta", False):
            existing = RespuestaFormulario.objects(formulario=form, respondedor=respondedor_obj).first()
            if existing:
                raise serializers.ValidationError({
            "non_field_errors": "Este formulario solo admite una respuesta por persona."
        })

        rf.save()
        return rf
    
    #Update para editar respuesta ------------------------
    def update(self, instance, validated_data):
        # Actualizar respuestas y tiempo de completación
        if "respuestas" in validated_data:
            # Construir lista de objetos RespuestaPregunta
            respuesta_objs = []
            for r in validated_data["respuestas"]:
                rp = RespuestaPregunta(
                    pregunta_id=r["pregunta_id"],
                    tipo=r["tipo"],
                    valor=r.get("valor", [])
                )
                respuesta_objs.append(rp)
            instance.respuestas = respuesta_objs
        if "tiempo_completacion" in validated_data:
            instance.tiempo_completacion = validated_data["tiempo_completacion"]
        # (Opcional: actualizar fecha_envio o respuestas de respondedor si se permite)

        instance.save()
        return instance
    
    
