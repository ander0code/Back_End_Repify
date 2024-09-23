
from rest_framework.routers import DefaultRouter
from usuario.views import Login

router = DefaultRouter()

router.register('login',Login,basename = 'login')

urlpatterns = router.urls