from .models import *
from .serializers import *

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, renderer_classes, permission_classes, throttle_classes, action
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from datetime import datetime
from decimal import Decimal

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

    def update(self, request, pk, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super(viewsets.ModelViewSet, self).update(request, pk, **kwargs)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            super(viewsets.ModelViewSet, self).destroy(request, pk)
            return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

class ManagersView(MenuItemView):
    group = [1, 'Manager']

    def create(self, request, pk=None):
        if request.user.groups.filter(name='Manager').exists():
            username = request.POST.get('username')
            try:
                user = User.objects.get(username=username)
                user.groups.add(self.group[0])
                return Response({'message': f'Added to {self.group[1]} group'}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'message': 'There is no valid User'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    queryset = User.objects.filter(groups=group[0]).all()
    serializer_class = CurrentUserSerializer

class SingleManagersView(SingleMenuItemView):
    group = [1, 'Manager']
    queryset = User.objects.filter(groups=group[0]).all()
    serializer_class = CurrentUserSerializer

class DeliveryCrewView(ManagersView):
    group = [2, 'Delivery Crew']
    queryset = User.objects.filter(groups=group[0]).all()

class SingleDeliveryCrewView(SingleManagersView):
    group = [2, 'Delivery Crew']
    queryset = User.objects.filter(groups=group[0]).all()

class CartView(viewsets.ModelViewSet):

    def list(self, request):
        queryset = Cart.objects.filter(user=request.user)
        serializer_class = CartSerializer(queryset, many=True, context={'request': request})
        return Response(serializer_class.data)

    def destroy(self, request):
        queryset = Cart.objects.select_related('user').all()
        queryset.delete()
        return Response({'message': 'Card deleted successfully'}, status=status.HTTP_200_OK)

    queryset = Cart.objects.select_related('user').all()
    serializer_class = CartSerializer

class OrderView(viewsets.ModelViewSet):

    def list(self, request):
        if request.user.groups.filter(name='Manager').exists():
            queryset = Order.objects.all()
            serializer_class = OrderSerializer(queryset, many=True, context={'request': request})
            return Response(serializer_class.data)
        elif request.user.groups.filter(name='Delivery').exists():
            queryset = Order.objects.filter(delivery_crew=request.user)
            serializer_class = OrderSerializer(queryset, many=True, context={'request': request})
            return Response(serializer_class.data)
        else:
            queryset = Order.objects.filter(user=request.user)
            serializer_class = OrderSerializer(queryset, many=True, context={'request': request})
            return Response(serializer_class.data)

    def create(self, request):
        cart = Cart.objects.filter(user=request.user)

        if cart:
            totalprice = Decimal(0)
            for item in cart:
                totalprice += item.price

            order = Order.objects.create(user=request.user, status=0, total=totalprice)
            order.save()

            for item in cart:
                orderitem = OrderItem(order=order, menuitem=item.menuitem, quantity=item.quantity,
                                      unit_price=item.unit_price, price=item.price).save()

            cart.delete()
            serializer_class = OrderSerializer(order)
            return Response({'message': 'Created Order', 'Order': serializer_class.data}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Your cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)

    queryset = Order.objects.select_related('user').all()
    serializer_class = OrderSerializer

class SingleOrderView(viewsets.ModelViewSet):

    def retrieve(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user == order.user or request.user.groups.filter(name='Manager').exists() or request.user == order.delivery_crew:
            orderquery = OrderItem.objects.filter(order=order)
            serializer_class = OrderItemSerializer(orderquery, many=True)
            return Response({'order': order.pk, 'items': serializer_class.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk):
        order = Order.objects.get(pk=pk)
        if request.user.groups.filter(name='Manager').exists() or order.delivery_crew == request.user:
            order = Order.objects.get(pk=pk)
            status_for_order = request.POST.get('status')
            if status_for_order:
                order.status = status_for_order
                order.save()
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.groups.filter(name='Manager').exists():
            delivery_crew = request.POST.get('delivery_crew')
            if delivery_crew:
                delivery_crew = User.objects.get(username=delivery_crew)
                order.delivery_crew = delivery_crew
                order.save()

        serializer_class = OrderSerializer(order)
        return Response({'message': 'Order status changed', 'Order': serializer_class.data}, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response({'message': 'Order deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not in the right group'}, status=status.HTTP_403_FORBIDDEN)

queryset = OrderItem.objects.select_related('order').all()
serializer_class = OrderSerializer
