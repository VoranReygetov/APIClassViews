from .models import *
from rest_framework import serializers
from decimal import Decimal
from rest_framework.validators import UniqueValidator
from .utils import bleachvalidate
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth.models import User, Group
from django.db import IntegrityError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'slug': {
                'validators': [UniqueValidator(queryset=Category.objects.all())]
            }
        }

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        if 'title' in self.context['request'].data:
            bleachvalidate(attrs, 'title')
            return super().validate(attrs)
        return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        depth = 1
        extra_kwargs = {
            'price': {'min_value': 0.01},
        }

class GroupsSerializerForUser(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group']
        extra_kwargs = {
            'group': {'source': 'name'},
        }

class CurrentUserSerializer(serializers.ModelSerializer):
    groups = GroupsSerializerForUser(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'groups']
        depth = 1

class CartSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

    def fullprice(self, product: Cart):
        return product.menuitem.price * product.quantity

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantitynow = validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantitynow
        try:
            cart = Cart.objects.create(user=user, menuitem=menuitem, quantity=quantitynow, unit_price=unit_price, price=price)
            return cart
        except IntegrityError:
            cartnow = Cart.objects.filter(user=user, menuitem=menuitem).first()
            cartnow.quantity = quantitynow
            cartnow.price = cartnow.unit_price * cartnow.quantity
            cartnow.save()
            return cartnow

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'date', 'user', 'delivery_crew']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']
