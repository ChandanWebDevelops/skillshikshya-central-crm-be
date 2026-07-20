from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.course.views import CourseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
