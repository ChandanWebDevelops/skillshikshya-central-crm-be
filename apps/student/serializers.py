from rest_framework import serializers
from apps.student.models import Student, StudentDocument


class StudentListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    assigned_counselor_name = serializers.CharField(source='assigned_counselor.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'full_name', 'phone', 'email',
            'gender', 'status', 'enrolled_at', 'branch_name',
            'source_name', 'assigned_counselor_name', 'created_by_name',
            'created_at',
        ]


class StudentSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    assigned_counselor_name = serializers.CharField(source='assigned_counselor.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = [
            'student_id', 'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]

    def get_document_count(self, obj):
        return obj.documents.count()


class StudentDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)

    class Meta:
        model = StudentDocument
        fields = '__all__'
        read_only_fields = ['student', 'uploaded_by', 'uploaded_at']
