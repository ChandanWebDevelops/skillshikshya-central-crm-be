from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.student.views import StudentViewSet, StudentDocumentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)

student_router = DefaultRouter()
student_router.register(r'documents', StudentDocumentViewSet, basename='student-document')

urlpatterns = [
    path('', include(router.urls)),
    path('students/<int:student_pk>/', include(student_router.urls)),
]
