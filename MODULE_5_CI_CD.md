# Module 5 : CI/CD avec GitHub Actions

## 5.1 Objectif
Automatiser le déploiement : chaque commit sur la branche `main` déclenche un build et un redéploiement via un pipeline GitHub Actions.

## 5.2 Étape 1 : Initialisation du Repository Git

### 5.2.1 Création du .gitignore
```bash
# Le .gitignore a déjà été créé avec :
# - Fichiers Python (__pycache__, *.pyc)
# - Environnements virtuels (venv/, env/)
# - Fichiers de projet (mlruns/, *.log, images)
# - Secrets (jamais commiter !)
# - IDE et OS
```

### 5.2.2 Initialisation Git
```bash
# Initialiser git avec 'main' comme branche par défaut
git init -b main

# Premier commit
git add .
git commit -m "Initial commit: Bank Churn API with CI/CD"
```

## 5.3 Étape 2 : Créer un Repository GitHub

### 5.3.1 Création du Repository
1. Allez sur https://github.com/new
2. Nom : `bank-churn-mlops`
3. Visibility : Public ou Private
4. Ne pas initialiser avec README
5. Cliquez sur "Create repository"

### 5.3.2 Lier votre repo local à GitHub
```bash
# Lier votre repo local à GitHub
git remote add origin https://github.com/votre-username/bank-churn-mlops.git
git branch -M main
git push -u origin main
```

## 5.4 Étape 3 : Configuration des Secrets GitHub

### 5.4.1 Secrets Azure requis
Dans votre repository GitHub → Settings → Secrets and variables → Actions :

```yaml
AZURE_TENANT_ID: "votre-tenant-id"
AZURE_CLIENT_ID: "votre-client-id" 
AZURE_CLIENT_SECRET: "votre-client-secret"
AZURE_RESOURCE_GROUP: "rg-mlops-bank-churn"
AZURE_CONTAINER_APP_NAME: "bank-churn"
AZURE_REGISTRY_NAME: "acrmlopsXXXX"  # Nom de votre ACR
```

### 5.4.2 Obtenir les credentials Azure
```bash
# Créer un Service Principal
az ad sp create-for-rbac \
  --name "github-actions-bank-churn" \
  --role "Contributor" \
  --scopes "/subscriptions/votre-subscription-id"

# Notez les valeurs retournées :
# - appId (CLIENT_ID)
# - password (CLIENT_SECRET)  
# - tenant (TENANT_ID)
```

## 5.5 Étape 4 : Préparation des Tests pour le Pipeline

### 5.5.1 Structure des tests
```
tests/
├── __init__.py
├── test_api.py      # Tests des endpoints API
└── test_models.py   # Tests des modèles Pydantic
```

### 5.5.2 Exécution locale des tests
```bash
# Installer les dépendances de test
pip install pytest pytest-cov flake8

# Exécuter tous les tests
pytest tests/ -v

# Avec coverage
pytest tests/ --cov=app --cov-report=html

# Linting du code
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

## 5.6 Étape 5 : Vérification des Noms de Ressources (CRITIQUE)

### 5.6.1 Script de vérification
```bash
#!/bin/bash
# verify-names.sh

echo "🔍 Vérification des noms de ressources Azure..."

# Vérifier que les noms correspondent
RESOURCE_GROUP="rg-mlops-bank-churn"
CONTAINER_APP_NAME="bank-churn"

# Lister les ressources
az group list --query "[?name=='$RESOURCE_GROUP'].name" -o tsv
az containerapp list --query "[?name=='$CONTAINER_APP_NAME'].name" -o tsv

echo "✅ Vérification terminée"
```

### 5.6.2 Noms importants dans le workflow
- `AZURE_RESOURCE_GROUP` : Doit correspondre exactement
- `AZURE_CONTAINER_APP_NAME` : Doit correspondre exactement  
- `AZURE_REGISTRY_NAME` : Nom de votre ACR existant

## 5.7 Étape 6 : Création du Workflow GitHub Actions

### 5.7.1 Fichier `.github/workflows/ci-cd.yml`
Le workflow contient 3 jobs :

#### Job 1 : Test
- **Matrix testing** : Python 3.9, 3.10, 3.11
- **Linting** : flake8 pour la qualité du code
- **Tests unitaires** : pytest avec coverage
- **Upload coverage** : Codecov pour le suivi

#### Job 2 : Build and Deploy
- **Docker Buildx** : Build optimisé avec cache
- **GitHub Container Registry** : Stockage des images
- **Azure CLI** : Déploiement automatisé
- **Health checks** : Vérification post-déploiement

#### Job 3 : Notify
- **Notifications** : Succès/échec du pipeline
- **Logging** : Informations de débogage

### 5.7.2 Triggers du pipeline
```yaml
on:
  push:
    branches: [ main ]      # Déclenche sur push vers main
  pull_request:
    branches: [ main ]      # Tests sur PR vers main
```

### 5.7.3 Variables d'environnement
```yaml
env:
  REGISTRY: ghcr.io        # GitHub Container Registry
  IMAGE_NAME: ${{ github.repository }}
```

## 5.8 Étape 7 : Déclencher et Observer le Pipeline

### 5.8.1 Premier déclenchement
```bash
# Faire un changement pour déclencher le pipeline
echo "# Updated README" >> README.md
git add README.md
git commit -m "Update README - trigger CI/CD"
git push origin main
```

### 5.8.2 Surveillance du pipeline
1. Allez dans votre repository GitHub
2. Cliquez sur "Actions"
3. Sélectionnez le workflow "CI/CD Pipeline"
4. Observez l'exécution des 3 jobs

### 5.8.3 Logs détaillés
Pour chaque job, vous pouvez :
- Voir les logs en temps réel
- Télécharger les artifacts
- Vérifier les erreurs spécifiques

## 5.9 Exercice Pratique

### 5.9.1 Objectif
Déployer automatiquement une nouvelle version de l'API avec une modification.

### 5.9.2 Étapes
1. **Modifier l'API** : Ajouter un nouveau endpoint `/stats`
2. **Ajouter des tests** : Créer des tests pour le nouvel endpoint
3. **Committer** : Pousser les changements
4. **Observer** : Vérifier le déploiement automatique
5. **Tester** : Valider le nouvel endpoint en production

### 5.9.3 Solution
```python
# Dans app/main.py
@app.get("/stats", tags=["General"])
def get_stats():
    """Retourne des statistiques sur l'API"""
    return {
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/predict", "/predict/batch", "/stats"],
        "model_type": "RandomForest"
    }
```

```python
# Dans tests/test_api.py
def test_stats_endpoint(self):
    """Test du endpoint stats"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "endpoints" in data
    assert "/stats" in data["endpoints"]
```

## 5.10 Dépannage des Erreurs Courantes

### 5.10.1 Erreurs d'authentification Azure
```bash
# Erreur : Failed to login
Solution : Vérifiez AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
```

### 5.10.2 Erreurs de noms de ressources
```bash
# Erreur : Resource not found
Solution : Vérifiez que AZURE_RESOURCE_GROUP et AZURE_CONTAINER_APP_NAME existent
```

### 5.10.3 Erreurs Docker
```bash
# Erreur : Build failed
Solution : Vérifiez le Dockerfile et les dépendances dans requirements.txt
```

### 5.10.4 Erreurs de tests
```bash
# Erreur : Tests failed
Solution : Exécutez les tests localement avec pytest tests/ -v
```

## 5.11 Checkpoint

Avant de passer au module suivant, vérifiez que :
- ✅ Repository GitHub créé et lié
- ✅ Secrets GitHub configurés
- ✅ Pipeline CI/CD fonctionnel
- ✅ Tests passant avec succès
- ✅ Déploiement automatique opérationnel
- ✅ Health checks validés en production

## 5.12 Commandes Utiles

### 5.12.1 Git
```bash
# Vérifier le statut
git status

# Voir les commits
git log --oneline

# Voir les branches
git branch -a
```

### 5.12.2 GitHub CLI
```bash
# Voir les workflows
gh workflow list

# Voir les runs récents
gh run list --limit 10

# Voir les logs d'un run
gh run view <run-id> --log
```

### 5.12.3 Azure
```bash
# Vérifier les ressources
az group list --output table
az containerapp list --output table

# Voir les logs de l'application
az containerapp logs show --name <app-name> --resource-group <rg-name>
```

---

**🎯 Module 5 Terminé !** Votre API est maintenant déployée automatiquement à chaque changement avec un pipeline CI/CD complet.
