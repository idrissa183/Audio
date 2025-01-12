import numpy as np

class QualityPredictor:
    def __init__(self, model):
        self.model = model  # Modèle entraîné

    # Fonction pour mapper les valeurs à des catégories
    def map_quality(self, value):
        if 0 <= value <= 1:
            return "qualité médiocre"
        elif 1 < value <= 2:
            return "qualité faible"
        elif 2 < value <= 3:
            return "qualité moyenne"
        elif 3 < value <= 4:
            return "qualité bonne"
        elif 4 < value <= 5:
            return "qualité excellente"
        else:
            return "valeur hors limites"

    # Méthode pour prédire et mapper directement les catégories
    def predict(self, X):
        numeric_predictions = self.model.predict(X)  # Prédiction numérique
        categories = np.vectorize(self.map_quality)(numeric_predictions)  # Mapping
        return categories