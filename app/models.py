from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List

class CustomerFeatures(BaseModel):
    """Schema pour les features d'un client"""
    CreditScore: int = Field(..., ge=300, le=850, description="Score de credit")
    Age: int = Field(..., ge=18, le=100, description="Age du client")
    Tenure: int = Field(..., ge=0, le=10, description="Anciennete en annees")
    Balance: float = Field(..., ge=0, description="Solde du compte")
    NumOfProducts: int = Field(..., ge=1, le=4, description="Nombre de produits")
    HasCrCard: int = Field(..., ge=0, le=1, description="Possession carte credit")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Membre actif")
    EstimatedSalary: float = Field(..., ge=0, description="Salaire estime")
    Geography_Germany: int = Field(..., ge=0, le=1, description="Client allemand")
    Geography_Spain: int = Field(..., ge=0, le=1, description="Client espagnol")
    
    @field_validator('Geography_Spain')
    @classmethod
    def check_geography_exclusion(cls, v, info):
        if info.data and info.data.get('Geography_Germany') == 1 and v == 1:
            raise ValueError('Geography_Germany et Geography_Spain ne peuvent pas être tous les deux à 1')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "CreditScore": 650,
                "Age": 35,
                "Tenure": 5,
                "Balance": 50000,
                "NumOfProducts": 2,
                "HasCrCard": 1,
                "IsActiveMember": 1,
                "EstimatedSalary": 75000,
                "Geography_Germany": 0,
                "Geography_Spain": 1
            }
        }
    )

class PredictionResponse(BaseModel):
    """Schema pour la reponse de prediction"""
    churn_probability: float = Field(..., ge=0, le=1, description="Probabilite de churn (0-1)")
    prediction: int = Field(..., ge=0, le=1, description="Prediction binaire (0=reste, 1=part)")
    risk_level: str = Field(..., description="Niveau de risque (Low/Medium/High)")
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        if v not in ['Low', 'Medium', 'High']:
            raise ValueError('risk_level doit être Low, Medium ou High')
        return v

class HealthResponse(BaseModel):
    """Schema pour le health check"""
    status: str
    model_loaded: bool
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['healthy', 'unhealthy']:
            raise ValueError('status doit être healthy ou unhealthy')
        return v
    
    model_config = ConfigDict(protected_namespaces=())