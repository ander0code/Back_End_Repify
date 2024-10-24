
from rest_framework.routers import DefaultRouter
from usuario.views import LoginViewSet, PublicacionViewSet, PerfilViewSet

router = DefaultRouter()

router.register('login',LoginViewSet,basename = 'login')
router.register('projects', PublicacionViewSet, basename='projects')
router.register('perfil',PerfilViewSet, basename= 'perfil')

urlpatterns = router.urls