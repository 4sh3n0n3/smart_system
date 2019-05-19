from rest_framework import routers


from .views import CourseCardViewSet, CourseContainerViewSet, CourseRequestViewSet, ContainerRelationViewSet

router = routers.DefaultRouter()
router.register(r'cards', CourseCardViewSet)
router.register(r'containers', CourseContainerViewSet)
router.register(r'requests', CourseRequestViewSet)
router.register(r'containerrelations', ContainerRelationViewSet)

urlpatterns = []
urlpatterns += router.urls

