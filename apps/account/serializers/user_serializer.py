from rest_framework import serializers
from apps.account.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    user_permissions = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_staff', 'is_superuser', 'user_permissions', 'last_login', 'created_at', 'updated_at']

    def get_user_permissions(self, obj):
        return sorted(obj.get_all_permissions())

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if groups:
            user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if groups is not None:
            instance.groups.set(groups)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserMiniSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'is_staff', 'is_superuser', 'branch', 'branch_name', 'groups', 'user_permissions']

    def get_user_permissions(self, obj):
        return sorted(obj.get_all_permissions())
