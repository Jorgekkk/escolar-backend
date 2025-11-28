from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import MateriaSerializer
from app_escolar_api.models import Materias, Maestros
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class MateriasAll(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        serializer = MateriaSerializer(materias, many=True)
        return Response(serializer.data, 200)

class MateriasView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # OBTENER UNA MATERIA POR ID 
    def get(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        if not materia_id:
            return Response({"details": "Falta parámetro id"}, 400)
        
        materia = get_object_or_404(Materias, id=materia_id)
        serializer = MateriaSerializer(materia)
        return Response(serializer.data, 200)

    # REGISTRAR NUEVA MATERIA
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if Materias.objects.filter(nrc=request.data.get("nrc")).exists():
             return Response({"message": "El NRC ya existe en la base de datos"}, 400)

        # Preparar datos
        data = request.data.copy()
        
        # Validar profesor
        profesor_id = data.get("profesor")
        if profesor_id:
            if not Maestros.objects.filter(id=profesor_id).exists():
                 return Response({"message": "El profesor seleccionado no existe"}, 400)

        serializer = MateriaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"materia_created_id": serializer.data['id']}, 201)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ACTUALIZAR MATERIA
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia_id = request.GET.get("id") or request.data.get("id")
        materia = get_object_or_404(Materias, id=materia_id)

        serializer = MateriaSerializer(materia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Materia actualizada correctamente"}, 200)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ELIMINAR MATERIA
    def delete(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        materia = get_object_or_404(Materias, id=materia_id)
        materia.delete()
        return Response({"message": "Materia eliminada correctamente"}, 200)