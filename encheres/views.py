from datetime import timedelta  # OK si tu manipules des durées

from django.contrib import messages  # Pour afficher des messages flash, OK
from django.contrib.auth import login, logout  # Pour gérer les sessions utilisateurs, OK
from django.contrib.auth.decorators import login_required  # Pour protéger les vues, OK
from django.core.mail import send_mail  # Si tu envoies des mails, OK
from django.http import JsonResponse  # Pour renvoyer du JSON, OK
from django.shortcuts import render, redirect  # Pour les vues, OK
from django.utils import timezone  # Pour gérer la date/heure, OK
import logging  # Pour logger, OK

from .forms import RegisterForm, OffreForm  # Tes formulaires locaux, OK
from .models import Voiture, Enchere  # Tes modèles locaux, OK

from django.db import transaction  # Pour les transactions atomiques, OK
from decimal import Decimal  # Pour manipuler les nombres décimaux précis, OK

from django_ratelimit.decorators import ratelimit  # Si tu utilises la limitation de requêtes, OK
from django.views.decorators.http import require_POST  # Pour restreindre les méthodes HTTP, OK
from django.views.decorators.csrf import csrf_protect

from .models import Offre



def accueil(request):
    return render(request, 'encheres/accueil.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Comme set_password est géré dans form.save(), on appelle juste form.save()
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}, votre compte a été créé avec succès !")
            return redirect('accueil')
    else:
        form = RegisterForm()
    return render(request, 'encheres/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accueil')


def voitures_list(request):
    voitures = Voiture.objects.all()
    return render(request, 'encheres/voitures_list.html', {'voitures': voitures})


logger = logging.getLogger('encheres')

@login_required
@ratelimit(key='user', rate='60s/m', method='POST', block=True)
def enchere_en_cours(request):
    maintenant = timezone.now()
    encheres = Enchere.objects.filter(date_debut__lte=maintenant)
    enchere = None
    for e in encheres:
        fin = e.date_debut + timedelta(minutes=e.duree_minutes)
        if fin >= maintenant:
            enchere = e
            break

    if not enchere:
        messages.info(request, "Aucune enchère en cours.")
        return redirect('accueil')

    if request.method == 'POST':
        form = OffreForm(request.POST)
        if form.is_valid():
            offre = form.cleaned_data['offre']
            try:
                with transaction.atomic():
                    # Recharger enchere en base pour s'assurer d'avoir les données à jour
                    enchere_db = Enchere.objects.select_for_update().get(pk=enchere.pk)
                    fin = enchere_db.date_debut + timedelta(minutes=enchere_db.duree_minutes)
                    if timezone.now() > fin:
                        messages.error(request, "L'enchère est terminée.")
                    elif offre <= enchere_db.prix_actuel + Decimal('99.99'):
                        form.add_error('offre', "L'offre doit être supérieure au prix actuel + 99,99 €.")
                    else:
                        enchere_db.prix_actuel = offre
                        enchere_db.gagnant = request.user
                        enchere_db.save()
                        messages.success(request, "Votre offre a été enregistrée avec succès.")
                        ip = request.META.get('REMOTE_ADDR', 'IP inconnue')
                        logger.info(f"Nouvelle enchère de {user} : {offre} € sur objet #{enchere.pk} depuis IP {ip}")
                        return redirect('enchere_en_cours')
            except Enchere.DoesNotExist:
                messages.error(request, "Enchère introuvable.")
        # en cas d'erreur, on continue et on réaffiche le formulaire avec erreurs
    else:
        form = OffreForm()

    fin = enchere.date_debut + timedelta(minutes=enchere.duree_minutes)
    temps_restant = max(0, (fin - maintenant).total_seconds())

    return render(request, 'encheres/enchere_en_cours.html', {
        'enchere': enchere,
        'temps_restant': int(temps_restant),
        'form': form,
    })


@login_required
def enchere_terminee(request):
    maintenant = timezone.now()
    encheres_terminees = Enchere.objects.filter(date_debut__lte=maintenant).order_by('-date_debut')
    terminees = [e for e in encheres_terminees if e.date_debut + timedelta(minutes=e.duree_minutes) <= maintenant]

    enchere = terminees[0] if terminees else None
    if not enchere:
        messages.info(request, "Aucune enchère terminée pour le moment.")
        return redirect('enchere_en_cours')

    est_gagnant = enchere.gagnant == request.user
    return render(request, 'encheres/enchere_terminee.html', {
        'enchere': enchere,
        'est_gagnant': est_gagnant,
    })


@login_required
def enchere_gagnee(request):
    maintenant = timezone.now()
    encheres = Enchere.objects.filter(gagnant=request.user)
    gagnees = [e for e in encheres if e.date_debut + timedelta(minutes=e.duree_minutes) <= maintenant]

    enchere = sorted(gagnees, key=lambda e: e.date_debut + timedelta(minutes=e.duree_minutes), reverse=True)[0] if gagnees else None

    return render(request, 'encheres/enchere_gagnee.html', {
        'enchere': enchere
    })


def notifier_gagnant(enchere):
    if enchere.gagnant and not enchere.notification_envoyee:
        send_mail(
            subject='Félicitations ! Vous avez remporté l’enchère',
            message=f"Bonjour {enchere.gagnant.username},\n\nVous avez remporté l’enchère pour le véhicule : {enchere.voiture} avec une offre de {enchere.prix_actuel} €.",
            from_email=None,
            recipient_list=[enchere.gagnant.email],
            fail_silently=False,
        )
        enchere.notification_envoyee = True
        enchere.save()


def enchere_status(request):
    maintenant = timezone.now()
    encheres = Enchere.objects.filter(date_debut__lte=maintenant).order_by('date_debut')
    enchere = next((e for e in encheres if e.date_debut + timedelta(minutes=e.duree_minutes) >= maintenant), None)

    if enchere:
        fin = enchere.date_debut + timedelta(minutes=enchere.duree_minutes)
        temps_restant = max(0, (fin - maintenant).total_seconds())
        data = {
            "prix_actuel": enchere.prix_actuel,
            "temps_restant": int(temps_restant)
        }
    else:
        data = {
            "prix_actuel": None,
            "temps_restant": 0
        }
    return JsonResponse(data)

@csrf_protect
@require_POST
@login_required
def soumettre_offre(request):
    now = timezone.now()
    enchere_active = None

    for enchere in Enchere.objects.all():
        if enchere.est_active():
            enchere_active = enchere
            break

    if not enchere_active:
        return JsonResponse({'success': False, 'error': "Aucune enchère active."})

    # Ensuite, tu peux continuer avec enchere_active au lieu de enchere
    if enchere_active.date_fin < now:
        return JsonResponse({'success': False, 'error': "L'enchère est terminée."})

    try:
        offre = float(request.POST.get('offre', '0'))
    except ValueError:
        return JsonResponse({'success': False, 'error': "Montant invalide."})

    minimum_requis = enchere.prix_actuel + Decimal('0.01')
    if Decimal(str(offre)) < minimum_requis:
        return JsonResponse({
            'success': False,
            'error': f"L'offre doit être supérieure à {minimum_requis:.2f} €"
    })

    Offre.objects.create(utilisateur=request.user, enchere=enchere_active, montant=offre)

    enchere_active.prix_actuel = offre
    enchere_active.save()

    return JsonResponse({'success': True, 'nouveau_prix': offre})

