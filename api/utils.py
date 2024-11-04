import random
from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation
from .data import bebidas as bebidas_data  # Renaming the imported bebidas to avoid conflict

import random
from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation
from .data import bebidas as bebidas_data  # Renaming the imported bebidas to avoid conflict

from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation
from .data import bebidas as bebidas_data  # Renaming the imported bebidas to avoid conflict
from .recommendation import calculate_recommendation

def get_next_question(session):
    """
    Obtiene la siguiente pregunta de la sesión actual.
    Si no hay opciones válidas para una pregunta, se omite y se pasa a la siguiente.
    Si no quedan preguntas válidas, devuelve la recomendación final.
    """
    question_index = session.question_index
    preferences = session.preferences  # Preferencias seleccionadas hasta el momento

    # Filtrar las bebidas que coinciden con las preferencias actuales
    def filter_bebidas(bebidas, preferences):
        filtered_bebidas = bebidas
        for key, value in preferences.items():
            filtered_bebidas = [b for b in filtered_bebidas if b.get(key) == value]
        return filtered_bebidas

    # Filtrar bebidas disponibles según preferencias actuales
    available_bebidas = filter_bebidas(bebidas_data, preferences)

    # Si no hay bebidas que cumplan con las preferencias actuales, devolver la recomendación final
    if not available_bebidas:
        return {"recommendation": calculate_recommendation(preferences)}

    # Buscar la siguiente pregunta con opciones válidas
    while question_index < len(questions):
        current_question = questions[question_index]
        field = current_question["field"]
        options = current_question["options"]

        # Filtrar opciones válidas para la pregunta actual basadas en las bebidas disponibles
        valid_options = set(b[field] for b in available_bebidas if b.get(field) in options)

        # Si hay opciones válidas, devuelve esta pregunta
        if valid_options:
            session.question_index = question_index  # Actualiza el índice de la pregunta en la sesión
            session.save()
            return {
                "question": current_question["text"],
                "options": list(valid_options),
                "index": question_index
            }

        # Si no hay opciones válidas, incrementa el índice y pasa a la siguiente pregunta
        question_index += 1

    # Si no quedan preguntas válidas, devuelve la recomendación final
    return {"recommendation": calculate_recommendation(preferences)}


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
