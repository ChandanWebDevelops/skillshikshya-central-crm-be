from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.lead.views import (
    LeadSourceViewSet, CampaignViewSet, LeadStatusViewSet,
    LeadPriorityViewSet, LeadTagViewSet, LeadViewSet,
    LeadCourseInterestViewSet, EnrollmentViewSet, PaymentViewSet,
    LeadCallViewSet, LeadActivityViewSet, FollowUpViewSet, LeadDocumentViewSet,
)

router = DefaultRouter()
router.register(r'lead-sources', LeadSourceViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'lead-statuses', LeadStatusViewSet)
router.register(r'lead-priorities', LeadPriorityViewSet)
router.register(r'lead-tags', LeadTagViewSet)
router.register(r'leads', LeadViewSet)

lead_router = DefaultRouter()
lead_router.register(r'calls', LeadCallViewSet, basename='lead-call')
lead_router.register(r'activities', LeadActivityViewSet, basename='lead-activity')
lead_router.register(r'followups', FollowUpViewSet, basename='lead-followup')
lead_router.register(r'documents', LeadDocumentViewSet, basename='lead-document')
lead_router.register(r'course-interests', LeadCourseInterestViewSet, basename='lead-course-interest')
lead_router.register(r'enrollments', EnrollmentViewSet, basename='lead-enrollment')

enrollment_router = DefaultRouter()
enrollment_router.register(r'payments', PaymentViewSet, basename='enrollment-payment')

urlpatterns = [
    path('', include(router.urls)),
    path('leads/<int:lead_pk>/', include(lead_router.urls)),
    path('leads/<int:lead_pk>/enrollments/<int:enrollment_pk>/', include(enrollment_router.urls)),
]
