# GraphMind File Structure
tree_type = ["TREE"]
raw_type = ["RAW"]


# GraphMind Engine File Support and Structure Support
HIERARCHY_STRUCT_SUPPORT = tree_type
HIERARCHY_FILE_SUPPORT = ["md"]


CHUNK_STRUCT_SUPPORT = raw_type
CHUNK_FILE_SUPPORT = ["md", "txt", "csv"]


CASCADE_STRUCT_SUPPORT = raw_type + tree_type
CASCADE_FILE_SUPPORT = ["md", "txt", "csv"]
