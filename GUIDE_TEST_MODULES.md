# 🧪 Guide de Test - Modules MLOps

## 📋 Vue d'ensemble

Ce guide vous permet de tester chaque module de votre projet pour vérifier que tout fonctionne avant la soutenance.

---

## ✅ MODULE 1 : Entraînement du Modèle

### Test 1 : Vérifier les dépendances

```bash
# Activer l'environnement virtuel
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# Vérifier que Python fonctionne
python --version
# Doit afficher Python 3.9.x ou supérieur

# Vérifier les packages installés
pip list | grep -E "scikit-learn|mlflow|pandas|numpy"
```

### Test 2 : Vérifier le dataset

```bash
# Vérifier que le dataset existe
python -c "import pandas as pd; df = pd.read_csv('data/bank_churn.csv'); print(f'Dataset: {len(df)} lignes, {len(df.columns)} colonnes')"
```

**Résultat attendu :**
```
Dataset: 10000 lignes, 11 colonnes
```

### Test 3 : Entraîner le modèle

```bash
# Exécuter le script d'entraînement
python train_model.py
```

**Résultat attendu :**
```
Chargement des donnees...
Dataset : 10000 lignes, 11 colonnes
Taux de churn : XX.XX%

Train : 8000 lignes
Test : 2000 lignes

Entrainement du modele...

==================================================
RESULTATS DE L'ENTRAINEMENT
==================================================
Accuracy  : 0.XXXX
Precision : 0.XXXX
Recall    : 0.XXXX
F1 Score  : 0.XXXX
ROC AUC   : 0.XXXX
==================================================

Modele sauvegarde dans : model/churn_model.pkl
MLflow UI : mlflow ui --port 5000
```

### Test 4 : Vérifier MLflow

```bash
# Vérifier que MLflow a créé les runs
ls mlruns/

# Démarrer MLflow UI
mlflow ui --port 5000
```

**Actions à faire :**
1. Ouvrir http://localhost:5000 dans le navigateur
2. Vérifier qu'il y a des runs d'entraînement
3. Cliquer sur un run pour voir les métriques
4. Vérifier les artefacts (confusion_matrix.png, feature_importance.png)

### Test 5 : Vérifier le modèle sauvegardé

```bash
# Vérifier que le modèle existe
python -c "import joblib; model = joblib.load('model/churn_model.pkl'); print('Modèle chargé avec succès'); print(f'Type: {type(model)}')"
```

**Résultat attendu :**
```
Modèle chargé avec succès
Type: <class 'sklearn.ensemble._forest.RandomForestClassifier'>
```

---

## ✅ MODULE 2 : API FastAPI

### Test 1 : Vérifier les dépendances API

```bash
# Vérifier FastAPI et uvicorn
pip list | grep -E "fastapi|uvicorn|pydantic"
```

### Test 2 : Démarrer l'API localement

```bash
# Démarrer l'API
uvicorn app.main:app --reload --port 8000
```

**Résultat attendu :**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Modele charge avec succes depuis model/churn_model.pkl
INFO:     Application startup complete.
```

### Test 3 : Tester l'endpoint racine

**Dans un nouveau terminal :**
```bash
# Test avec curl
curl http://localhost:8000/

# Ou avec PowerShell
Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Résultat attendu :**
```json
{
  "message": "Bank Churn Prediction API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

### Test 4 : Tester le health check

```bash
curl http://localhost:8000/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Test 5 : Tester la documentation interactive

1. Ouvrir http://localhost:8000/docs dans le navigateur
2. Vérifier que tous les endpoints sont visibles :
   - `GET /`
   - `GET /health`
   - `POST /predict`
   - `POST /predict/batch`
3. Cliquer sur `/predict` → "Try it out"
4. Utiliser les données d'exemple :
```json
{
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
```
5. Cliquer sur "Execute"
6. Vérifier la réponse :
```json
{
  "churn_probability": 0.XXXX,
  "prediction": 0,
  "risk_level": "Low" ou "Medium" ou "High"
}
```

### Test 6 : Tester une prédiction avec curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 700,
    "Age": 40,
    "Tenure": 7,
    "Balance": 80000,
    "NumOfProducts": 3,
    "HasCrCard": 1,
    "IsActiveMember": 0,
    "EstimatedSalary": 90000,
    "Geography_Germany": 1,
    "Geography_Spain": 0
  }'
```

**Résultat attendu :** JSON avec churn_probability, prediction, risk_level

### Test 7 : Tester la validation (données invalides)

```bash
# Test avec données invalides (âge trop élevé)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 700,
    "Age": 150,
    "Tenure": 5,
    "Balance": 50000,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 70000,
    "Geography_Germany": 0,
    "Geography_Spain": 1
  }'
```

**Résultat attendu :** Erreur 422 avec message de validation

### Test 8 : Tester le batch prediction

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '[
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
  ]'
```

**Résultat attendu :** JSON avec un tableau de prédictions

---

## ✅ MODULE 3 : Docker

### Test 1 : Vérifier Docker

```bash
# Vérifier que Docker fonctionne
docker --version
docker ps
```

### Test 2 : Vérifier le Dockerfile

```bash
# Lire le Dockerfile
cat Dockerfile
# ou sur Windows
type Dockerfile
```

**Vérifier que :**
- Base image : `python:3.9-slim`
- Port exposé : `8000`
- Commande : `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Test 3 : Build l'image Docker

```bash
# Build l'image
docker build -t churn-api:v1 .

# Vérifier que l'image a été créée
docker images | grep churn-api
```

**Résultat attendu :**
```
churn-api   v1   [IMAGE_ID]   [Taille]   [Date]
```

### Test 4 : Tester le conteneur localement

```bash
# Lancer le conteneur
docker run -d -p 8000:8000 --name churn-api-test churn-api:v1

# Vérifier que le conteneur tourne
docker ps | grep churn-api-test

# Tester l'API dans le conteneur
curl http://localhost:8000/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Test 5 : Vérifier les logs du conteneur

```bash
# Voir les logs
docker logs churn-api-test
```

**Résultat attendu :** Logs montrant le démarrage de l'API et le chargement du modèle

### Test 6 : Arrêter et nettoyer

```bash
# Arrêter le conteneur
docker stop churn-api-test

# Supprimer le conteneur
docker rm churn-api-test
```

---

## ✅ MODULE 4 : Déploiement Azure

### Prérequis

```bash
# Vérifier Azure CLI
az --version

# Se connecter à Azure
az login

# Vérifier l'abonnement
az account show
```

### Test 1 : Vérifier les ressources Azure existantes

```bash
# Lister les resource groups
az group list --output table

# Vérifier si votre resource group existe
az group show --name rg-mlops-bank-churn
```

### Test 2 : Tester le script de déploiement (optionnel - attention aux coûts)

**⚠️ ATTENTION :** Ne lancez ce script que si vous voulez créer de nouvelles ressources Azure (coûts possibles)

```powershell
# Sur Windows PowerShell
.\deploy-azure.ps1
```

**Ou créer un script de test qui vérifie seulement :**

```bash
# Créer un script test-azure.sh
cat > test-azure.sh << 'EOF'
#!/bin/bash
echo "Test des prérequis Azure..."

# Vérifier la connexion
az account show || { echo "❌ Non connecté à Azure"; exit 1; }
echo "✅ Connecté à Azure"

# Vérifier les providers
az provider list --query "[?namespace=='Microsoft.ContainerRegistry' || namespace=='Microsoft.App'].{Namespace:namespace, State:registrationState}" --output table
echo "✅ Providers vérifiés"

echo "✅ Tous les prérequis sont OK"
EOF

chmod +x test-azure.sh
./test-azure.sh
```

### Test 3 : Vérifier l'API en production (si déjà déployée)

```bash
# Récupérer l'URL de l'application
# (Depuis azure-deploy-info.txt ou le portail Azure)
APP_URL="https://bank-churn.delightfulflower-76ee4057.francecentral.azurecontainerapps.io"

# Tester le health check
curl $APP_URL/health

# Tester une prédiction
curl -X POST "$APP_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Test 4 : Vérifier les logs Azure

```bash
# Voir les logs de la Container App
az containerapp logs show \
  --name bank-churn \
  --resource-group rg-mlops-bank-churn \
  --tail 50
```

---

## ✅ MODULE 5 : CI/CD avec GitHub Actions

### Test 1 : Vérifier le workflow

```bash
# Vérifier que le fichier workflow existe
cat .github/workflows/ci-cd.yml
```

**Vérifier que le workflow contient :**
- Trigger sur `push` vers `main`
- Job `test` avec matrix Python
- Job `build-and-deploy`
- Job `notify`

### Test 2 : Vérifier les secrets GitHub (via interface web)

**Actions à faire :**
1. Aller sur GitHub → Votre repo → Settings → Secrets and variables → Actions
2. Vérifier que ces secrets existent :
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
   - `AZURE_RESOURCE_GROUP`
   - `AZURE_CONTAINER_APP_NAME`
   - `AZURE_REGISTRY_NAME`

### Test 3 : Tester les tests localement

```bash
# Installer les dépendances de test
pip install pytest pytest-cov flake8

# Exécuter les tests
pytest tests/ -v

# Avec coverage
pytest tests/ --cov=app --cov-report=html

# Linting
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

**Résultat attendu :** Tous les tests passent ✅

### Test 4 : Déclencher le pipeline (test)

**Option 1 : Faire un petit changement et commit**

```bash
# Faire un petit changement
echo "# Test CI/CD" >> README.md

# Commit et push
git add README.md
git commit -m "Test: Déclencher le pipeline CI/CD"
git push origin main
```

**Option 2 : Utiliser l'interface GitHub**

1. Aller sur GitHub → Actions
2. Sélectionner le workflow "CI/CD Pipeline"
3. Cliquer sur "Run workflow"
4. Sélectionner la branche `main`
5. Cliquer sur "Run workflow"

### Test 5 : Observer le pipeline

1. Aller sur GitHub → Actions
2. Cliquer sur le run en cours
3. Observer les jobs :
   - ✅ `test` doit passer
   - ✅ `build-and-deploy` doit passer
   - ✅ `notify` doit passer

### Test 6 : Vérifier les artifacts

Dans GitHub Actions, vérifier que :
- Les tests ont généré un rapport de coverage
- Le build Docker a réussi
- Le déploiement Azure a réussi

---

## 🧪 TESTS AUTOMATISÉS

### Exécuter tous les tests

```bash
# Créer un script de test complet
cat > test-all.sh << 'EOF'
#!/bin/bash

echo "🧪 Tests complets du projet MLOps"
echo "=================================="

# Test 1: Module 1 - Entraînement
echo ""
echo "📊 Test Module 1: Entraînement"
python train_model.py
if [ $? -eq 0 ]; then
    echo "✅ Module 1: OK"
else
    echo "❌ Module 1: ÉCHEC"
fi

# Test 2: Module 2 - API
echo ""
echo "🚀 Test Module 2: API"
# Démarrer l'API en arrière-plan
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 5

# Tester les endpoints
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Module 2: API fonctionne"
else
    echo "❌ Module 2: API ne répond pas"
fi

# Arrêter l'API
kill $API_PID

# Test 3: Module 3 - Docker
echo ""
echo "🐳 Test Module 3: Docker"
docker build -t churn-api:test . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Module 3: Docker build OK"
else
    echo "❌ Module 3: Docker build ÉCHEC"
fi

# Test 4: Module 5 - Tests unitaires
echo ""
echo "🔬 Test Module 5: Tests unitaires"
pytest tests/ -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ Module 5: Tous les tests passent"
else
    echo "❌ Module 5: Certains tests échouent"
fi

echo ""
echo "=================================="
echo "✅ Tests terminés"
EOF

chmod +x test-all.sh
./test-all.sh
```

**Version PowerShell pour Windows :**

```powershell
# Créer test-all.ps1
@"
# Tests complets du projet MLOps
Write-Host "🧪 Tests complets du projet MLOps" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Test 1: Module 1
Write-Host "`n📊 Test Module 1: Entraînement" -ForegroundColor Yellow
python train_model.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Module 1: OK" -ForegroundColor Green
} else {
    Write-Host "❌ Module 1: ÉCHEC" -ForegroundColor Red
}

# Test 2: Module 2 - API
Write-Host "`n🚀 Test Module 2: API" -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "app.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 5

$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "✅ Module 2: API fonctionne" -ForegroundColor Green
} else {
    Write-Host "❌ Module 2: API ne répond pas" -ForegroundColor Red
}

# Test 3: Module 3 - Docker
Write-Host "`n🐳 Test Module 3: Docker" -ForegroundColor Yellow
docker build -t churn-api:test . 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Module 3: Docker build OK" -ForegroundColor Green
} else {
    Write-Host "❌ Module 3: Docker build ÉCHEC" -ForegroundColor Red
}

# Test 4: Module 5 - Tests unitaires
Write-Host "`n🔬 Test Module 5: Tests unitaires" -ForegroundColor Yellow
pytest tests/ -v
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Module 5: Tous les tests passent" -ForegroundColor Green
} else {
    Write-Host "❌ Module 5: Certains tests échouent" -ForegroundColor Red
}

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "✅ Tests terminés" -ForegroundColor Green
"@ | Out-File -FilePath test-all.ps1 -Encoding UTF8

# Exécuter
.\test-all.ps1
```

---

## 📋 CHECKLIST DE TEST COMPLÈTE

### Module 1 : Entraînement
- [ ] Dataset présent et valide
- [ ] Script d'entraînement s'exécute sans erreur
- [ ] Modèle sauvegardé dans `model/churn_model.pkl`
- [ ] MLflow UI accessible et montre les runs
- [ ] Métriques affichées (accuracy, precision, recall, etc.)

### Module 2 : API FastAPI
- [ ] API démarre sans erreur
- [ ] Endpoint `/` répond
- [ ] Endpoint `/health` répond avec `model_loaded: true`
- [ ] Endpoint `/predict` fonctionne avec données valides
- [ ] Endpoint `/predict` rejette les données invalides (422)
- [ ] Endpoint `/predict/batch` fonctionne
- [ ] Documentation `/docs` accessible et fonctionnelle

### Module 3 : Docker
- [ ] Dockerfile présent et valide
- [ ] Build Docker réussit
- [ ] Image Docker créée
- [ ] Conteneur démarre et API fonctionne dedans
- [ ] Port 8000 exposé correctement

### Module 4 : Azure
- [ ] Azure CLI installé et connecté
- [ ] Resource group existe (si déjà déployé)
- [ ] API en production accessible (si déjà déployée)
- [ ] Health check fonctionne en production
- [ ] Prédictions fonctionnent en production

### Module 5 : CI/CD
- [ ] Fichier workflow présent dans `.github/workflows/`
- [ ] Secrets GitHub configurés
- [ ] Tests unitaires passent localement
- [ ] Pipeline se déclenche sur commit
- [ ] Tous les jobs du pipeline passent
- [ ] Déploiement automatique fonctionne

---

## 🚨 RÉSOLUTION DE PROBLÈMES

### Problème : Le modèle ne charge pas

```bash
# Vérifier que le modèle existe
ls -lh model/churn_model.pkl

# Si absent, réentraîner
python train_model.py
```

### Problème : L'API ne démarre pas

```bash
# Vérifier que le port 8000 n'est pas utilisé
# Windows :
netstat -ano | findstr :8000
# Mac/Linux :
lsof -i :8000

# Vérifier les dépendances
pip install -r requirements.txt
```

### Problème : Docker build échoue

```bash
# Vérifier le Dockerfile
cat Dockerfile

# Build avec plus de logs
docker build -t churn-api:v1 . --progress=plain

# Vérifier que le modèle est copié
docker run --rm churn-api:v1 ls -la model/
```

### Problème : Tests échouent

```bash
# Exécuter avec plus de détails
pytest tests/ -v -s

# Exécuter un test spécifique
pytest tests/test_api.py::TestHealthEndpoints::test_root_endpoint -v
```

### Problème : Pipeline CI/CD échoue

1. Vérifier les logs dans GitHub Actions
2. Vérifier que les secrets sont configurés
3. Tester localement les commandes qui échouent
4. Vérifier les noms de ressources Azure

---

## ✅ VALIDATION FINALE AVANT SOUTENANCE

```bash
# Script de validation complète
echo "🔍 Validation finale du projet..."
echo ""

echo "1. Vérification des fichiers essentiels..."
[ -f "train_model.py" ] && echo "✅ train_model.py" || echo "❌ train_model.py manquant"
[ -f "app/main.py" ] && echo "✅ app/main.py" || echo "❌ app/main.py manquant"
[ -f "Dockerfile" ] && echo "✅ Dockerfile" || echo "❌ Dockerfile manquant"
[ -f ".github/workflows/ci-cd.yml" ] && echo "✅ ci-cd.yml" || echo "❌ ci-cd.yml manquant"
[ -f "model/churn_model.pkl" ] && echo "✅ Modèle sauvegardé" || echo "❌ Modèle manquant - Exécutez train_model.py"

echo ""
echo "2. Tests unitaires..."
pytest tests/ -v --tb=short

echo ""
echo "3. Build Docker..."
docker build -t churn-api:validation . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Docker build OK"
else
    echo "❌ Docker build échoue"
fi

echo ""
echo "✅ Validation terminée !"
```

---

**Bonne chance pour vos tests ! 🚀**
