import random
from .questions import questions, weights
from .models import SuccessfulCase, NegativeRecommendation

def get_next_question(session):
    # Obtener el índice de la pregunta actual
    question_index = session.question_index
    if question_index < len(questions):
        return questions[question_index]
    return None

def calculate_recommendation(preferences):
    """
    Calcula la recomendación basada en:
    1. Casos exitosos (SuccessfulCase).
    2. Sistema de ponderación si no hay coincidencias exactas.
    """
    # 1. Buscar coincidencia en los casos exitosos
    successful_cases = SuccessfulCase.objects.all()
    for case in successful_cases:
        if (case.intensity == preferences.get("intensity") and
            case.flavor_profile == preferences.get("flavor_profile") and
            case.drink_type == preferences.get("drink_type")):
            # Si hay coincidencia exacta con un caso exitoso, retornar esa recomendación
            return case.recommendation

    # 2. Si no hay coincidencia exacta, usar la lógica ponderada

    # Ejemplo de bebidas en lugar de una base de datos completa
    bebidas = [
        {"name": "Chardonnay", "intensity": "Suave", "flavor_profile": "Frutal", "drink_type": "Vino", "temperature": "Fría", "bubbles": False},
        {"name": "Cabernet Sauvignon", "intensity": "Fuerte", "flavor_profile": "Seco", "drink_type": "Vino", "temperature": "Temperatura ambiente", "bubbles": False},
        {"name": "Mojito", "intensity": "Suave", "flavor_profile": "Dulce", "drink_type": "Coctel", "temperature": "Fría", "bubbles": True}
        # Agrega más bebidas aquí...
    ]

    # Filtrar bebidas basándose en recomendaciones negativas
    for neg in NegativeRecommendation.objects.all():
        bebidas = [b for b in bebidas if not (b["intensity"] == neg.intensity and b["flavor_profile"] == neg.flavor_profile and b["drink_type"] == neg.drink_type)]

    # Calcular puntuación de coincidencia ponderada
    def calculate_score(bebida):
        score = 0
        for key, weight in weights.items():
            if preferences.get(key) == bebida.get(key):
                score += weight
        return score

    # Seleccionar la bebida con la puntuación más alta
    bebida_recomendada = max(bebidas, key=calculate_score)
    return bebida_recomendada["name"]
