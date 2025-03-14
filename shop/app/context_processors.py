# app/context_processors.py

from .models import Category

def header_categories(request):
    # Récupérer toutes les catégories depuis la base de données
    categories = Category.objects.all()

    # Structure des données que tu veux envoyer
    serialized_categories = []

    for category in categories:
        serialized_category = {
            'name': category.name,
            'subcategories': []
        }

        # Sérialisation des sous-catégories et des activités associées
        for subcategory in category.subcategories.all():
            serialized_subcategory = {
                'name': subcategory.name,
                'activities': list(subcategory.activities.values('name'))  # Liste des noms d'activités
            }
            serialized_category['subcategories'].append(serialized_subcategory)

        serialized_categories.append(serialized_category)

    # Retourner un dictionnaire avec les données
    return {'categories': serialized_categories}
