from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.student.views import StudentViewSet, StudentDocumentViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)

student_router = DefaultRouter()
student_router.register(r'documents', StudentDocumentViewSet, basename='student-document')
student_router.register(r'attendance', AttendanceViewSet, basename='student-attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('students/<int:student_pk>/', include(student_router.urls)),
]
