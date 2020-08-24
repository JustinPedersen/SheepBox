"""
Functions related to Nurbs Curves within Maya
"""
import pymel.core as pm


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
