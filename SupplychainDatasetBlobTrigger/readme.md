# SupplychainDatasetBlobTrigger

**IMPORTANT : Azure Digital Twins model, dataset Excel file and Azure function versions must be aligned**


### How it works

This Azure function is intended to process a Cosmo Tech Supply Chain dataset in order to load it into an Azure Digital Twins instance.<br>

To trigger the function `SupplychainDatasetBlobTrigger`, upload a Cosmo Tech Supply Chain dataset Excel file (`.xlsx` extension) into the configured container (parameter `INPUT_STORAGE_CONTAINER`, `/Input` by default) of the configured Azure Storage (connection string parameter `INPUT_STORAGE_CONNECTION`).<br>
We have 2 modes  of loading the dataset into ADT (parameter `OUTPUT_MODE`): 
1. ADT Direct load with parameter `OUTPUT_MODE`: `adt`. This requires to provide the Azure Digital Twins URL in parameter `AZURE_DIGITAL_TWINS_URL`
2. Load via Storage queue with parameter `OUTPUT_MODE`: `queue`. The queue is consumed and trigger a ADT loading by a [DT Injector Azure Function](https://github.com/Cosmo-Tech/azure-digital-twin-injector). This mode requires to provide the parameters `QUEUE_STORAGE_CONNECTION` and `QUEUE_STORAGE_NAME`



## Pre-requisites

### Azure function identity
Azure Function > Settings > Identity > System assigned > Status = ON

### Azure Digital Twins persmissions (requires only if mode is `adt`)
Azure Digital Twins > IAM > Add role assignment > Azure Digital Twins Data Owner > Managed identity = the created function app

## Configuration

* **OUTPUT_MODE** : output mode of the Azure Function : **Azure Digital Twins load** with `adt` or via **Azure Storage Queue** with parameter `queue`

* **INPUT_STORAGE_CONNECTION** : connection string of the input Azure Storage account
* **INPUT_STORAGE_CONTAINER** : BLOB container name in the input Storage

* **AZURE_DIGITAL_TWINS_URL** : Azure Digital Twins URL
* **AZURE_DIGITAL_TWINS_PURGE_BEFORE_LOAD** : indicates if the Azure Digital Twins instance is purged before being loaded (on available with `OUTPUT_MODE`: `adt`)

* **QUEUE_STORAGE_NAME** : connection string of the output Azure Storage account
* **QUEUE_STORAGE_NAME** : Queue name in the output Storage


