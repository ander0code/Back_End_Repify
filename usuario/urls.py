
from rest_framework.routers import DefaultRouter
from usuario.views import LoginViewSet, PublicacionViewSet, PerfilViewSet, FormsViewSet

router = DefaultRouter()

router.register('login',LoginViewSet,basename = 'login')
router.register('projects', PublicacionViewSet, basename='projects')
router.register('perfil',PerfilViewSet, basename= 'perfil')
router.register('form',FormsViewSet, basename= 'form')

urlpatterns = router.urls