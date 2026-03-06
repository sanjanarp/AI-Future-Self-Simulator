#!/usr/bin/env pwsh
<#
.SYNOPSIS
Automated Azure Deployment Script for Future Self Simulator
.DESCRIPTION
This script deploys the Future Self Simulator to Azure Container Apps.
Copy this file to deploy.ps1 and fill in your values before running.
.EXAMPLE
.\deploy.ps1 -SubscriptionId "your-subscription-id" -Location "eastus" -ProjectName "Future Self Simulator"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-future-self-simulator",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectName = "Future Self Simulator"
)

# Color output functions
function Write-Success { Write-Host "SUCCESS: $args" -ForegroundColor Green }
function Write-Error { Write-Host "ERROR: $args" -ForegroundColor Red }
function Write-Info { Write-Host "INFO: $args" -ForegroundColor Cyan }
function Write-Section { Write-Host "`n=== $args ===" -ForegroundColor Yellow }

# ── CHANGE THESE to match your desired Azure resource names ──
$acrName       = "your-acr-name"          # must be globally unique, alphanumeric only
$imageName     = "future-self-simulator"
$imageTag      = "latest"
$identityName  = "mi-future-self-simulator"
$keyVaultName  = "your-keyvault-name"     # must be globally unique
$envName       = "cae-future-self-simulator"
$appName       = "ca-future-self-simulator"
$appInsightsName = "ai-future-self-simulator"
$workspaceName = "law-future-self-simulator"

Write-Section "Future Self Simulator - Azure Deployment"
Write-Info "Subscription: $SubscriptionId"
Write-Info "Region: $Location"
Write-Info "Resource Group: $ResourceGroupName"

# Check Azure CLI
Write-Section "Checking Azure CLI"
try {
    $version = az --version 2>&1 | Select-Object -First 1
    Write-Success "Azure CLI installed: $version"
} catch {
    Write-Error "Azure CLI not found. Please install from: https://aka.ms/installazurecliwindows"
    exit 1
}

# Step 1: Login and Set Subscription
Write-Section "Step 1: Login and Set Subscription"
try {
    az account set --subscription $SubscriptionId
    $account = az account show --query "name" -o tsv
    Write-Success "Using subscription: $account"
} catch {
    Write-Error "Failed to set subscription. Attempting login..."
    az login
    az account set --subscription $SubscriptionId
}

# Step 2: Create Resource Group
Write-Section "Step 2: Create Resource Group"
try {
    $rgExists = az group exists --name $ResourceGroupName
    if ($rgExists -eq "true") {
        Write-Info "Resource group already exists: $ResourceGroupName"
    } else {
        Write-Info "Creating resource group..."
        az group create --name $ResourceGroupName --location $Location
        Write-Success "Resource group created"
    }
} catch {
    Write-Error "Failed to create resource group: $_"
    exit 1
}

# Step 3: Create Container Registry
Write-Section "Step 3: Create Container Registry"
try {
    $acrExists = az acr list --resource-group $ResourceGroupName --query "[?name=='$acrName'].name" -o tsv
    if ($acrExists) {
        Write-Info "Container registry already exists: $acrName"
    } else {
        Write-Info "Creating Container Registry..."
        az acr create --resource-group $ResourceGroupName --name $acrName --sku Basic --admin-enabled true
        Write-Success "Container Registry created"
    }
} catch {
    Write-Error "Failed to create Container Registry: $_"
}

# Step 4: Build and Push Docker Image
Write-Section "Step 4: Build and Push Docker Image"
try {
    Write-Info "Building Docker image and pushing to ACR..."
    az acr build `
        --registry $acrName `
        --image "${imageName}:${imageTag}" `
        --file Dockerfile `
        .
    Write-Success "Docker image built and pushed"
} catch {
    Write-Error "Failed to build/push Docker image: $_"
}

# Step 5: Create User-Assigned Managed Identity
Write-Section "Step 5: Create User-Assigned Managed Identity"
try {
    $identityExists = az identity list --resource-group $ResourceGroupName --query "[?name=='$identityName'].name" -o tsv
    if ($identityExists) {
        Write-Info "Managed identity already exists: $identityName"
    } else {
        Write-Info "Creating Managed Identity..."
        az identity create --resource-group $ResourceGroupName --name $identityName
        Write-Success "Managed Identity created"
    }
    
    $principalId = az identity show `
        --resource-group $ResourceGroupName `
        --name $identityName `
        --query "principalId" -o tsv
    Write-Info "Principal ID: $principalId"
} catch {
    Write-Error "Failed to create Managed Identity: $_"
}

# Step 6: Create Key Vault
Write-Section "Step 6: Create Key Vault"
try {
    $kvExists = az keyvault list --resource-group $ResourceGroupName --query "[?name=='$keyVaultName'].name" -o tsv
    if ($kvExists) {
        Write-Info "Key Vault already exists: $keyVaultName"
    } else {
        Write-Info "Creating Key Vault..."
        az keyvault create `
            --resource-group $ResourceGroupName `
            --name $keyVaultName `
            --location $Location
        Write-Success "Key Vault created"
    }
    
    # Grant Managed Identity access
    Write-Info "Granting Managed Identity access to Key Vault..."
    az keyvault set-policy `
        --name $keyVaultName `
        --object-id $principalId `
        --secret-permissions get list
    Write-Success "Key Vault policy set"
} catch {
    Write-Error "Failed to create Key Vault: $_"
}

# Step 7: Prompt for API Keys (use env vars if present)
Write-Section "Step 7: Store API Keys in Key Vault"
Write-Info "Storing Azure OpenAI details from environment variables if set, otherwise you'll be prompted."

if ($env:AZURE_OPENAI_API_KEY) {
    $apiKey = $env:AZURE_OPENAI_API_KEY
    Write-Info "Using AZURE_OPENAI_API_KEY from environment"
} else {
    $apiKey = Read-Host "Enter AZURE_OPENAI_API_KEY (or skip)"
}
if ($apiKey) {
    az keyvault secret set --vault-name $keyVaultName --name "AZURE-OPENAI-API-KEY" --value $apiKey
    Write-Success "Azure OpenAI API Key stored"
}

if ($env:AZURE_OPENAI_ENDPOINT) {
    $endpoint = $env:AZURE_OPENAI_ENDPOINT
    Write-Info "Using AZURE_OPENAI_ENDPOINT from environment"
} else {
    $endpoint = Read-Host "Enter AZURE_OPENAI_ENDPOINT (e.g., https://yourresource.openai.azure.com)"
}
if ($endpoint) {
    az keyvault secret set --vault-name $keyVaultName --name "AZURE-OPENAI-ENDPOINT" --value $endpoint
    Write-Success "Azure OpenAI Endpoint stored"
}

if ($env:AZURE_OPENAI_DEPLOYMENT) {
    $deployment = $env:AZURE_OPENAI_DEPLOYMENT
    Write-Info "Using AZURE_OPENAI_DEPLOYMENT from environment"
} else {
    $deployment = Read-Host "Enter AZURE_OPENAI_DEPLOYMENT"
}
if ($deployment) {
    az keyvault secret set --vault-name $keyVaultName --name "AZURE-OPENAI-DEPLOYMENT" --value $deployment
    Write-Success "Azure OpenAI Deployment stored"
}

# Step 8: Create Log Analytics and Application Insights
Write-Section "Step 8: Create Monitoring Resources"
try {
    Write-Info "Creating Log Analytics Workspace..."
    $workspaceExists = az monitor log-analytics workspace list --resource-group $ResourceGroupName --query "[?name=='$workspaceName'].name" -o tsv
    if (-not $workspaceExists) {
        az monitor log-analytics workspace create `
            --resource-group $ResourceGroupName `
            --workspace-name $workspaceName
        Write-Success "Log Analytics Workspace created"
    } else {
        Write-Info "Log Analytics Workspace already exists"
    }
    
    Write-Info "Creating Application Insights..."
    $appInsightsExists = az monitor app-insights component list --resource-group $ResourceGroupName --query "[?name=='$appInsightsName'].name" -o tsv
    if (-not $appInsightsExists) {
        az monitor app-insights component create `
            --app $appInsightsName `
            --location $Location `
            --resource-group $ResourceGroupName `
            --workspace $workspaceName
        Write-Success "Application Insights created"
    } else {
        Write-Info "Application Insights already exists"
    }
} catch {
    Write-Error "Failed to create monitoring resources: $_"
}

# Step 9: Create Container App Environment
Write-Section "Step 9: Create Container App Environment"
try {
    $envExists = az containerapp env list --resource-group $ResourceGroupName --query "[?name=='$envName'].name" -o tsv
    if ($envExists) {
        Write-Info "Container App Environment already exists: $envName"
    } else {
        Write-Info "Creating Container App Environment..."
        az containerapp env create `
            --name $envName `
            --resource-group $ResourceGroupName `
            --location $Location
        Write-Success "Container App Environment created"
    }
} catch {
    Write-Error "Failed to create Container App Environment: $_"
}

# Step 10: Deploy Container App
Write-Section "Step 10: Deploy to Azure Container Apps"
try {
    $appExists = az containerapp list --resource-group $ResourceGroupName --query "[?name=='$appName'].name" -o tsv
    
    # Get ACR credentials
    $acrUsername = az acr credential show -n $acrName -o tsv --query username
    $acrPassword = az acr credential show -n $acrName -o tsv --query "passwords[0].value"
    
    if ($appExists) {
        Write-Info "Container App already exists. Updating..."
        az containerapp update `
            --name $appName `
            --resource-group $ResourceGroupName `
            --set-env-vars `
                "AZURE_KEY_VAULT_URL=https://${keyVaultName}.vault.azure.net/"
    } else {
        Write-Info "Creating Container App..."
        az containerapp create `
            --name $appName `
            --resource-group $ResourceGroupName `
            --environment $envName `
            --image "${acrName}.azurecr.io/${imageName}:${imageTag}" `
            --registry-server "${acrName}.azurecr.io" `
            --registry-username $acrUsername `
            --registry-password $acrPassword `
            --target-port 8000 `
            --ingress external `
            --cpu 0.5 `
            --memory 1Gi `
            --min-replicas 1 `
            --max-replicas 3 `
            --user-assigned $identityName
        Write-Success "Container App created"
    }
    
    # Get public URL
    $fqdn = az containerapp show `
        --name $appName `
        --resource-group $ResourceGroupName `
        --query "properties.configuration.ingress.fqdn" -o tsv
    
    Write-Success "Deployment complete!"
    Write-Info "Your app is available at: https://$fqdn"
    Write-Info "View the UI: https://$fqdn/static/index.html"
    
} catch {
    Write-Error "Failed to deploy Container App: $_"
}

# Step 11: Verification
Write-Section "Step 11: Verification"
try {
    Write-Info "Checking Container App status..."
    az containerapp show `
        --name $appName `
        --resource-group $ResourceGroupName `
        --query "{name:name, status:properties.provisioningState, url:properties.configuration.ingress.fqdn}"
    
    Write-Success "All resources deployed successfully!"
    Write-Info "Resource Group: $ResourceGroupName"
    Write-Info "Container App: $appName"
    Write-Info "Container Registry: $acrName"
    Write-Info "Key Vault: $keyVaultName"
} catch {
    Write-Error "Failed to verify deployment: $_"
}

Write-Section "Deployment Summary"
Write-Success "Deployment script completed!"
Write-Info "Next steps:"
Write-Info "1. Visit: https://$fqdn/static/index.html"
Write-Info "2. Add your API secrets to Key Vault (if not done above)"
Write-Info "3. Monitor logs: az containerapp logs show --name $appName --resource-group $ResourceGroupName --container-name $appName"
Write-Info "4. View in Azure Portal: https://portal.azure.com"
