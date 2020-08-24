"""
Functions related to file paths and folder structures
"""
import os
import re

import pymel.core as pm


def get_workspace_root():
    """
    :return: Get the workspace root and return its path.
    :rtype: str
    """
    return os.path.normpath(pm.workspace(query=True, rootDirectory=True))


def get_data_folder():
    """
    :return: Get the current workspace's data folder.
    :rtype: str
    """
    return os.path.join(get_workspace_root(), 'data')


def get_skin_pack_folder(create=False):
    """
    :param bool create: If True will create the folder if it is missing.
                        If False and the folder does not exist will return None.
    :return: Get the Current skin pack folder inside the data folder.
    :rtype: str|None
    """
    skin_pack_folder = os.path.join(get_data_folder(), 'skinPacks')

    if os.path.exists(skin_pack_folder):
        return skin_pack_folder
    else:
        if create:
            os.mkdir(skin_pack_folder)
            return skin_pack_folder


def get_files(target_folder, extension):
    """
    Get all the files in a folder filtered by file extension.

    :param str target_folder: Target folder to look into.
    :param str extension: File extension to filter by. eg: '.png'
    :return: List of all the files found.
    """
    # Getting all files ending in .suffix + returning them
    return [file for file in os.listdir(target_folder) if file.endswith(extension)]


def find_latest_file(target_folder, extension, full_path=True):
    """
    Finds the latest file in a sub folder of the data folder

    :param str target_folder: Target folder to look into.
    :param str extension: .extension of files to use as a filter.
    :param bool full_path: If True will return the full path to the file if found.
    :return latest_file : Path to the latest file
    :rtype: str
    """
    # Getting all files ending in .suffix
    all_files = get_files(target_folder, extension)

    # finding the file that has the highest index
    if all_files:
        latest_file = None
        biggest_index = None
        for file in all_files:
            result = re.search(r'_v\d\d\d', file)
            if result:
                str_index = file.split('_v')[-1].split(extension)[0]
                file_index = int(str_index)
                if biggest_index is None:
                    biggest_index = file_index
                    latest_file = file
                else:
                    if file_index > biggest_index:
                        biggest_index = file_index
                        latest_file = file
        if latest_file:
            return latest_file if not full_path else os.path.join(target_folder, latest_file)


def version_from_name(path):
    """
    Get the file version from the name provided that the file fits the naming convention.

    :param str path: Path to the file.
    :return: Version number
    :rtype: int
    :raises: ValueError if the path does not match the version convention.
    """
    if re.search(r'_v\d\d\d\.', path):
        # Format out the version number and return it as an int
        return int(path.split('.')[0][-3:])
    else:
        raise ValueError('{} Does not match the version naming convention'.format(path))
