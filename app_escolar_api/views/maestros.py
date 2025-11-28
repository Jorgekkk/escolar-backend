from django.db.models import *
from django.db import transaction
# Simplifiqué los imports de serializers para evitar redundancia
from app_escolar_api.serializers import *
from app_escolar_api.models import * # <--- ESTO DEBE IR EN OTRA LÍNEA
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
import json

class MaestrosAll(generics.CreateAPIView):
    # Obtener la lista de todos los maestros activos
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestroSerializer(maestros, many=True).data
        # Procesar el campo JSON manualmente para la lista
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    maestro["materias_json"] = []
        return Response(lista, 200)

class MaestrosView(generics.CreateAPIView):
    
    # -------------------------------------------------------------------------
    # GESTIÓN DE PERMISOS
    # -------------------------------------------------------------------------
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    # -------------------------------------------------------------------------
    # OBTENER MAESTRO (GET)
    # -------------------------------------------------------------------------
    def get(self, request, *args, **kwargs):
        maestro_id = request.GET.get("id")
        
        if not maestro_id:
            return Response({"detail": "ID de maestro requerido"}, 400)
        
        try:
            maestro = Maestros.objects.get(id=maestro_id, user__is_active=1)
            maestro_data = MaestroSerializer(maestro).data
            
            # Parsear materias_json si es string
            if "materias_json" in maestro_data and isinstance(maestro_data["materias_json"], str):
                try:
                    maestro_data["materias_json"] = json.loads(maestro_data["materias_json"])
                except Exception:
                    maestro_data["materias_json"] = []
            
            return Response(maestro_data, 200)
            
        except Maestros.DoesNotExist:
            return Response({"detail": "Maestro no encontrado"}, 404)
        except Exception as e:
            return Response({"detail": f"Error al obtener maestro: {str(e)}"}, 400)

    # -------------------------------------------------------------------------
    # REGISTRAR NUEVO MAESTRO (POST)
    # -------------------------------------------------------------------------
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        
        if user_serializer.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            
            # Verificar usuario existente
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response({"message": "Username " + email + ", is already taken"}, 400)
            
            # Crear usuario
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )
            user.set_password(password)
            user.save()
            
            # Asignar grupo/rol
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()
            
            # Crear perfil de maestro
            maestro = Maestros.objects.create(
                user=user,
                id_trabajador=request.data["id_trabajador"],
                fecha_nacimiento=request.data["fecha_nacimiento"],
                telefono=request.data["telefono"],
                rfc=request.data["rfc"].upper(),
                cubiculo=request.data["cubiculo"],
                area_investigacion=request.data["area_investigacion"],
                materias_json=json.dumps(request.data["materias_json"])
            )
            maestro.save()
            
            return Response({"maestro_created_id": maestro.id}, 201)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------------------------
    # ACTUALIZAR DATOS (PUT)
    # -------------------------------------------------------------------------
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        maestro_id = request.data.get("id")
        
        if not maestro_id:
            return Response({"detail": "ID de maestro requerido"}, 400)
        
        try:
            maestro = Maestros.objects.get(id=maestro_id)
            user = maestro.user
            
            # Actualizar datos del User
            if "first_name" in request.data:
                user.first_name = request.data["first_name"]
            
            if "last_name" in request.data:
                user.last_name = request.data["last_name"]
            
            user.save()
            
            # Actualizar datos del Maestro
            fields_to_update = ["id_trabajador", "fecha_nacimiento", "telefono", "cubiculo", "area_investigacion"]
            
            for field in fields_to_update:
                if field in request.data:
                    setattr(maestro, field, request.data[field])

            if "rfc" in request.data:
                maestro.rfc = request.data["rfc"].upper()
            
            if "materias_json" in request.data:
                if isinstance(request.data["materias_json"], list):
                    maestro.materias_json = json.dumps(request.data["materias_json"])
                else:
                    maestro.materias_json = request.data["materias_json"]
            
            maestro.save()
            
            return Response({
                "message": "Maestro actualizado correctamente",
                "maestro_id": maestro.id
            }, 200)
            
        except Maestros.DoesNotExist:
            return Response({"detail": "Maestro no encontrado"}, 404)
        except Exception as e:
            return Response({"detail": f"Error al actualizar maestro: {str(e)}"}, 400)

    # -------------------------------------------------------------------------
    # ELIMINAR MAESTRO (DELETE)
    # -------------------------------------------------------------------------
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        maestro_id = request.GET.get("id")
        
        if not maestro_id:
            return Response({"details": "Falta parámetro id"}, 400)

        maestro = get_object_or_404(Maestros, id=maestro_id)
        
        try:
            maestro.user.delete() 
            return Response({"details": "Maestro eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar", "error": str(e)}, 400)