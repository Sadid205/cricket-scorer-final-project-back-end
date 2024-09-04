from rest_framework import serializers
from .models import Author
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password','confirm_password']

    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password!=confirm_password:
            raise serializers.ValidationError({"Error":"Password doesn't matched."})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"Error":"Email is already exists"})
        user_account = User(username=username,email=email,first_name=first_name,last_name=last_name)
        user_account.set_password(password)
        user_account.is_active = False
        user_account.save()
        new_author = Author(user=user_account)
        new_author.save()
        return user_account

class AuthorLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)