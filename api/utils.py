import random
from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation
from .data import bebidas
def get_next_question(session):
    # Obtener el índice de la pregunta actual
    question_index = session.question_index
    if question_index < len(questions):
        return questions[question_index]
    return None

def calculate_recommendation(preferences):
    """
    Calcula la recomendación teniendo en cuenta:
    1. Casos exitosos que coincidan exactamente con las preferencias.
    2. Filtrado de bebidas exactas con dislikes.
    3. Ajuste de puntuación basado en historial de likes y dislikes, con menos peso que las preferencias actuales.
    """
    # 1. Buscar coincidencia exacta en casos exitosos
    successful_cases = SuccessfulCase.objects.all()
    for case in successful_cases:
        if (case.intensity == preferences.get("intensity") and
            case.flavor_profile == preferences.get("flavor_profile") and
            case.drink_type == preferences.get("drink_type")):
            return case.recommendation


    disliked_recommendations = NegativeRecommendation.objects.values_list('recommendation', flat=True)
    bebidas = [b for b in bebidas if b["name"] not in disliked_recommendations]

    def calculate_score(bebida):
        score = 0

        # Aumentar o disminuir puntaje basado en historial (con menos peso)
        successful_count = SuccessfulCase.objects.filter(recommendation=bebida["name"]).count()
        negative_count = NegativeRecommendation.objects.filter(recommendation=bebida["name"]).count()

        # Ajuste de historial, con un peso de 0.5 por cada like/dislike histórico
        score += 0.5 * successful_count
        score -= 0.5 * negative_count

        for key, weight in weights.items():
            if preferences.get(key) == bebida.get(key):
                score += weight

        return score

    bebida_recomendada = max(bebidas, key=calculate_score)
    return bebida_recomendada["name"]
