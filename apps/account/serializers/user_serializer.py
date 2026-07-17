from rest_framework import serializers
from apps.account.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login']

    def validate_role(self, value):
        request = self.context.get('request')
        if request and not request.user.is_staff and value != getattr(self.instance, 'role', None):
            raise serializers.ValidationError('Only admins can change role.')
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if role:
            user.role = role
            user.groups.add(role)
            user.save(update_fields=['role'])
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if role is not None:
            old_role = instance.role
            instance.role = role
            if old_role:
                instance.groups.remove(old_role)
            instance.groups.add(role)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
