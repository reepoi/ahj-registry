from django.urls import path, include
# from django.conf.urls import url
from . import views

urlpatterns = [
    path('location/', views.find_ahj_location, name='location'),
    path('address/', views.find_ahj_address, name='address')
]

# urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]