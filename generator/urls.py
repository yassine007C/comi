from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('generate/', views.generate_view, name='generate'),
    path('gallery/', views.image_gallery, name='gallery'),
]
