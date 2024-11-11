
from rest_framework.routers import DefaultRouter
from usuario.views import LoginViewSet, ProjectViewSet, PerfilViewSet, FormsViewSet,UserAchievementsViewSet,ApplicationsViewSet,NotificationsViewSet,CollaboratorsViewSet,MetricsViewSet

router = DefaultRouter()

router.register('login',LoginViewSet,basename = 'login')
router.register('projects', ProjectViewSet, basename='projects')
router.register('perfil',PerfilViewSet, basename= 'perfil')
router.register('form',FormsViewSet, basename= 'form')
router.register('achievement',UserAchievementsViewSet, basename= 'achievement')
router.register('applications',ApplicationsViewSet, basename= 'applications')
router.register('notifications',NotificationsViewSet, basename= 'notifications')
router.register('collaborators',CollaboratorsViewSet, basename= 'collaborators')
router.register('metrics',MetricsViewSet, basename= 'metrics')

urlpatterns = router.urls