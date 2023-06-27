from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from sensecity_africa.photos import views as photos_views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r"photos", photos_views.PhotoViewSet)
router.register(
    r"random-photos", photos_views.RandomPhotoViewSet, basename="random-photo"
)


app_name = "api"
urlpatterns = router.urls
