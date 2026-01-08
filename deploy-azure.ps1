
# ================================
# VARIABLES - MODIFIEZ SI BESOIN
# ================================
$RESOURCE_GROUP = "rg-mlops-bank-churn"
$LOCATION = "westeurope"
$ACR_NAME = "acrmlops$(Get-Random -Maximum 9999)"  # Nom unique pour ACR
$CONTAINER_APP_NAME = "bank-churn"
$CONTAINERAPPS_ENV = "env-mlops-workshop"
$IMAGE_NAME = "churn-api"
$IMAGE_TAG = "v1"
$TARGET_PORT = 8000

Write-Host "=========================================="
Write-Host "DEPLOIEMENT AZURE - Bank Churn API"
Write-Host "=========================================="
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "Location: $LOCATION"
Write-Host "ACR Name: $ACR_NAME"
Write-Host "=========================================="

# ================================
# ETAPE 1: Enregistrer les providers
# ================================
Write-Host "`n[1/7] Enregistrement des providers Azure..."
az provider register --namespace Microsoft.ContainerRegistry --wait 2>$null
az provider register --namespace Microsoft.App --wait 2>$null
az provider register --namespace Microsoft.OperationalInsights --wait 2>$null
Write-Host "OK - Providers enregistres"

# ================================
# ETAPE 2: Creer le Resource Group
# ================================
Write-Host "`n[2/7] Creation du Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none 2>$null
Write-Host "OK - Resource Group cree: $RESOURCE_GROUP"

# ================================
# ETAPE 3: Creer Azure Container Registry
# ================================
Write-Host "`n[3/7] Creation du Container Registry (ACR)..."
az acr create `
    --resource-group $RESOURCE_GROUP `
    --name $ACR_NAME `
    --sku Basic `
    --admin-enabled true `
    --location $LOCATION `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur ACR en $LOCATION, essai avec northeurope..."
    $LOCATION = "northeurope"
    az acr create `
        --resource-group $RESOURCE_GROUP `
        --name $ACR_NAME `
        --sku Basic `
        --admin-enabled true `
        --location $LOCATION `
        --output none
}

Write-Host "OK - ACR cree: $ACR_NAME"

# ================================
# ETAPE 4: Push de l'image Docker vers ACR
# ================================
Write-Host "`n[4/7] Connexion et push de l'image vers ACR..."
az acr login --name $ACR_NAME

$ACR_LOGIN_SERVER = $(az acr show --name $ACR_NAME --query loginServer -o tsv).Trim()
Write-Host "ACR Server: $ACR_LOGIN_SERVER"

# Tag et push
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest"
docker push "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
docker push "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest"
Write-Host "OK - Image pushee dans ACR"

# ================================
# ETAPE 5: Creer Log Analytics Workspace
# ================================
Write-Host "`n[5/7] Creation de Log Analytics Workspace..."
$LAW_NAME = "law-mlops-$(Get-Random -Maximum 9999)"
az monitor log-analytics workspace create `
    --resource-group $RESOURCE_GROUP `
    --workspace-name $LAW_NAME `
    --location $LOCATION `
    --output none

Start-Sleep -Seconds 10

$LAW_ID = $(az monitor log-analytics workspace show `
    --resource-group $RESOURCE_GROUP `
    --workspace-name $LAW_NAME `
    --query customerId -o tsv).Trim()

$LAW_KEY = $(az monitor log-analytics workspace get-shared-keys `
    --resource-group $RESOURCE_GROUP `
    --workspace-name $LAW_NAME `
    --query primarySharedKey -o tsv).Trim()

Write-Host "OK - Log Analytics cree: $LAW_NAME"

# ================================
# ETAPE 6: Creer Container Apps Environment
# ================================
Write-Host "`n[6/7] Creation de l'environnement Container Apps..."
az containerapp env create `
    --name $CONTAINERAPPS_ENV `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --logs-workspace-id $LAW_ID `
    --logs-workspace-key $LAW_KEY `
    --output none

Write-Host "OK - Environment cree: $CONTAINERAPPS_ENV"

# ================================
# ETAPE 7: Deployer Container App
# ================================
Write-Host "`n[7/7] Deploiement de la Container App..."

# Recuperer les credentials ACR
$ACR_USER = $(az acr credential show --name $ACR_NAME --query username -o tsv).Trim()
$ACR_PASS = $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv).Trim()

az containerapp create `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --environment $CONTAINERAPPS_ENV `
    --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" `
    --ingress external `
    --target-port $TARGET_PORT `
    --registry-server $ACR_LOGIN_SERVER `
    --registry-username $ACR_USER `
    --registry-password $ACR_PASS `
    --min-replicas 1 `
    --max-replicas 1 `
    --output none

Write-Host "OK - Container App deployee"

# ================================
# RESULTAT FINAL
# ================================
$APP_URL = $(az containerapp show `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query properties.configuration.ingress.fqdn -o tsv).Trim()

Write-Host "`n=========================================="
Write-Host "DEPLOIEMENT REUSSI !"
Write-Host "=========================================="
Write-Host "ACR Name      : $ACR_NAME"
Write-Host "Region        : $LOCATION"
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host ""
Write-Host "URLs de l'application:"
Write-Host "  API     : https://$APP_URL"
Write-Host "  Health  : https://$APP_URL/health"
Write-Host "  Docs    : https://$APP_URL/docs"
Write-Host ""
Write-Host "Pour supprimer toutes les ressources:"
Write-Host "  az group delete --name $RESOURCE_GROUP --yes --no-wait"
Write-Host "=========================================="

# Sauvegarder les infos
$info = @"
# Informations de deploiement Azure
RESOURCE_GROUP=$RESOURCE_GROUP
ACR_NAME=$ACR_NAME
CONTAINER_APP_NAME=$CONTAINER_APP_NAME
APP_URL=https://$APP_URL
"@
$info | Out-File -FilePath "azure-deploy-info.txt" -Encoding utf8
Write-Host "`nInformations sauvegardees dans: azure-deploy-info.txt"
