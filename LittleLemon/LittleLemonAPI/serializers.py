from .models import *
from rest_framework import serializers
from decimal import Decimal
from rest_framework.validators import UniqueValidator
from .utils import bleachvalidate
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
            model = Category
            fields = '__all__'
            extra_kwargs = {
            'slug': {
            'validators': [
            UniqueValidator(queryset=Category.objects.all())]
            }}

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    def validate(self, attrs):
        bleachvalidate(attrs, 'title')
        return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = ['id','title','price', 'featured','category', 'category_id']
        depth=1
        extra_kwargs = {
            'price':{'min_value':0.01},
            }       #min vals for variables
    

class GroupsSerializerForUser(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group']
        extra_kwargs = {
            'group':{'source':'name'},
            }       #min vals for variables


class CurrentUserSerializer(serializers.ModelSerializer):
    # groups = serializers.StringRelatedField(read_only=True)
    groups = GroupsSerializerForUser(many=True)
    class Meta:
        model = User
        fields = ['id','username', 'groups']
        depth=1


