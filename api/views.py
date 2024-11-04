from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserSession
from .utils import get_next_question, calculate_recommendation
from .serializers import UserSerializer, UserSessionSerializer
from .questions import questions, weights
from .models import UserSession, SuccessfulCase, NegativeRecommendation

@api_view(['POST'])
def feedback(request, user_id):
    try:
        session = UserSession.objects.get(user_id=user_id)
        
        feedback = request.data.get("feedback")
        if feedback not in ["positive", "negative"]:
            return Response({"error": "Feedback inválido. Use 'positive' o 'negative'."}, status = 400)
        
        if session.recommendation:
            if feedback == "positive":
                SuccessfulCase.objects.create(
                    intensity=session.preferences.get("intensity"),
                    flavor_profile=session.preferences.get("flavor_profile"),
                    drink_type=session.preferences.get("drink_type"),
                    recommendation=session.recommendation
                )
            elif feedback == "negative":
                NegativeRecommendation.objects.create(
                    intensity=session.preferences.get("intensity"),
                    flavor_profile=session.preferences.get("flavor_profile"),
                    drink_type=session.preferences.get("drink_type"),
                    recommendation=session.recommendation
                )
        
        # Reiniciar la sesión de preguntas
        session.question_index = 0
        session.preferences = {}
        session.completed = False
        session.recommendation = None
        session.save()
        
        return Response({"message": "Feedback recibido y sesión reiniciada."})
    except UserSession.DoesNotExist:
        return Response({"error": "Sesión no encontrada."}, status=404)

@api_view(['POST'])
def create_user(request):
    username = request.data.get("username")
    user = User.objects.create(username=username)
    UserSession.objects.create(user=user)
    return Response({"message": "Usuario creado", "user_id": user.id})

@api_view(['GET'])
def next_question(request, user_id):
    session = UserSession.objects.get(user_id=user_id)
    if session.completed:
        return Response({"message": "El proceso ha finalizado", "recommendation": session.recommendation})
    
    question = get_next_question(session)
    if question:
        return Response({"question": question["text"], "options": question["options"], "index": question["index"]})
    else:
        recommendation = calculate_recommendation(session.preferences)
        session.recommendation = recommendation
        session.completed = True
        session.save()
        return Response({"message": "Recomendación finalizada", "recommendation": recommendation})

@api_view(['POST'])
def answer_question(request, user_id):
    session = UserSession.objects.get(user_id=user_id)
    question_index = session.question_index
    answer = request.data.get("answer")

    # Almacenar respuesta en preferences
    question = next(q for q in questions if q["index"] == question_index)
    session.preferences[question["field"]] = answer
    session.question_index += 1  # Incrementar para la siguiente pregunta
    session.save()
    
    return Response({"message": "Respuesta guardada", "next_question_index": session.question_index})
