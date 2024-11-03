from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserSession
from .utils import get_next_question, calculate_recommendation
from .serializers import UserSerializer, UserSessionSerializer
from .questions import questions, weights

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
