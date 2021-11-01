prescription_schema = {
    "type": "object",
    "properties": {
        "clinic": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number"
                }
            }
        },
        "physician": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number"
                }
            }
        },
        "patient": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number"
                }
            }
        },
        "text": {
            "type": "string"
        }
    }
}
