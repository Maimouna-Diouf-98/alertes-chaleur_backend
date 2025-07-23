from django.contrib import admin
from .models import Utilisateur
from .models import Notification

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'role', 'date_naissance', 'localite','sexe','telephone')
    search_fields = ('nom', 'prenom')
    list_filter = ('role', 'localite')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'lu', 'date_envoi')
    list_filter = ('lu', 'date_envoi')
    search_fields = ('titre', 'contenu')