from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPIView, LoginAPIView, ListeUtilisateursAPIView,MeteoVigilanceAPIView, MeteoPersonnaliseeAPIView, AlerteAdminAPIView


urlpatterns = [
 
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('utilisateurs/', ListeUtilisateursAPIView.as_view()),
    path('meteo-vigilance/', MeteoVigilanceAPIView.as_view()),
    path('meteo-prevision/', MeteoPersonnaliseeAPIView.as_view()),
    path('alerte/', AlerteAdminAPIView.as_view(),),
]

