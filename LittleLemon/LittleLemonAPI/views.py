from .models import *
from .serializers import *

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class MenuItemView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def create(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            return super().create(request)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'No PUT/PATCH method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'No GET method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'No DELETE method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)       

class SingleMenuItemView(MenuItemView):

    def create(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            return Response({'message': 'No POST method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)   
        
    def retrieve(self, request, pk):
        menu_item = self.queryset.filter(pk=pk).first()
        if menu_item:
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(menu_item, context={'request': request})
            return Response(serializer.data)
        return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            return super(viewsets.ModelViewSet, self).update(request, pk)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            super(viewsets.ModelViewSet, self).destroy(request, pk)
            return Response({'message': 'Succesfully deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)


class ManagersView(MenuItemView):

    def create(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            username = request.POST.get('username')
            try:
                user = User.objects.get(username=username)
                user.groups.add(1)
                return Response({'message': 'Added to Manager group'}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'message': 'There is no valid User'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)
        
    queryset = User.objects.filter(groups = 1).all()
    serializer_class = CurrentUserSerializer

class SingleManagersView(SingleMenuItemView):
    queryset = User.objects.filter(groups = 1).all()
    serializer_class = CurrentUserSerializer

class DeliveryCrewView(MenuItemView):
    queryset = User.objects.filter(groups = 2).all()
    serializer_class = CurrentUserSerializer