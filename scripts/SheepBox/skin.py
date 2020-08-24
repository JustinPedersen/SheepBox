"""
Methods related to Maya Skinning.
"""
import pymel.core as pm


def get_skinned_geo():
    """
    Helper function to get all geo in the scene that has a skin cluster attatched.

    :return: List of geo that has a skin cluster.
    :rtype: list[PyNode]
    """
    skinned_geo = []
    for skin_cluster in pm.ls(type="skinCluster"):
        for shape in skin_cluster.getGeometry():
            skinned_geo.append(shape.firstParent())

    return skinned_geo


def copy_skin_influence(from_obj, to_obj):
    """
    Copy Joint influence and skin weights form one object ot another.

    :param PyNode from_obj: Object to copy weights from.
    :param PyNode to_obj: Object to copy weights to.
    :return: The created skin cluster
    :rtype: PyNode
    """
    skinned_joints = pm.skinCluster(from_obj, query=True, influence=True)
    result_skin = pm.skinCluster(skinned_joints, to_obj)
    pm.copySkinWeights(from_obj,
                       to_obj,
                       noMirror=True,
                       surfaceAssociation='closestPoint',
                       influenceAssociation='closestJoint')

    return result_skin


def bind_mirror_weights(from_obj, to_obj):
    """
    Helper function to bind the mirror joints from object A to object B.
    Will only operate if there is no skin cluster on to_obj.

    :param PyNode from_obj: Object to copy influence from.
    :param PyNode to_obj: Object to copy influence to.
    """
    # Check for skin cluster
    for hist in pm.listHistory(to_obj):
        if pm.nodeType(hist) == 'skinCluster':
            return

    # If none found, find the opposite joints and bind them.
    skinned_joints = pm.skinCluster(from_obj, query=True, influence=True)

    # Swap the _L for _R + Convert them to pynodes
    # TODO: Find a better _L _R method
    mirror_joint_names = [pm.PyNode(jnt.name().replace('_L', '_R')) for jnt in skinned_joints]

    return pm.skinCluster(mirror_joint_names, to_obj, toSelectedBones=True)


def mirror_transfer_skin_weights():
    """
    Helper function to mirror weights from two pieces of geo that are separate.
    Selection order: This -> That
    """
    user_sel = pm.ls(sl=True)

    # TODO: More robust way of finding from and to objects.
    from_object = user_sel[0]
    to_object = pm.PyNode(from_object.replace('_L', '_R'))

    # If the to object has no skin cluster, add one best we can.
    bind_mirror_weights(from_object, to_object)

    # Duplicate and combine the pieces
    duplicate_pieces = pm.duplicate([from_object, to_object])
    combined_geo, _ = pm.polyUnite(*duplicate_pieces,
                                   ch=1,
                                   mergeUVSets=1,
                                   centerPivot=True,
                                   name='TEMP_combined_mirror_geo')

    # Delete history
    pm.delete(combined_geo, constructionHistory=True)

    skin_cluster = copy_skin_influence(from_object, combined_geo)

    # Mirroring the skin cluster
    pm.copySkinWeights(ss=skin_cluster,
                       ds=skin_cluster,
                       mirrorMode='YZ',
                       surfaceAssociation='closestPoint',
                       influenceAssociation='closestJoint')

    # Final copy skin weights to target geo
    pm.copySkinWeights(combined_geo,
                       to_object,
                       noMirror=True,
                       surfaceAssociation='closestPoint',
                       influenceAssociation='closestJoint')

    # Cleanup
    pm.delete(combined_geo)
    pm.delete(duplicate_pieces)
    pm.select(user_sel, r=True)
    print('Copying Complete!')
