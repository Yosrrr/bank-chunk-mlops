import pytest
import json
from fastapi.testclient import TestClient
import os
import sys

# Ajouter le répertoire parent au path pour importer app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test des endpoints de santé"""
    
    def test_root_endpoint(self):
        """Test du endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Bank Churn Prediction API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "docs" in data

    def test_health_endpoint_with_model(self, monkeypatch):
        """Test du endpoint health avec modèle chargé"""
        # Mock du modèle
        class MockModel:
            def predict_proba(self, X):
                return [[0.3, 0.7]]
        
        monkeypatch.setattr("app.main.model", MockModel())
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True

    def test_health_endpoint_without_model(self):
        """Test du endpoint health sans modèle"""
        response = client.get("/health")
        # Le modèle n'est pas chargé dans les tests
        assert response.status_code == 503
        assert "Modele non charge" in response.json()["detail"]


class TestPredictionEndpoints:
    """Test des endpoints de prédiction"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        # Mock du modèle
        class MockModel:
            def predict_proba(self, X):
                # Simuler différentes probabilités selon les features
                if X[0][0] > 750:  # CreditScore élevé
                    return [[0.8, 0.2]]
                else:
                    return [[0.3, 0.7]]
        
        # Remplacer le modèle global
        import app.main
        app.main.model = MockModel()

    def test_predict_single_customer_high_score(self):
        """Test prédiction pour un client avec score élevé"""
        customer_data = {
            "CreditScore": 800,
            "Age": 35,
            "Tenure": 5,
            "Balance": 50000,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 70000,
            "Geography_Germany": 0,
            "Geography_Spain": 1
        }
        
        response = client.post("/predict", json=customer_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "churn_probability" in data
        assert "prediction" in data
        assert "risk_level" in data
        assert 0 <= data["churn_probability"] <= 1
        assert data["prediction"] in [0, 1]
        assert data["risk_level"] in ["Low", "Medium", "High"]

    def test_predict_single_customer_low_score(self):
        """Test prédiction pour un client avec score faible"""
        customer_data = {
            "CreditScore": 600,
            "Age": 45,
            "Tenure": 2,
            "Balance": 10000,
            "NumOfProducts": 1,
            "HasCrCard": 1,
            "IsActiveMember": 0,
            "EstimatedSalary": 40000,
            "Geography_Germany": 1,
            "Geography_Spain": 0
        }
        
        response = client.post("/predict", json=customer_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["prediction"] == 1  # Doit prédire churn
        assert data["risk_level"] in ["Medium", "High"]

    def test_predict_batch_customers(self):
        """Test prédiction en batch"""
        customers_data = [
            {
                "CreditScore": 750,
                "Age": 30,
                "Tenure": 3,
                "Balance": 25000,
                "NumOfProducts": 2,
                "HasCrCard": 1,
                "IsActiveMember": 1,
                "EstimatedSalary": 60000,
                "Geography_Germany": 0,
                "Geography_Spain": 0
            },
            {
                "CreditScore": 500,
                "Age": 55,
                "Tenure": 8,
                "Balance": 150000,
                "NumOfProducts": 4,
                "HasCrCard": 0,
                "IsActiveMember": 0,
                "EstimatedSalary": 120000,
                "Geography_Germany": 1,
                "Geography_Spain": 0
            }
        ]
        
        response = client.post("/predict/batch", json=customers_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["predictions"]) == 2
        
        for pred in data["predictions"]:
            assert "churn_probability" in pred
            assert "prediction" in pred

    def test_predict_invalid_data(self):
        """Test prédiction avec données invalides"""
        invalid_data = {
            "CreditScore": "invalid",  # Should be int
            "Age": 35,
            "Tenure": 5,
            "Balance": 50000,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 70000,
            "Geography_Germany": 0,
            "Geography_Spain": 1
        }
        
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_predict_missing_fields(self):
        """Test prédiction avec champs manquants"""
        incomplete_data = {
            "CreditScore": 700,
            "Age": 35
            # Missing other required fields
        }
        
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == 422  # Validation error


class TestModelLoading:
    """Test du chargement du modèle"""
    
    def test_model_file_not_found(self, monkeypatch):
        """Test quand le fichier modèle n'existe pas"""
        monkeypatch.setenv("MODEL_PATH", "nonexistent/model.pkl")
        
        # Recharger l'application pour tester le chargement
        from app.main import load_model
        import asyncio
        
        # Exécuter la fonction de chargement
        asyncio.run(load_model())
        
        # Vérifier que le modèle est None
        import app.main
        assert app.main.model is None


class TestErrorHandling:
    """Test de la gestion des erreurs"""
    
    def test_predict_without_model(self):
        """Test prédiction sans modèle chargé"""
        import app.main
        app.main.model = None
        
        customer_data = {
            "CreditScore": 700,
            "Age": 35,
            "Tenure": 5,
            "Balance": 50000,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 70000,
            "Geography_Germany": 0,
            "Geography_Spain": 1
        }
        
        response = client.post("/predict", json=customer_data)
        assert response.status_code == 503
        assert "Modele non disponible" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
