import random
from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation
from .data import bebidas as bebidas_data  # Renaming the imported bebidas to avoid conflict

def get_next_question(session):
    """
    Obtiene la siguiente pregunta de la sesión actual.
    """
    question_index = session.question_index
    if question_index < len(questions):
        return questions[question_index]
    return None

def calculate_recommendation(preferences):
    """
    Calcula la recomendación de bebida basada en las preferencias del usuario y el historial.
    
    Se basa en los siguientes criterios:
    1. Coincidencia exacta en casos exitosos previos.
    2. Filtrado de bebidas que coincidan con las preferencias y que no estén en la lista de dislikes.
    3. Ajuste de puntuación basado en el historial de likes y dislikes, con menos peso que las preferencias actuales.
    """
    # 1. Buscar coincidencia exacta en casos exitosos
    successful_cases = SuccessfulCase.objects.all()
    for case in successful_cases:
        if (case.intensity == preferences.get("intensity") and
            case.flavor_profile == preferences.get("flavor_profile") and
            case.drink_type == preferences.get("drink_type")):
            return case.recommendation

    # 2. Filtrar bebidas excluyendo las que tienen dislikes
    disliked_recommendations = set(NegativeRecommendation.objects.values_list('recommendation', flat=True))
    filtered_bebidas = [b for b in bebidas_data if b["name"] not in disliked_recommendations]

    # 3. Calcular la puntuación de cada bebida en base a las preferencias y el historial
    def calculate_score(bebida):
        score = 0

        # Ajuste de historial, con un peso de 0.5 por cada like/dislike histórico
        successful_count = SuccessfulCase.objects.filter(recommendation=bebida["name"]).count()
        negative_count = NegativeRecommendation.objects.filter(recommendation=bebida["name"]).count()
        score += 0.5 * successful_count - 0.5 * negative_count

        # Ajuste de puntuación en base a coincidencias con las preferencias actuales
        for key, weight in weights.items():
            if preferences.get(key) == bebida.get(key):
                score += weight

        return score

    # Obtener la bebida con la puntuación más alta
    bebida_recomendada = max(filtered_bebidas, key=calculate_score)
    return bebida_recomendada["name"]
