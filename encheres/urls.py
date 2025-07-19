from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Page d'accueil de l'app enchères : /encheres/
    path('', views.accueil, name='accueil'),

    # Liste des voitures : /encheres/voitures/
    path('voitures/', views.voitures_list, name='voitures_list'),

    # Gestion utilisateur, si tu souhaites les mettre ici (sinon tu peux les gérer au niveau projet)
    path('login/', auth_views.LoginView.as_view(template_name='encheres/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
    path('register/', views.register, name='register'),

    # Enchère en cours : /encheres/enchere/
    path('enchere/', views.enchere_en_cours, name='enchere_en_cours'),

    # API pour obtenir le status de l'enchère (JSON) : /encheres/api/enchere_status/
    path('encheres/api/enchere_status/', views.enchere_status, name='enchere_status'),

    # URL pour soumettre une offre via AJAX : /encheres/soumettre_offre/
    path('soumettre_offre/', views.soumettre_offre, name='soumettre_offre'),
    
]