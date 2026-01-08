import pytest
from pydantic import ValidationError
from app.models import CustomerFeatures, PredictionResponse, HealthResponse


class TestCustomerFeatures:
    """Test du modèle CustomerFeatures"""
    
    def test_valid_customer_features(self):
        """Test avec des features valides"""
        features = CustomerFeatures(
            CreditScore=700,
            Age=35,
            Tenure=5,
            Balance=50000.0,
            NumOfProducts=2,
            HasCrCard=1,
            IsActiveMember=1,
            EstimatedSalary=70000.0,
            Geography_Germany=0,
            Geography_Spain=1
        )
        
        assert features.CreditScore == 700
        assert features.Age == 35
        assert features.Balance == 50000.0
        assert features.NumOfProducts == 2

    def test_invalid_credit_score(self):
        """Test avec CreditScore invalide"""
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=150,  # Trop bas
                Age=35,
                Tenure=5,
                Balance=50000,
                NumOfProducts=2,
                HasCrCard=1,
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

    def test_invalid_age(self):
        """Test avec âge invalide"""
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=150,  # Trop élevé
                Tenure=5,
                Balance=50000,
                NumOfProducts=2,
                HasCrCard=1,
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

    def test_negative_balance(self):
        """Test avec solde négatif"""
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=35,
                Tenure=5,
                Balance=-1000,  # Négatif
                NumOfProducts=2,
                HasCrCard=1,
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

    def test_invalid_num_products(self):
        """Test avec nombre de produits invalide"""
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=35,
                Tenure=5,
                Balance=50000,
                NumOfProducts=0,  # Doit être >= 1
                HasCrCard=1,
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

    def test_binary_fields_validation(self):
        """Test validation des champs binaires"""
        # Test HasCrCard invalide
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=35,
                Tenure=5,
                Balance=50000,
                NumOfProducts=2,
                HasCrCard=2,  # Doit être 0 ou 1
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

        # Test IsActiveMember invalide
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=35,
                Tenure=5,
                Balance=50000,
                NumOfProducts=2,
                HasCrCard=1,
                IsActiveMember=-1,  # Doit être 0 ou 1
                EstimatedSalary=70000,
                Geography_Germany=0,
                Geography_Spain=1
            )

    def test_geography_mutual_exclusion(self):
        """Test que Geography_Germany et Geography_Spain ne peuvent pas être tous les deux à 1"""
        with pytest.raises(ValidationError):
            CustomerFeatures(
                CreditScore=700,
                Age=35,
                Tenure=5,
                Balance=50000,
                NumOfProducts=2,
                HasCrCard=1,
                IsActiveMember=1,
                EstimatedSalary=70000,
                Geography_Germany=1,  # Les deux à 1
                Geography_Spain=1    # Invalid
            )


class TestPredictionResponse:
    """Test du modèle PredictionResponse"""
    
    def test_valid_prediction_response(self):
        """Test avec une réponse de prédiction valide"""
        response = PredictionResponse(
            churn_probability=0.75,
            prediction=1,
            risk_level="High"
        )
        
        assert response.churn_probability == 0.75
        assert response.prediction == 1
        assert response.risk_level == "High"

    def test_invalid_probability(self):
        """Test avec probabilité invalide"""
        with pytest.raises(ValidationError):
            PredictionResponse(
                churn_probability=1.5,  # > 1
                prediction=1,
                risk_level="High"
            )

        with pytest.raises(ValidationError):
            PredictionResponse(
                churn_probability=-0.1,  # < 0
                prediction=1,
                risk_level="High"
            )

    def test_invalid_prediction(self):
        """Test avec prédiction invalide"""
        with pytest.raises(ValidationError):
            PredictionResponse(
                churn_probability=0.75,
                prediction=2,  # Doit être 0 ou 1
                risk_level="High"
            )

    def test_invalid_risk_level(self):
        """Test avec niveau de risque invalide"""
        with pytest.raises(ValidationError):
            PredictionResponse(
                churn_probability=0.75,
                prediction=1,
                risk_level="Critical"  # Niveau non autorisé
            )


class TestHealthResponse:
    """Test du modèle HealthResponse"""
    
    def test_valid_health_response(self):
        """Test avec une réponse santé valide"""
        response = HealthResponse(
            status="healthy",
            model_loaded=True
        )
        
        assert response.status == "healthy"
        assert response.model_loaded is True

    def test_invalid_status(self):
        """Test avec statut invalide"""
        with pytest.raises(ValidationError):
            HealthResponse(
                status="running",  # Doit être "healthy" ou "unhealthy"
                model_loaded=True
            )


class TestModelSerialization:
    """Test de la sérialisation des modèles"""
    
    def test_customer_features_serialization(self):
        """Test sérialisation CustomerFeatures"""
        features = CustomerFeatures(
            CreditScore=700,
            Age=35,
            Tenure=5,
            Balance=50000.0,
            NumOfProducts=2,
            HasCrCard=1,
            IsActiveMember=1,
            EstimatedSalary=70000.0,
            Geography_Germany=0,
            Geography_Spain=1
        )
        
        # Test model_dump() (Pydantic v2)
        data = features.model_dump()
        assert isinstance(data, dict)
        assert data["CreditScore"] == 700
        
        # Test model_dump_json() (Pydantic v2)
        json_data = features.model_dump_json()
        assert isinstance(json_data, str)
        assert "CreditScore" in json_data

    def test_prediction_response_serialization(self):
        """Test sérialisation PredictionResponse"""
        response = PredictionResponse(
            churn_probability=0.75,
            prediction=1,
            risk_level="High"
        )
        
        data = response.model_dump()
        assert data["churn_probability"] == 0.75
        assert data["prediction"] == 1
        assert data["risk_level"] == "High"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
