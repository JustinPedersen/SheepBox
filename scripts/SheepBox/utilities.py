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


def match_to_geo():
    """
    Helper function to match the first selected object to the second selected mesh object.
    """
    user_sel = pm.ls(sl=True)

    _, temp_cluster = pm.cluster(user_sel[-1])
    pm.matchTransform(user_sel[0], temp_cluster, position=True, rotation=False, scale=False)
    pm.delete(temp_cluster)
