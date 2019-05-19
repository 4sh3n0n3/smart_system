from rest_framework import routers

from user_module.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = []
urlpatterns += router.urls
