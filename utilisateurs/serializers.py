from rest_framework import serializers
from .models import Utilisateur
from .models import Notification
class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ('id', 'nom', 'prenom', 'date_naissance', 'localite', 'role', 'password', 'sexe','telephone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Utilisateur.objects.create_user(
            nom=validated_data['nom'],
            prenom=validated_data['prenom'],
            telephone= validated_data['telephone'],
            sexe= validated_data['sexe'],
            date_naissance=validated_data.get('date_naissance'),
            localite=validated_data['localite'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
