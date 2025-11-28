from django.db.models import *
from app_escolar_api.serializers import *
from app_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if user.is_active:
            # Obtener perfil y roles del usuario
            roles = user.groups.all()
            
            if not roles.exists():
                return Response(
                    {"detail": "Usuario sin rol asignado"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Si solo es un rol específico asignamos el elemento 0
            role_name = roles.first().name.lower()  # Convertir a minúsculas para evitar errores
            
            # Esta función genera la clave dinámica (token) para iniciar sesión
            token, created = Token.objects.get_or_create(user=user)
            
            # Verificar que tipo de usuario quiere iniciar sesión
            if role_name == 'alumno':
                alumno = Alumnos.objects.filter(user=user).first()
                if not alumno:
                    return Response(
                        {"detail": "Perfil de alumno no encontrado"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                alumno_data = AlumnoSerializer(alumno).data
                alumno_data["token"] = token.key
                alumno_data["rol"] = "alumno"
                return Response(alumno_data, status=status.HTTP_200_OK)
            
            elif role_name == 'maestro':
                maestro = Maestros.objects.filter(user=user).first()
                if not maestro:
                    return Response(
                        {"detail": "Perfil de maestro no encontrado"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                maestro_data = MaestroSerializer(maestro).data
                maestro_data["token"] = token.key
                maestro_data["rol"] = "maestro"
                return Response(maestro_data, status=status.HTTP_200_OK)
            
            elif role_name == 'administrador':
                user_data = UserSerializer(user, many=False).data
                user_data['token'] = token.key
                user_data["rol"] = "administrador"
                return Response(user_data, status=status.HTTP_200_OK)
            
            else:
                return Response(
                    {"detail": f"Rol '{role_name}' no reconocido"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
        return Response(
            {"detail": "Usuario inactivo"}, 
            status=status.HTTP_403_FORBIDDEN
        )


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        if user.is_active:
            try:
                token = Token.objects.get(user=user)
                token.delete()
                return Response({'logout': True}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response(
                    {'detail': 'Token no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {'logout': False, 'detail': 'Usuario inactivo'}, 
            status=status.HTTP_403_FORBIDDEN
        )