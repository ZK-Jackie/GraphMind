def dict_list_remove_dup(dict_list: list[dict], unique_prop: str) -> list[dict]:
    """
    Remove duplicated dict in a list of dict.
    :param dict_list: list of dict
    :return: list of dict
    """
    unique_set = set()
    result = []
    for item in dict_list:
        if item[unique_prop] not in unique_set:
            result.append(item)
            unique_set.add(item[unique_prop])
    return result
