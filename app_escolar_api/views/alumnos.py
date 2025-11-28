from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import UserSerializer, AlumnoSerializer
from app_escolar_api.models import *
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

class AlumnosAll(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active=1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        return Response(lista, 200)


class AlumnosView(generics.GenericAPIView):
    
    # Permisos por método (Mantenido del "Updated upstream")
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #  CREAR ALUMNO
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Validación del usuario
        user_serializer = UserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, 400)

        # Datos
        email = request.data["email"]
        password = request.data["password"]
        role = request.data["rol"]

        # Validar si ya existe
        if User.objects.filter(email=email).exists():
            return Response({"message": f"Username {email} already exists"}, 400)

        # Crear usuario
        user = User.objects.create(
            username=email,
            email=email,
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            is_active=1
        )
        user.set_password(password)
        user.save()

        # Rol
        group, created = Group.objects.get_or_create(name=role)
        group.user_set.add(user)

        # Crear alumno
        alumno = Alumnos.objects.create(
            user=user,
            matricula=request.data["matricula"],
            curp=request.data["curp"].upper(),
            rfc=request.data["rfc"].upper(),
            fecha_nacimiento=request.data["fecha_nacimiento"],
            edad=request.data["edad"],
            telefono=request.data["telefono"],
            ocupacion=request.data["ocupacion"]
        )

        return Response({"Alumno creado con ID": alumno.id}, 201)

    #  GET alumno por ID 
    def get(self, request, *args, **kwargs):
        alumno_id = request.GET.get("id")

        if not alumno_id:
            return Response({"details": "Falta parámetro id"}, 400)

        alumno = get_object_or_404(Alumnos, id=alumno_id)
        data = AlumnoSerializer(alumno).data
        return Response(data, 200)

    #  EDITAR alumno 
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        alumno_id = request.GET.get("id")

        if not alumno_id:
            return Response({"details": "Falta parámetro id"}, 400)

        alumno = get_object_or_404(Alumnos, id=alumno_id)

        # Editar datos del usuario
        alumno.user.first_name = request.data["first_name"]
        alumno.user.last_name = request.data["last_name"]
        alumno.user.email = request.data["email"]
        alumno.user.username = request.data["email"]
        alumno.user.save()

        # Editar datos del alumno
        alumno.matricula = request.data["matricula"]
        alumno.curp = request.data["curp"].upper()
        alumno.rfc = request.data["rfc"].upper()
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.edad = request.data["edad"]
        alumno.telefono = request.data["telefono"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.save()

        return Response({"details": "Alumno actualizado"}, 200)

    #  ELIMINAR alumno 
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno_id = request.GET.get("id")

        if not alumno_id:
            return Response({"details": "Falta parámetro id"}, 400)

        alumno = get_object_or_404(Alumnos, id=alumno_id)

        try:
            alumno.user.delete()  # Borra al usuario y cascada sobre Alumno
            return Response({"details": "Alumno eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Error al eliminar", "error": str(e)}, 400)