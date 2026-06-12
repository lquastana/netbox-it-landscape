from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_it_landscape'

router = NetBoxRouter()
router.register('business-domains', views.BusinessDomainViewSet)
router.register('business-processes', views.BusinessProcessViewSet)
router.register('applications', views.ApplicationViewSet)
router.register('application-flows', views.ApplicationFlowViewSet)

urlpatterns = router.urls
