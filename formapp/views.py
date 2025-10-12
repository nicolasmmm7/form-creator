
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from formapp.models import Formulario
from formapp.serializers import FormularioSerializer

class FormularioListCreateAPI(APIView):
    """GET: listar formularios
       POST: crear nuevo formulario"""

    def get(self, request):
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
    #actualizar
    def put(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormularioSerializer(formulario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Formulario actualizado correctamente"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #borrar
    def delete(self, request, id):
        formulario = self.get_object(id)
        if not formulario:
            return Response({"error": "Formulario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        formulario.delete()
        return Response({"message": "Formulario eliminado"}, status=status.HTTP_204_NO_CONTENT)