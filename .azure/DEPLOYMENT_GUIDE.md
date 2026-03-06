# Azure Deployment Guide: Future Self Simulator

**Deployment Date**: March 5, 2026  
**Subscription ID**: `09da0fd9-ddb6-4b5b-ae46-eaae2670b37e`  
**Region**: `eastus`  
**Project**: Future Self Simulator AI Agent

---

## STEP 1: Install Azure CLI (One-time setup)

Azure CLI is not currently on your system. Choose **one** of these methods:

### Method A: Download & Run Installer (Easiest)
1. Go to: https://aka.ms/installazurecliwindows
2. Download the `.msi` file
3. Double-click and follow the installer wizard
4. Restart PowerShell/Terminal after installation
5. Test: Open PowerShell and run `az --version`

### Method B: Use Scoop (if installed)
```powershell
scoop install azure-cli
```

### Method C: Use Chocolatey (if installed)
```powershell
choco install azure-cli
```

---

## STEP 2: Login to Azure

After Azure CLI is installed and you've restarted your terminal:

```powershell
# Login to Azure (opens browser window)
az login

# Set your subscription
az account set --subscription "09da0fd9-ddb6-4b5b-ae46-eaae2670b37e"

# Verify
az account show --query "{subscriptionId:id, tenantId:tenantId}"
```

---

## STEP 3: Create Resource Group

```powershell
# Create resource group in eastus
az group create `
  --name "rg-future-self-simulator" `
  --location "eastus"

# Verify
az group show --name "rg-future-self-simulator"
```

---

## STEP 4: Deploy Infrastructure (Bicep IaC)

The deployment plan includes a Bicep template. Run:

```powershell
# Navigate to your project directory
cd "c:\Users\sanja\Downloads\Future Self Simulator AI Agent"

# Deploy resources (if bicep template is in .azure/ folder)
# Option A: If you have a bicep file
az deployment group create `
  --resource-group "rg-future-self-simulator" `
  --template-file ".\.azure\main.bicep" `
  --parameters `
    projectName="Future Self Simulator" `
    location="eastus" `
    containerImageVersion="latest"

# Option B: Create individual resources manually (script below)
```

---

## STEP 5: Create Azure Container Registry (ACR)

```powershell
# Create container registry
$acrName = "acsfutureselfsimulattor"  # Must be alphanumeric, globally unique

az acr create `
  --resource-group "rg-future-self-simulator" `
  --name $acrName `
  --sku Basic `
  --admin-enabled true

# Get login credentials
az acr credential show `
  --resource-group "rg-future-self-simulator" `
  --name $acrName

# Save: SERVER, USERNAME, passwords (you'll need these)
```

---

## STEP 6: Build & Push Docker Image to ACR

```powershell
# Set variables
$acrName = "acsfutureselfsimulattor"
$imageName = "future-self-simulator"
$imageTag = "latest"

# Navigate to project root
cd "c:\Users\sanja\Downloads\Future Self Simulator AI Agent"

# Build and push in one command
az acr build `
  --registry $acrName `
  --image "${imageName}:${imageTag}" `
  --file Dockerfile `
  .

# Verify image was pushed
az acr repository show `
  --name $acrName `
  --repository $imageName
```

---

## STEP 7: Create User-Assigned Managed Identity

```powershell
$identityName = "mi-future-self-simulator"

# Create managed identity
az identity create `
  --resource-group "rg-future-self-simulator" `
  --name $identityName

# Get the principal ID (save this)
$principalId = az identity show `
  --resource-group "rg-future-self-simulator" `
  --name $identityName `
  --query "principalId" -o tsv

Write-Host "Managed Identity Principal ID: $principalId"
```

---

## STEP 8: Create Azure Key Vault

```powershell
$keyVaultName = "kv-futureself-sim"  # Must be unique, alphanumeric + hyphens

# Create Key Vault
az keyvault create `
  --resource-group "rg-future-self-simulator" `
  --name $keyVaultName `
  --location "eastus"

# Grant Managed Identity access to Key Vault
$identityName = "mi-future-self-simulator"
$principalId = az identity show `
  --resource-group "rg-future-self-simulator" `
  --name $identityName `
  --query "principalId" -o tsv

az keyvault set-policy `
  --name $keyVaultName `
  --object-id $principalId `
  --secret-permissions get list

# Add your API secrets to Key Vault
# (Replace with your actual API keys)
az keyvault secret set `
  --vault-name $keyVaultName `
  --name "AZURE-OPENAI-API-KEY" `
  --value "your-actual-api-key-here"

az keyvault secret set `
  --vault-name $keyVaultName `
  --name "AZURE-OPENAI-ENDPOINT" `
  --value "https://your-resource.openai.azure.com/"

az keyvault secret set `
  --vault-name $keyVaultName `
  --name "AZURE-OPENAI-DEPLOYMENT" `
  --value "your-deployment-name"


```

---

## STEP 9: Create Application Insights & Log Analytics

```powershell
# Create Log Analytics Workspace
$workspaceName = "law-future-self-simulator"

az monitor log-analytics workspace create `
  --resource-group "rg-future-self-simulator" `
  --workspace-name $workspaceName

# Get Workspace ID
$workspaceId = az monitor log-analytics workspace show `
  --resource-group "rg-future-self-simulator" `
  --workspace-name $workspaceName `
  --query "id" -o tsv

# Create Application Insights
$appInsightsName = "ai-future-self-simulator"

az monitor app-insights component create `
  --app $appInsightsName `
  --location "eastus" `
  --resource-group "rg-future-self-simulator" `
  --workspace $workspaceName

# Get Instrumentation Key
$instrKey = az monitor app-insights component show `
  --app $appInsightsName `
  --resource-group "rg-future-self-simulator" `
  --query "instrumentationKey" -o tsv

Write-Host "Instrumentation Key: $instrKey"
```

---

## STEP 10: Create Container App Environment

```powershell
# Create Container App Environment
$envName = "cae-future-self-simulator"

az containerapp env create `
  --name $envName `
  --resource-group "rg-future-self-simulator" `
  --location "eastus"
```

---

## STEP 11: Deploy to Azure Container Apps

```powershell
# Set variables
$appName = "ca-future-self-simulator"
$envName = "cae-future-self-simulator"
$acrName = "acsfutureselfsimulattor"
$imageName = "future-self-simulator"
$imageTag = "latest"
$identityName = "mi-future-self-simulator"
$keyVaultName = "kv-futureself-sim"

# Create Container App
az containerapp create `
  --name $appName `
  --resource-group "rg-future-self-simulator" `
  --environment $envName `
  --image "${acrName}.azurecr.io/${imageName}:${imageTag}" `
  --registry-server "${acrName}.azurecr.io" `
  --registry-username (az acr credential show -n $acrName -o tsv --query username) `
  --registry-password (az acr credential show -n $acrName -o tsv --query "passwords[0].value") `
  --target-port 8000 `
  --ingress external `
  --cpu 0.5 `
  --memory 1Gi `
  --min-replicas 1 `
  --max-replicas 3 `
  --user-assigned $identityName `
  --env-vars `
    "AZURE_KEY_VAULT_URL=https://${keyVaultName}.vault.azure.net/"

# Get the public URL
az containerapp show `
  --name $appName `
  --resource-group "rg-future-self-simulator" `
  --query "properties.configuration.ingress.fqdn" -o tsv
```

---

## STEP 12: Verify Deployment

```powershell
# Check Container App status
az containerapp show `
  --name "ca-future-self-simulator" `
  --resource-group "rg-future-self-simulator" `
  --query "{name:name, status:properties.provisioningState, fqdn:properties.configuration.ingress.fqdn}"

# Check logs
az containerapp logs show `
  --name "ca-future-self-simulator" `
  --resource-group "rg-future-self-simulator" `
  --container-name "ca-future-self-simulator"

# Test the app
# Get FQDN from step above and visit: https://<FQDN>/static/index.html
```

---

## Environment Variables Mapping

Your app expects these environment variables. Update as needed in Key Vault:

```
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_DEPLOYMENT=<your-deployment>
AZURE_OPENAI_MODEL=gpt-4o
```

---

## Troubleshooting

**Azure CLI not found after install?**
- Restart PowerShell/Terminal completely
- Check PATH: `$env:PATH`
- If still missing, reinstall from: https://aka.ms/installazurecliwindows

**Container App not starting?**
```powershell
# View logs
az containerapp logs show --name ca-future-self-simulator --resource-group rg-future-self-simulator --follow
```

**Image not found in registry?**
```powershell
# List images in ACR
az acr repository list --name acsfutureselfsimulattor
```

---

## Quick Cleanup (if needed)

```powershell
# Delete entire resource group and all resources
az group delete --name "rg-future-self-simulator" --yes --no-wait
```

---

## Next Steps

1. ✅ **Download & Install Azure CLI** (https://aka.ms/installazurecliwindows)
2. ⏳ **Follow Steps 2-12** above in order
3. ✅ **Get your public URL** from Step 12
4. ✅ **Test app** by visiting the HTTPS URL
5. ✅ **Monitor** in Azure Portal

**Estimated time**: ~20-30 minutes for first deployment
