
from rest_framework.routers import DefaultRouter
from usuario.views import LoginViewSet 

router = DefaultRouter()

router.register('login',LoginViewSet,basename = 'login')


urlpatterns = router.urls