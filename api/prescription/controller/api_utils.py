import json


def validate_json(raw_data: str) -> bool:
    """
    Validates if the incoming data is a valid json document
    :param raw_data:
    :return:
    """
    try:
        json.loads(raw_data)
    except ValueError:
        return False
    return True


def validate_schema(schema, document) -> bool:
    """
Validates a JSON document against a schema
    :param schema: a schema for validating a json document
    :param document: a json document
    :return: True if document is compliant with schema
    """
    schema.validate(document)
    return schema.is_valid(document)
