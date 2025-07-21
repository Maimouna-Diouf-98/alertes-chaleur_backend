from django.contrib import admin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'role', 'date_naissance', 'localite','sexe','telephone')
    search_fields = ('nom', 'prenom')
    list_filter = ('role', 'localite')
