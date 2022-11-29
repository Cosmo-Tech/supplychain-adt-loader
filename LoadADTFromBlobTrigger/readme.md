# Supply Chain Azure Digital Twins loader


## How it works

This Azure function is intended to load an Azure Digital Twins instance from an Cosmo Tech Supply Chain dataset.<br>
data Azuer To trigger a load a Azure Digital Twins instance  (parameter `AZURE_DIGITAL_TWINS_URL`), upload a Cosmo Tech Supply Chain dataset Excel file (`.xlsx` extension) into the configured container (parameter `INPUT_STORAGE_CONTAINER`, `/Input` by default) of the configured Azure Storage (connection string parameter `INPUT_STORAGE_CONNECTION`).

**IMPORTANT : Azure Digital Twins model, dataset Excel file and Azure function versions must be aligned**


## Learn more

<TODO> Documentation

## Pre-requisites

### Azure function identity
Azure Function > Settings > Identity > System assigned > Status = ON

### Azure Digital Twins persmissions
Azure Digital Twins > IAM > Add role assignment > Azure Digital Twins Data Owner > Managed identity = the created function app

## Configuration


* **INPUT_STORAGE_CONNECTION** : connection string of the Azure Storage account
* **INPUT_STORAGE_CONTAINER** : BLOB container in the Storage

* **AZURE_DIGITAL_TWINS_URL** : Azure Digital Twins URL
* **AZURE_DIGITAL_TWINS_PURGE_BEFORE_LOAD** : indicates if the Azure Digital Twins instance is purged before being loaded


## Development environment

* Function App resource group
https://portal.azure.com/#@cosmotech.com/resource/subscriptions/a24b131f-bd0b-42e8-872a-bded9b91ab74/resourceGroups/supplychainadtloaderdev


