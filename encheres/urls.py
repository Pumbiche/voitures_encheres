from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('voitures/', views.voitures_list, name='voitures_list'),
    path('login/', auth_views.LoginView.as_view(template_name='encheres/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
    path('register/', views.register, name='register'),
    path('', views.accueil, name='accueil'),
    path('voitures/', views.voitures_list, name='voitures_list'),
    path('enchere/', views.enchere_en_cours, name='enchere_en_cours'),
    path('encheres/api/enchere_status/', views.enchere_status, name='enchere_status'),
    path('enchere/<int:enchere_id>/offre/', views.soumettre_offre, name='soumettre_offre'),
    path('', views.accueil, name='accueil'),
    ]
