from django.core.management.base import BaseCommand
from django.utils import timezone
from encheres.models import Enchere

class Command(BaseCommand):
    help = 'Supprime les enchères terminées'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        encheres_a_supprimer = [e for e in Enchere.objects.all() if e.date_fin <= now]

        for enchere in encheres_a_supprimer:
            self.stdout.write(f"Suppression de l'enchère sur {enchere.voiture}")
            enchere.delete()

        self.stdout.write(self.style.SUCCESS(f"{len(encheres_a_supprimer)} enchère(s) supprimée(s)."))