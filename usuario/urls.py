
from rest_framework.routers import DefaultRouter
from usuario.views import LoginViewSet, PublicacionViewSet 

router = DefaultRouter()

router.register('login',LoginViewSet,basename = 'login')
router.register('projects', PublicacionViewSet, basename='projects')

urlpatterns = router.urls