from rest_framework.routers import DefaultRouter
from .views import SimilarUsersViewSet

router = DefaultRouter()
router.register(r'similitudes_user', SimilarUsersViewSet, basename='similitudes_user')

urlpatterns = router.urls