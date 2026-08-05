from rest_framework import serializers
from apps.course.models import Course, Batch, CourseBatch


class CourseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class BatchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class CourseBatchSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = CourseBatch
        fields = '__all__'
        read_only_fields = ['coursebatch_id', 'created_at', 'updated_at', 'created_by']
