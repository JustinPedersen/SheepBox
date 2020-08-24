import pymel.core as pm


def lock_hide_attrs(node, translate=False, rotate=False, scale=False, shape=False):
    """
    Will lock and hide all the specified attrs
    """
    channels_to_lock = []
    if translate:
        channels_to_lock.append('translate')
    if rotate:
        channels_to_lock.append('rotate')
    if scale:
        channels_to_lock.append('scale')

    for channel in channels_to_lock:
        for ax in ['X', 'Y', 'Z']:
            node.attr(channel + ax).lock(True)
            pm.setAttr(node.attr(channel + ax), keyable=False, channelBox=False)

    if shape:
        shape_nodes = pm.listRelatives(node, shapes=True)
        for shape in shape_nodes:
            shape.lodVisibility.set(False)
