def info_tree_serializer():
    return {
        "InfoTreeTaskResult": {
            "source": "str | list | None",
            "entity": "str | list | None",
            "relation": "str | list | None",
            "others": "str | dict | None"
        },
        "InfoTreeTask": {
            "task_id": "str",
            "task_prompt": "str",
            "task_response": "InfoTreeTaskResult",
            "task_status": "str"
        }
    }