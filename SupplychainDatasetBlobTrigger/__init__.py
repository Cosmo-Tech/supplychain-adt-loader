import logging
import os
import re
import tempfile
import uuid

import azure.functions as func
from Supplychain.Generic.adt_writer import ADTWriter
from Supplychain.Generic.excel_folder_reader import ExcelReader
from Supplychain.Generic.memory_folder_io import MemoryFolderIO
from Supplychain.Generic.storage_queue_writer import QueueWriter
from Supplychain.Transform.from_table_to_dict import write_transformed_data
from Supplychain.Generic.timer import Timer

messages_order = ['Stock',
                  'ProductionOperation',
                  'ProductionResource',
                  'input',
                  'output',
                  'contains',
                  'Transport']

def __sanitize_adt_id(input: str) -> str:
    """
    Replace any non alphanumeric character by a '_' character
    This method is used to avoid limitations with identifiers in ADT
    :param input: input string
    :return: output string
    """
    return re.sub("[^0-9a-zA-Z]+", "_", input)
    
def convert(input_folder: str, for_adt: bool = True, for_queue: bool = False) -> MemoryFolderIO:
    with Timer("[Convert dataset]") as t:
        dataset = ExcelReader(input_folder=input_folder, keep_nones=False)
        t.split("Read dataset")
        intermediate = MemoryFolderIO()
        reading_errors = write_transformed_data(
            reader=dataset,
            writer=intermediate,
        )
        if reading_errors:
            exit(1)

        if for_adt:
            # Add missing metadata to entities
            metadatas = {
                'Stock': {
                    "$metadata": {"$model": 'dtmi:com:cosmotech:supplychain:Stock;1'}
                },
                'ProductionOperation': {
                    "$metadata": {"$model": 'dtmi:com:cosmotech:supplychain:ProductionOperation;1'}
                },
                'ProductionResource': {
                    "$metadata": {"$model": 'dtmi:com:cosmotech:supplychain:ProductionResource;1'}
                },
                'input': {
                    "$relationshipName": "input"
                },
                'output': {
                    "$relationshipName": "output"
                },
                'contains': {
                    "$relationshipName": "contains"
                },
                'Transport': {
                    "$relationshipName": "Transport"
                }
            }
            for entity_name, content in metadatas.items():
                _file = intermediate.files.get(entity_name, [])
                for entity in _file:
                    entity.update(content)

            # rename columns and sanitize
            renames = {
                "id": "$id",
                "source": "$sourceId",
                "target": "$targetId"
            }
            for _file_name, _file_content in intermediate.files.items():
                for entity in _file_content:
                    for original_column, new_column in renames.items():
                        if None in entity:
                            del entity[None]
                        if new_column not in entity and original_column in entity:
                            entity[new_column] = __sanitize_adt_id(entity[original_column])
                            del entity[original_column]
                    if for_queue and "$sourceId" in entity and "$targetId" in entity and "$relationshipId" not in entity:
                        entity.setdefault('$relationshipId', str(uuid.uuid1()))
                        entity["relationship"] = entity.copy() # dt injector requires a relationship member
        t.split("Convert to dict")
        return intermediate

def direct_to_adt(input_folder: str, force_purge: bool):
    intermediate = convert(input_folder)
    with Timer("[Send to ADT]") as t:
        adt_writer = ADTWriter(force_purge=force_purge)
        for table_name in messages_order:
            table_content = intermediate.files.get(table_name, list())
            adt_writer.send_items(items=table_content)
            t.display_message(f"Sent {table_name}")
        t.display_message("Send to ADT")


def to_storage_queue(input_folder: str,
                     connection_str: str,
                     queue_name: str):
    intermediate = convert(input_folder, for_queue = True)
    with Timer("[Send to queue]") as t:
        queue_writer = QueueWriter(connection_str,
                                   queue_name)
        for table_name in messages_order:
            table_content = intermediate.files.get(table_name, list())
            queue_writer.send_items(items=table_content)
            t.display_message(f"Sent {table_name}")
        t.display_message("Send to queue")

def main(myblob: func.InputStream):

    head, filename = os.path.split(myblob.name)
    logging.info(f"Python blob trigger function processed blob \n"
                 f"File Name: {filename}\n"
                 f"Excel Size: {myblob.length} bytes")

    input_folder = tempfile.gettempdir()
    with open(os.path.join(input_folder, filename), 'wb') as input_file:
         input_file.write(myblob.read())

    output_mode = os.environ.get("OUTPUT_MODE", None)

    
    if output_mode == "queue":
        queue_connection = os.environ.get("QUEUE_STORAGE_CONNECTION", None)
        queue_name = os.environ.get("QUEUE_STORAGE_NAME", None)
        if not queue_connection or not queue_name:
            raise Exception(f"Configuration issue !\n"
                 f"Provide parameter for 'QUEUE_STORAGE_CONNECTION' and 'QUEUE_STORAGE_NAME' when 'OUTPUT_MODE' is 'queue'.\n")
        to_storage_queue(input_folder, queue_connection, queue_name)

    elif output_mode == "adt":
        adt_force_purge = bool(os.environ.get("AZURE_DIGITAL_TWINS_PURGE_BEFORE_LOAD", False))
        if "AZURE_DIGITAL_TWINS_URL" not in os.environ:
            raise Exception(f"Configuration issue ! 'AZURE_DIGITAL_TWINS_URL' not provided .")
        direct_to_adt(input_folder, adt_force_purge)

    else:
        raise Exception(f"Configuration issue !\n"
                 f"'OUTPUT_MODE' not configured properly.\n"
                 f"Set 'queue' or 'adt'.\n")
