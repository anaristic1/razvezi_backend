from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import Route, RouteStatusHistory, Status
from .serializers import RouteSerializer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def createRouteStatusHistory(route, status, user):
    RouteStatusHistory.objects.create(
        route=route,
        status=status,
        changed_by=user,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "routes",
        {
            "type": "route_update",
            "message": "Hello, world!"
        }
    )


class IsDriverForWrite(BasePermission):
    def has_permission(self, request, view):
        # Allow all read-only methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated and
            request.user.role == 'driver'
        )


class RouteList(generics.ListCreateAPIView):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(
            Q(status=1),
            date_created__date=timezone.localdate()
        )

class UserCreatedRoutes(generics.ListCreateAPIView):
    """ Routes that are today created by user."""
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Route.objects.filter(
            created_by=user,
            date_created__date=timezone.localdate(),
        )


class DriverRoutes(generics.ListCreateAPIView):
    """ Driver will not see his finished rides. """
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Route.objects.filter(
            Q(status=2) | Q(status=3),
            taken_by=user,
            date_created__date=timezone.localdate(),
        )


def route_history(request, route_id):
    history = RouteStatusHistory.objects.filter(route_id=route_id)

    data = [
        {
            "status": h.status,
            "changed_by": h.changed_by.username,
            "changed_at": h.changed_at,
        }
        for h in history
    ]

    return JsonResponse(data, safe=False)


class DriverTakesProductView(APIView):
    def post(self, request, route_id):
        user = request.user
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return JsonResponse({"success": False, "message": "Route not found"}, status=status.HTTP_400_BAD_REQUEST)

        print('route found')

        if route.status == Status.PRIHVACEN and user == route.taken_by:
            route.status = Status.PREUZETO
            route.save()
            createRouteStatusHistory(route=route, status=Status.PREUZETO, user=user)
            return JsonResponse({"success": True, "message": "Sucess."}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"success": False, "message": "Route not taken. Check status or user."}, status=status.HTTP_400_BAD_REQUEST)


class IsRouteOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class DispatcherClosesRoute(APIView):
    """ UzunMirkova moze da zatvori rutu koju je napravila """
    permission_classes = [IsAuthenticated, IsRouteOwner]

    def post(self, request, route_id):
        user = request.user
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return JsonResponse({"success": False, "message": "Route not found"},
                                status=status.HTTP_400_BAD_REQUEST)

        if route.status in (Status.PREUZETO, Status.ZAVRSEN, Status.OTKAZAN):
            return JsonResponse({"success": False, "message": "Route can't be stopped"},
                                status=status.HTTP_400_BAD_REQUEST)

        if route.status in (Status.NOV, Status.PRIHVACEN):
            route.status = Status.OTKAZAN
            route.save()
            createRouteStatusHistory(route=route, status=Status.OTKAZAN, user=user)
            return JsonResponse({"success": True, "message": "Sucess."}, status=status.HTTP_200_OK)


class DriverFinishesRouteView(APIView):
    """zavrsena ruta, ne prikazuje se u listi njegovih ruta """

    def post(self, request, route_id):
        user = request.user
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return JsonResponse({"success": False, "message": "Route not found"},
                                status=status.HTTP_400_BAD_REQUEST)

        if route.status == Status.PREUZETO and user == route.taken_by:
            route.status = Status.ZAVRSEN
            route.save()
            createRouteStatusHistory(route=route, status=Status.ZAVRSEN, user=user)
            return JsonResponse({"success": True, "message": "Sucess."}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"success": False, "message": "Route not taken. Check status or user."},
                                status=status.HTTP_400_BAD_REQUEST)


class RouteDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated, IsDriverForWrite]
    queryset = Route.objects.all()
    lookup_field = "id"

    def perform_update(self, serializer):
        serializer.save(
            taken_by=self.request.user,
        )
        createRouteStatusHistory(route= serializer.instance, status=Status.PRIHVACEN, user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_route(request):
    serializer = RouteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        createRouteStatusHistory(route=serializer.instance, status=Status.NOV, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if user:
            login(request, user)
            return Response(
                {
                    "user": {
                        "username": user.username,
                        "role": user.role,
                    }
                 },
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message":"Logged out"})
