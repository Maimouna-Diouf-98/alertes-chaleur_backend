from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
class UtilisateurManager(BaseUserManager):
    def create_user(self, telephone, nom, prenom, localite, date_naissance, sexe, password=None, role='user'):
        if not telephone:
            raise ValueError("Le téléphone est obligatoire")

        user = self.model(
            telephone=telephone,
            nom=nom,
            prenom=prenom,
            localite=localite,
            date_naissance=date_naissance,
            sexe=sexe,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telephone, nom, prenom, localite, date_naissance, sexe, password):
        user = self.create_user(
            telephone=telephone,
            nom=nom,
            prenom=prenom,
            localite=localite,
            date_naissance=date_naissance,
            sexe=sexe,
            password=password,
            role='admin'
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    PROFIL_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'Utilisateur')
    ]
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    localite = models.CharField(max_length=100)
    sexe = models.CharField(max_length=10, choices=[('homme', 'Homme'), ('femme', 'Femme')])
    telephone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=PROFIL_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

   
    USERNAME_FIELD = 'telephone' 
    REQUIRED_FIELDS = ['nom','prenom', 'localite', 'date_naissance']

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"