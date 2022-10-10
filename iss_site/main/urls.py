from django.urls import path
from . import views

urlpatterns = [
    path('', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path('camera', views.Camera, name='camera'),
    path('cam', views.Cam, name='cam'),
    path('settings/<int:pk>', views.ProfileUpdate.as_view(), name='settings'),
    path('api/status', views.GetStatus.as_view(), name='statusapi')
]