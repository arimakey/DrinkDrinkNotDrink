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
    Calcula la recomendación de bebida basada en las preferencias del usuario y el historial,
    incluyendo el cálculo de incertidumbre.
    """
    # Umbral de incertidumbre máximo permitido (por ejemplo, 30%)
    MAX_UNCERTAINTY_THRESHOLD = 30

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

    # 3. Calcular la puntuación y la incertidumbre para cada bebida
    def calculate_score(bebida):
        score = 0
        max_score = sum(weights.values())  # Puntuación máxima si todas las características coinciden

        # Ajuste de historial, con un peso de 0.5 por cada like/dislike histórico
        successful_count = SuccessfulCase.objects.filter(recommendation=bebida["name"]).count()
        negative_count = NegativeRecommendation.objects.filter(recommendation=bebida["name"]).count()
        score += 0.5 * successful_count - 0.5 * negative_count

        # Ajuste de puntuación en base a coincidencias con las preferencias actuales
        for key, weight in weights.items():
            if preferences.get(key) == bebida.get(key):
                score += weight

        # Calcular porcentaje de incertidumbre
        uncertainty = 100 - ((score / max_score) * 100) if max_score else 100
        return score, uncertainty

    # 4. Seleccionar la bebida con la menor incertidumbre dentro del umbral permitido
    bebida_recomendada, incertidumbre = None, 100  # Incertidumbre inicial alta
    for bebida in filtered_bebidas:
        score, bebida_uncertainty = calculate_score(bebida)
        if bebida_uncertainty < incertidumbre:  # Seleccionar la bebida con menor incertidumbre
            bebida_recomendada = bebida
            incertidumbre = bebida_uncertainty

    # 5. Evaluar el umbral de incertidumbre
    if incertidumbre > MAX_UNCERTAINTY_THRESHOLD:
        return "Sera para la proxima"  # Rechazar recomendación si la incertidumbre es demasiado alta
    else:
        return bebida_recomendada  # Devolver la bebida completa si está dentro del rango
