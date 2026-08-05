from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.course.views import CourseViewSet, BatchViewSet, CourseBatchViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'course-batches', CourseBatchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]