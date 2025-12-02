# responseapp/serializers.py
from rest_framework import serializers
from bson import ObjectId
from .models import RespuestaFormulario, Respondedor, RespuestaPregunta
from formapp.models import Formulario
from mongoengine.errors import DoesNotExist
from utils.email_utils import send_form_responses_copy


class RespuestaFormularioSerializer(serializers.Serializer):
    formulario = serializers.CharField()
    respondedor = serializers.DictField(required=False, allow_null=True)
    tiempo_completacion = serializers.IntegerField(required=False, default=0)
    enviar_copia = serializers.BooleanField(required=False, default=False)
    respuestas = serializers.ListField(
        child=serializers.DictField()
    )

    def validate(self, data):
        """
        Validar que el formulario exista y adjuntarlo para uso posterior
        """
        form_id_str = data.get("formulario")
        if not form_id_str:
            raise serializers.ValidationError({"formulario": "Campo requerido."})
        
        try:
            form_obj = Formulario.objects.get(id=ObjectId(form_id_str))
        except DoesNotExist:
            raise serializers.ValidationError({"formulario": "Formulario no encontrado."})
        
        data["_form_obj"] = form_obj
        return data

    def create(self, validated_data):
        """
        Crear una nueva respuesta de formulario
        """
        form_obj = validated_data.pop("_form_obj")
        respondedor_data = validated_data.pop("respondedor", {})
        tiempo_completacion = validated_data.pop("tiempo_completacion", 0)
        enviar_copia = validated_data.pop("enviar_copia", False)
        respuestas_data = validated_data.pop("respuestas", [])
        
        # 🆕 Extraer navegador y dispositivo del payload
        navegador_payload = respondedor_data.get("navegador", "Desconocido")
        dispositivo_payload = respondedor_data.get("dispositivo", "Desconocido")
        
        # Fallback desde el contexto (User-Agent del servidor)
        dispositivo_fallback = self.context.get("dispositivo", "Desconocido")
        
        # Usar el del payload si existe, sino el fallback
        navegador_final = navegador_payload if navegador_payload != "Desconocido" else "Desconocido"
        dispositivo_final = dispositivo_payload if dispositivo_payload != "Desconocido" else dispositivo_fallback
        
        print(f"📊 Guardando respuesta - Navegador: {navegador_final}, Dispositivo: {dispositivo_final}")
        
        # Crear o buscar respondedor (SIN actualizar navegador/dispositivo)
        ip = respondedor_data.get("ip_address", "0.0.0.0")
        email = respondedor_data.get("email")
        google_id = respondedor_data.get("google_id")
        nombre = respondedor_data.get("nombre")
        
        # Buscar respondedor existente
        respondedor = None
        if email:
            respondedor = Respondedor.objects(email=email).first()
        if not respondedor and google_id:
            respondedor = Respondedor.objects(google_id=google_id).first()
        if not respondedor:
            respondedor = Respondedor.objects(ip_address=ip).first()
        
        if not respondedor:
            # Crear nuevo respondedor SIN navegador/dispositivo
            respondedor = Respondedor(
                ip_address=ip,
                email=email,
                nombre=nombre,
                google_id=google_id
            )
            respondedor.save()
            print(f"✅ Nuevo respondedor creado: {respondedor.id}")
        else:
            # ✅ Solo actualizar datos de identidad (NO navegador/dispositivo)
            actualizado = False
            if email and respondedor.email != email:
                respondedor.email = email
                actualizado = True
            if nombre and respondedor.nombre != nombre:
                respondedor.nombre = nombre
                actualizado = True
            
            if actualizado:
                respondedor.save()
                print(f"✅ Respondedor actualizado (identidad): {respondedor.id}")
        
        # Crear las respuestas a preguntas
        respuestas_objs = []
        for rdata in respuestas_data:
            rp = RespuestaPregunta(
                pregunta_id=rdata.get("pregunta_id"),
                tipo=rdata.get("tipo"),
                valor=rdata.get("valor", [])
            )
            respuestas_objs.append(rp)
        
        # ✅ Crear RespuestaFormulario con navegador/dispositivo de ESTA respuesta
        rf = RespuestaFormulario(
            formulario=form_obj,
            respondedor=respondedor,
            tiempo_completacion=tiempo_completacion,
            navegador=navegador_final,      # ✅ A nivel de respuesta
            dispositivo=dispositivo_final,  # ✅ A nivel de respuesta
            respuestas=respuestas_objs
        )
        rf.save()
        
        print(f"✅ RespuestaFormulario guardada con ID: {rf.id}")
        print(f"   └─ Navegador: {rf.navegador}, Dispositivo: {rf.dispositivo}, Tiempo: {rf.tiempo_completacion}s")
        
        # TODO: Enviar copia por correo si enviar_copia == True
        # 🆕 Enviar copia por correo — AHORA FUNCIONA
        if enviar_copia and email:
            respuestas_list = []
            for rp in respuestas_objs:
                respuestas_list.append({
                    "pregunta": rp.pregunta_id,
                    "respuesta": ", ".join(rp.valor) if isinstance(rp.valor, list) else rp.valor
                })

            send_form_responses_copy(
                recipient_email=email,
                form_title=form_obj.titulo,
                respuestas_list=respuestas_list
            )
            print("📧 Copia enviada correctamente desde POST")
        
        return rf

    def update(self, instance, validated_data):
        """
        Actualizar una respuesta existente + enviar email si enviar_copia=True
        """
        form_obj = validated_data.pop("_form_obj", None)
        respondedor_data = validated_data.pop("respondedor", {})
        tiempo_completacion = validated_data.pop("tiempo_completacion", instance.tiempo_completacion)
        enviar_copia = validated_data.pop("enviar_copia", False)
        respuestas_data = validated_data.pop("respuestas", [])

        instance.tiempo_completacion = tiempo_completacion

        # Reconstruir respuestas
        respuestas_objs = []
        for rdata in respuestas_data:
            rp = RespuestaPregunta(
                pregunta_id=rdata.get("pregunta_id"),
                tipo=rdata.get("tipo"),
                valor=rdata.get("valor", [])
            )
            respuestas_objs.append(rp)

        instance.respuestas = respuestas_objs
        instance.save()

        # 🆕 Enviar copia por correo también en UPDATE
        email = respondedor_data.get("email") or (instance.respondedor.email if instance.respondedor else None)

        if enviar_copia and email:
            respuestas_list = []
            for rp in respuestas_objs:
                respuestas_list.append({
                    "pregunta": rp.pregunta_id,
                    "respuesta": ", ".join(rp.valor) if isinstance(rp.valor, list) else rp.valor
                })

            send_form_responses_copy(
                recipient_email=email,
                form_title=form_obj.titulo if form_obj else instance.formulario.titulo,
                respuestas_list=respuestas_list
            )
            print("📧 Copia enviada correctamente desde PUT")

        return instance