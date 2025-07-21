from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Utilisateur
from .serializers import UtilisateurSerializer
from api_meteo.services import get_weather_by_city
from api_meteo.services import get_forecast_by_city_and_date
from datetime import date, datetime
from api_meteo.sms_orange import  envoyer_sms
from rest_framework.permissions import IsAdminUser

CONDITIONS_METEO_FR = {
    "clear sky": "ciel dégagé",
    "few clouds": "quelques nuages",
    "scattered clouds": "nuages épars",
    "broken clouds": "nuages fragmentés",
    "overcast clouds": "ciel couvert",
    "shower rain": "pluie éparse",
    "light rain": "pluie légère",
    "moderate rain": "pluie modérée",
    "heavy intensity rain": "pluie forte",
    "rain": "pluie",
    "thunderstorm": "orage",
    "light snow": "faibles chutes de neige",
    "snow": "neige",
    "mist": "brume",
    "haze": "brume sèche",
    "fog": "brouillard",
    "smoke": "fumée",
    "sand": "sable",
    "dust": "poussière",
    "squalls": "rafales de vent",
    "tornado": "tornade"
}



class ListeUtilisateursAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'admin':
            return Response({'detail': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        
        utilisateurs = Utilisateur.objects.all()
        serializer = UtilisateurSerializer(utilisateurs, many=True)
        return Response(serializer.data)

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UtilisateurSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message':'Inscription Reussi',
                'user_id': user.id,
                'nom': user.nom,
                'prenom': user.prenom,
                'localite': user.localite,
                'role':user.role,
                'sexe':user.sexe,
                'telephone':user.telephone,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        nom = request.data.get('nom')
        password = request.data.get('password')
        
        user = authenticate(nom=nom, password=password) 
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message':'Connexion Reussi!',
                'user_id': user.id,
                'nom': user.nom,
                'prenom': user.prenom,
                'localite': user.localite,
                'role':user.role,
                'sexe':user.sexe,
                'telephone':user.telephone,
            })

        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)
   
class MeteoVigilanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        utilisateur = request.user
        ville = utilisateur.localite

        data = get_weather_by_city(ville)

        main_data = data.get('main')
        if not main_data:
            return Response({'error': 'Données météo indisponibles ou ville non trouvée'}, status=status.HTTP_400_BAD_REQUEST)

        temperature = main_data.get('temp')
        description_en = data['weather'][0]['description']
        description = CONDITIONS_METEO_FR.get(description_en.lower().strip(), f"{description_en} (non traduit)")

        return Response({
            'ville': ville,
            'date': date.today().isoformat(),
            'temperature': temperature,
            'conditions': description
        })

class MeteoPersonnaliseeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        ville = request.data.get('ville')
        date_str = request.data.get('date')  # format: "YYYY-MM-DD"
        utilisateur = request.user
        


        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return Response({'error': 'Date invalide (format attendu: YYYY-MM-DD)'}, status=400)

        forecast = get_forecast_by_city_and_date(ville, target_date)
        if not forecast:
            return Response({'error': 'Prévision indisponible pour cette date'}, status=400)

        temp = forecast['main']['temp']
        description_en = forecast['weather'][0]['description']
        description = CONDITIONS_METEO_FR.get(description_en.lower().strip(), f"{description_en} (non traduit)")

        if temp < 10:
            niveau = "Froid"
            conseils = "Couvrez-vous bien et évitez de rester dehors longtemps."
        elif 10 <= temp < 18:
            niveau = "Fraîcheur"
            conseils = "Portez des vêtements adaptés à la fraîcheur."
        elif 18 <= temp < 25:
            niveau = "Tempéré"
            conseils = "Température agréable. Restez actif et hydratez-vous."
        elif 25 <= temp <= 30:
            niveau = "Chaud"
            conseils = "Buvez régulièrement de l’eau et évitez les efforts physiques."
        else:
            niveau = "Très chaud"
            conseils = "Restez à l’ombre, hydratez-vous et évitez toute exposition prolongée."

        return Response({
            'ville': ville,
            'date': date_str,
            'temperature': temp,
            'conditions': description,
            'niveau_temperature': niveau,
            'conseils': conseils,
        })

class AlerteAdminAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        admin_user = request.user
        if admin_user.role != 'admin':
            return Response({'detail': 'Accès refusé. Seuls les administrateurs peuvent envoyer des alertes.'},
                            status=status.HTTP_403_FORBIDDEN)

        user_ids = request.data.get('user_ids', [])
        localites = request.data.get('localites', [])

        users = Utilisateur.objects.all()
        if user_ids:
            users = users.filter(id__in=user_ids)
        if localites:
            users = users.filter(localite__in=localites)

        results = []
        for user in users:
            ville = user.localite
            data = get_weather_by_city(ville)
            if not data or 'main' not in data:
                results.append({'user': user.id, 'status': 'fail', 'reason': 'Météo non disponible'})
                continue

            temp = data['main']['temp']
            desc_en = data['weather'][0]['description']
            desc_fr = CONDITIONS_METEO_FR.get(desc_en.lower().strip(), desc_en)

            # Message personnalisé selon profil
            message = f"Alerte météo pour {ville} : {desc_fr}, {temp}°C."
            age = (date.today() - user.date_naissance).days // 365 if user.date_naissance else None
            sexe = user.sexe

            if temp >= 35 or desc_en.lower() in ["thunderstorm", "heavy intensity rain", "squalls"]:
                if age is not None:
                    if age <= 10:
                        message += " Enfant : reste à l'abri et hydrate-toi bien."
                    elif sexe == 'femme' and 15 <= age <= 45:
                        message += " Femmes enceintes : prudence et évitez les efforts."
                    elif sexe == 'homme' and 15 <= age <= 45:
                        message += " Jeunes hommes : évitez les activités physiques intenses."
                    elif age >= 60:
                        message += "  Personnes âgées : restez au frais et hydratez-vous."
            else:
                message += " ✅ Conditions normales. Restez vigilant."

            phone = user.telephone
            if phone:
                success = envoyer_sms(phone, message)
                results.append({'user': user.id, 'status': 'success' if success else 'fail'})
            else:
                results.append({'user': user.id, 'status': 'fail', 'reason': 'Numéro de téléphone manquant'})

        return Response({'résultats': results})
