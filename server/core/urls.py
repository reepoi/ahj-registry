from django.urls import path, include
from django.conf.urls import url
from . import views


urlpatterns = [
    path('ahj/', views.AHJList.as_view(), name="ahj"),
    path('ahj-private/', views.WebpageAHJList.as_view(), name='private'),
    path('edit/', views.EditList.as_view(), name='edit'),
    path('edit/submit/', views.submit_edit, name='edit'),
    path('edit/<str:pk>/', views.edit_detail, name='edit'),
    # path('ahj_csv/', views.ahj_upload, name="upload"),
    path('geo/', include('ahj_gis.urls')),
    path('ahj/<uuid:AHJID>/', views.AHJDetail.as_view(), name="ahj"),
    path('ahj/ownership/', views.owner_to_ahj, name="ahj"),
    path('history/ahj/', views.AHJHistory.as_view(), name="history"),
    path('history/ahj/<uuid:AHJID>/', views.AHJHistory.as_view(), name="history"),
    path('history/address/', views.AddressHistory.as_view(), name="history-address"),
    path('history/contact/', views.ContactHistory.as_view(), name="history-contact"),
    path('history/eng-rev-req/', views.EngineeringReviewRequirementHistory.as_view(), name="history-eng-rev-req"),
    path('history/location/', views.LocationHistory.as_view(), name="history-location"),
    path('login/', views.ObtainAuthTokenUserInfo.as_view(), name='api-token-auth'),
    path('register/', views.CreateUser.as_view(), name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^edit/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<edit_id>[0-9]+)/$',
        views.set_edit_status_email, name='set_edit_status_email')
]
