# usuarioapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from usuarioapp.models import Usuario
from usuarioapp.serializers import UsuarioSerializer
from bson import ObjectId


class UsuarioListCreateAPI(APIView):
    """GET: listar todos los usuarios
       POST: crear nuevo usuario"""
    
    def get(self, request):
        usuarios = Usuario.objects()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                "message": "Usuario creado correctamente",
                "id": str(usuario.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioDetailAPI(APIView):
    """GET, PUT, DELETE por ID"""

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
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario actualizado correctamente"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        usuario = self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        usuario.delete()
        return Response({"message": "Usuario eliminado"}, status=status.HTTP_204_NO_CONTENT)


# Create your views here.
