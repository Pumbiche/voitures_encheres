from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from cloudinary.models import CloudinaryField
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)

class Voiture(models.Model):
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    annee = models.PositiveIntegerField()
    prix_depart = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = CloudinaryField('image')
    date_pub = models.DateTimeField(auto_now_add=True)
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE)
    if DEBUG==True:
        image = models.ImageField(upload_to='voitures/')
    else:
        image = CloudinaryField('image')

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.annee})"
    

class Enchere(models.Model):
    voiture = models.OneToOneField(Voiture, on_delete=models.CASCADE)
    prix_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    meilleur_offreur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='encheres_meilleures'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    duree_minutes = models.PositiveIntegerField(default=10)
    gagnant = models.ForeignKey(
        User,on_delete=models.SET_NULL, null=True, blank=True, related_name='encheres_gagnees'
    )
    notification_envoyee = models.BooleanField(default=False)
    

    @property
    def date_fin(self):
        return self.date_debut + timezone.timedelta(minutes=self.duree_minutes)

    def est_active(self):
        now = timezone.now()
        return self.date_debut <= now < self.date_fin

    def __str__(self):
        return f"Enchère sur {self.voiture}"
    
class Offre(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    enchere = models.ForeignKey('Enchere', on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_offre = models.DateTimeField(auto_now_add=True)