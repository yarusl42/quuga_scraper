import os
from pathlib import Path


def generator_split_to_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_parent_dirs(file_path):
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)


def create_parent_dirs_dirpath(dir_path):
    create_parent_dirs(os.path.join(dir_path, 'a'))
