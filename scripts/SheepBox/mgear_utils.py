"""
mGear related helper functions
"""
import pymel.core as pm

import mgear.core.skin as skin

import SheepBox.path as sb_path
import SheepBox.skin as sb_skin


def save_new_skin_pack():
    """
    Helper function to find the latest skin pack in the data/skinPacks folder, version up and save out
    a skin pack for all geo in the scene.
    """
    extension = '.gSkinPack'
    skin_path = sb_path.get_skin_pack_folder(create=False)
    highest_skin_pack = sb_path.find_latest_file(skin_path, extension, full_path=True)

    # versioning up the latest file
    file_index = sb_path.version_from_name(highest_skin_pack)
    new_name = highest_skin_pack.replace(str(file_index).zfill(3), str(file_index + 1).zfill(3))

    # Getting the skinned Geo
    skined_geo = sb_skin.get_skinned_geo()

    skin.exportJsonSkinPack(packPath=new_name, objs=skined_geo)
