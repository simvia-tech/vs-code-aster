# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Synchronizer
------------

Implementation of the tree synchronization functions.

"""



def synchronize(root_src, root_dst, tree_data):
    """
    Synchronize the given items.

    Compares two trees recursively and updates destination tree to
    correspond to the source tree. Returns destination root item which
    can be the same as input `root_dst` or new one if it is re-created.

    Arguments:
        root_src (any): Source root item.
        root_dst (any): Destination root item.
        tree_data (any): Tree data comparator object.

    Returns:
        any: Updated destination root item.
    """
    if tree_data.is_equal(root_src, root_dst):
        tree_data.update_item(root_src, root_dst)
        synchronize_children(root_src, root_dst, tree_data)
        return root_dst

    new_root_dst = tree_data.create_item(root_src)
    synchronize_children(root_src, new_root_dst, tree_data)
    return new_root_dst


def synchronize_children(root_src, root_dst, tree_data):
    """
    Synchronize child items.

    Compares child items of given root items by calling `synchronize()`
    function properly.

    Arguments:
        root_src (any): Source root item.
        root_dst (any): Destination root item.
        tree_data (any): Tree data comparator object.
    """
    children_src = tree_data.get_src_children(root_src)
    children_dst = tree_data.get_dst_children(root_dst)
    new_children_dst = []
    for c_src in children_src:
        c_dst = get_dst_child(c_src, children_dst, tree_data)
        new_children_dst.append(c_dst)
        synchronize(c_src, c_dst, tree_data)
    tree_data.replace_dst_children(root_dst, new_children_dst)


def get_dst_child(root_src, children_dst, tree_data):
    """
    Get a destination child item that corresponds to the source item.

    Arguments:
        root_src (any): Source item.
        children_dst (list[any]): List of destination child items.
        tree_data (any): Tree data comparator object.

    Returns:
        any: Destination item.
    """
    for c_dst in children_dst:
        if tree_data.is_equal(root_src, c_dst):
            return c_dst
    new_dst = tree_data.create_item(root_src)
    return new_dst
