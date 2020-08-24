"""
General Utilities for Maya related operations.
"""
import pymel.core as pm


def selection_filter():
    """
    TODO: Create an easy filter for number of items selected.
    """


def delete_all_namespaces():
    """
    Delete all the namespaces in the scene and merge them with the root.
    """
    namespaces = pm.listNamespaces(recursive=True, internal=False)
    for ns in reversed(namespaces):
        pm.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)

    print('{} name spaces removed'.format(len(namespaces)))


def get_shapes(items=None, shape_filter=('mesh', 'nurbsCurve')):
    """
    Get all shapes from the item list. If none given will use the user selection.

    :param list items: PyNodes to operate on. If none given will use selection.
    :param list shape_filter: Whitelist filter for acceptable shape types.
    :return: List of all the shapes as PyNodes.
    :rtype: list[PyNode]
    """
    items = pm.ls(sl=True) if not items else items

    all_shapes = []
    for item in items:
        for shape in pm.listRelatives(item, shapes=True):
            if pm.nodeType(shape) in shape_filter:
                all_shapes.append(shape)

    return all_shapes


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


def match_to_geo():
    """
    Helper function to match the first selected object to the second selected mesh object.
    """
    user_sel = pm.ls(sl=True)

    _, temp_cluster = pm.cluster(user_sel[-1])
    pm.matchTransform(user_sel[0], temp_cluster, position=True, rotation=False, scale=False)
    pm.delete(temp_cluster)


def colour_iu():
    """
    Open up maya's colour picker UI and return the result of what the user selected.
    Will return blank dict if the user closes the ui.

    :return: Dict of the result
    :rtype: dict
    """
    pm.colorEditor()
    result = {}
    if pm.colorEditor(query=True, result=True):
        result['RGB'] = pm.colorEditor(query=True, rgb=True)
        result['HSV'] = pm.colorEditor(query=True, hsv=True)
        result['Alpha'] = pm.colorEditor(query=True, alpha=True)
    else:
        print('Editor was dismissed')

    return result


def set_colour():
    """
    Set the RGB colour on all currently selected Nurbs Curves.
    """
    # Open the colour ui and capture the result.
    colour_result = colour_iu()
    if colour_result:
        # Iterate over all shapes
        for shape in get_shapes(pm.ls(sl=True), ['nurbsCurve']):

            # Set the Overrides and selected RGB colour
            pm.setAttr(shape.overrideEnabled, 1)
            pm.setAttr(shape.overrideRGBColors, 1)
            for colour, value in zip(["R", "G", "B"], colour_result['RGB']):
                pm.setAttr(shape.attr('overrideColor{}'.format(colour)), value)
