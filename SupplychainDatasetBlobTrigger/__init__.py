import json
import logging
import os
import re
import tempfile
import typing
import uuid

import azure.functions as func
from Supplychain.Generic.excel_folder_reader import ExcelReader
from Supplychain.Generic.memory_folder_io import MemoryFolderIO
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

def main(myblob: func.InputStream, msg: func.Out[typing.List[str]]):

    head, filename = os.path.split(myblob.name)
    logging.info(f"Python blob trigger function processed blob \n"
                 f"File Name: {filename}\n"
                 f"Excel Size: {myblob.length} bytes")

    input_folder = tempfile.gettempdir()
    with open(os.path.join(input_folder, filename), 'wb') as input_file:
         input_file.write(myblob.read())

    msg_list = []
    intermediate = convert(input_folder, for_queue = True)
    for table_name in messages_order:
        table_content = intermediate.files.get(table_name, list())
        
        total_messages = len(table_content)
        for item in table_content:
            message = json.dumps(item, separators=(',', ':'))
            msg_list.append(message)
    msg.set(msg_list)  
