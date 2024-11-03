questions = [
    {"index": 0, "field": "drink_type", "text": "¿Qué tipo de bebida prefieres?", "options": ["Vino", "Coctel", "Licor puro"]},
    {"index": 1, "field": "intensity", "text": "¿Cuál es la intensidad que prefieres en la bebida?", "options": ["Suave", "Intermedio", "Fuerte"]},
    {"index": 2, "field": "flavor_profile", "text": "¿Qué perfil de sabor prefieres?", "options": ["Frutal", "Seco", "Dulce", "Amargo", "Ahumado"]},
    {"index": 3, "field": "temperature", "text": "¿Prefieres una bebida fría o a temperatura ambiente?", "options": ["Fría", "Temperatura ambiente"]},
    {"index": 4, "field": "bubbles", "text": "¿Te interesa una bebida con burbujas?", "options": ["Sí", "No"]}
]

weights = {
    "flavor_profile": 3,
    "intensity": 2,
    "drink_type": 1,
    "temperature": 1,
    "bubbles": 1
}
