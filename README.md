# SupplychainDatasetBlobTrigger

Azure function to load Azure Digital Twins instance from Supply Chain Dataset


**IMPORTANT : Azure Digital Twins model, dataset Excel file and Azure function versions must be aligned.**


### How it works

This Azure function is intended to process a Cosmo Tech Supply Chain dataset in order to load it into an Azure Digital Twins instance.<br>

1. To trigger the function `SupplychainDatasetBlobTrigger`, upload a Cosmo Tech Supply Chain dataset Excel file (`.xlsx` extension) into the configured container (parameter `INPUT_STORAGE_CONTAINER`, `/Input` by default) of the configured Azure Storage (connection string parameter `INPUT_STORAGE_CONNECTION`).<br>
2. Once triggered the function transforms the dataset into twin and relationships objects.<br>
3. Then the azure function sends these objects to a storage queue configured with parameters `OUTPUT_STORAGE_CONNECTION` and `OUTPUT_STORAGE_QUEUE_NAME`.<br>
4. The storage queue is consumed by an [DT Injector Azure Function](https://github.com/Cosmo-Tech/azure-digital-twin-injector).
<br>

## Pre-requisites

An existing Azure Digital Twins instance and an instance of [DT Injector Azure Function](https://github.com/Cosmo-Tech/azure-digital-twin-injector) installed and configured.
<br>
## Permissions

In order for the azure function to **receive data to the input storage container** : 
- Set Azure Function > Settings > Identity > System assigned > Status = ON
- The Azure function identity has to be declared as `Storage Blob Data Reader`
Or put a valid `AccountKey` for the parameter `INTPUT_STORAGE_CONNECTION`


In order for the azure function to **send data to the output storage queue** : 
- Set Azure Function > Settings > Identity > System assigned > Status = ON
- The Azure function identity has to be declared as `Storage Queue Data Message Sender`
Or put a valid `AccountKey` for the parameter `OUTPUT_STORAGE_CONNECTION`
<br>
## Settings

* **INPUT_STORAGE_CONNECTION** : connection string of the input Azure Storage account
* **INPUT_STORAGE_CONTAINER** : BLOB container name in the input Storage

* **OUTPUT_STORAGE_QUEUE_NAME** : connection string of the output Azure Storage account
* **OUTPUT_STORAGE_QUEUE_NAME** : Queue name in the output Storage (dt injector inpout queue)


