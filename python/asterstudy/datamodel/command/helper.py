# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D i
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
Command Helpers
---------------

Helper functionality for Command implementation.

"""


from ...common import (MeshGroupType,
                       recursive_items, recursive_setter)
from ..abstract_data_model import add_parent, remove_parent
from ..visit_study import (FilterVisitor, UnitVisitor,
                           GroupFilterVisitor, GroupNameFilterVisitor,
                           expects_grma, filter_groups, filter_tout,
                           get_related, LEVEL_2_COMMANDS)
from ..general import ConversionLevel, FileAttr
from ..catalogs import CATA

def register_cos(stage, command, pool_co=None, conversion=False):
    """Properly register all CO command args via producing corresponding
    hiddens.

    Arguments:
        stage (Stage): The stage that the command belongs to.
        command (Command): Command object.
        pool_co (dict, optional): CO objects that existed before unregistering.

    Returns:
        dict: Pool of CO objects that have not been reused.
    """
    for path, value in command.get_list_co():
        exist = pool_co and pool_co.get(path)
        if not exist:
            hidden = stage.add_command("_RESULT_OF_MACRO", value.name)
            hidden.init(dict(DECL=value, PARENT=command, PATH=path), conversion=conversion)
        else:
            del pool_co[path]
            exist.name = value.name
            add_parent(exist, command)

def unregister_cos(command, delete=True):
    """Unregister all registered command COs via removing corresponding hiddens.

    .. note:: If the caller does not need the CO objects, it must delete them.

    Arguments:
        command (Command): Command object that have to forget CO objects.
        delete (bool): If *True*, CO objects that belongs to the command are
            deleted. Otherwise, the command is only removed from their parents
            list.

    Returns:
        dict: Pool of CO objetcs that have not been forgotten.
    """
    pool_co = {}
    for child in command.hidden:
        if child.parent_id == command.uid:
            # command is the creator of the CO
            if delete:
                child.delete()
            else:
                pool_co[child.storage_nocopy['PATH']] = child
                # The Hidden must be removed if not re-registered.
                remove_parent(child, command)
        else:
            remove_parent(child, command)
    return pool_co

def unregister_parent(command, value):
    "Unregister all value items from the command instance"
    from .basic import Command

    if isinstance(value, Command):
        remove_parent(command, value)
    elif isinstance(value, (list, tuple)):
        for item in value:
            unregister_parent(command, item)
    elif isinstance(value, dict):
        for item in value.values():
            unregister_parent(command, item)

def update_dependence_up(storage):
    """Update 'up' dependencies of a command.

    When copying a command, this ensures that it will
    be referencing copies not originals up the dependence tree.

    This command is useful when parents are copied
        before children.

    Arguments:
        storage (dict): storage object with the values of the
            current command/keyword."""
    #
    # The method is called when copying children
    #
    # Before the method is called
    # -------   ------------
    # | copy |  | original |  parent commands
    # -------   -----------
    #          ^         ^
    #         /          |    reference
    #        /           |
    # -------   ------------
    # | copy |  | original |  child commands
    # -------   -----------
    #
    # After the method has been called
    # -------   ------------
    # | copy |  | original |  parent commands
    # -------   -----------
    #     ^              ^
    #     |              |    reference
    #     |              |
    # -------   ------------
    # | copy |  | original |  child commands
    # -------   -----------
    #
    from .basic import Command
    for path, item in recursive_items(storage):
        if isinstance(item, Command) and item.ccopy is not None:
            recursive_setter(storage, path, item.ccopy)

def update_dependence_down(command, same_stage):
    """Update 'down' dependencies of a command.

    When copying a command, this ensures that other
    copied commands down the dependence tree
    will be referencing the copy not the original.

    This method is useful when children are copied
        before parents.

    Arguments:
         command(Command): command object
         same_stage(bool): *True* updates only dependence
             between commands in the same stage,
             *False* updates only dependence
             between commands in different stages.
         """
    #
    # The method is called when copying parents
    #
    # Before the method is called
    # -------   ------------
    # | copy |  | original |  parent commands
    # -------   -----------
    #          ^         ^
    #         /          |    reference
    #        /           |
    # -------   ------------
    # | copy |  | original |  child commands
    # -------   -----------
    #
    # After the method has been called
    # -------   ------------
    # | copy |  | original |  parent commands
    # -------   -----------
    #     ^              ^
    #     |              |    reference
    #     |              |
    # -------   ------------
    # | copy |  | original |  child commands
    # -------   -----------
    #
    if command.ccopy is not None:
        if same_stage:
            iterator = (i.ccopy for i in command.child_commands \
                       if i.ccopy is not None \
                           and i.ccopy.stage.number == command.stage.number)
            for child in iterator:
                _update_dependence_helper(child, command)
        if not same_stage:
            iterator = (i for i in command.child_commands \
                        if i.stage.number > command.stage.number and \
                           i.stage.parent_case is not command.stage.parent_case)
            for child in iterator:
                _update_dependence_helper(child, command)

def _update_dependence_helper(command, parent):
    def _predicate(simple):
        return simple.value is parent

    visitor = FilterVisitor(_predicate)
    command.accept(visitor)

    for keyword in visitor.keywords:
        keyword.value = parent.ccopy

    if not visitor.keywords:
        # parent was "textually" referenced: [formula|variable] -> variable
        add_parent(command, parent.ccopy)
        remove_parent(command, parent)

def register_parent(command, value):
    "Register value items in the command instance"
    from .basic import Command

    if isinstance(value, Command):
        if value.name == '_' and value.gettype(ConversionLevel.NoFail):
            value.name = "_%d" % value.uid
        add_parent(command, value)
    elif isinstance(value, (list, tuple)):
        for item in value:
            register_parent(command, item)
    elif isinstance(value, dict):
        for item in value.values():
            register_parent(command, item)


def clean_undefined(value):
    "Removes all 'keys' of None 'values'"
    if isinstance(value, (list, tuple)):
        for item in value:
            clean_undefined(item)
    elif isinstance(value, dict):
        for key, item in value.copy().items():
            if item is None:
                del value[key]
            else:
                clean_undefined(item)


def unregister_unit(command, clear=True):
    """
    Unregister all units assigned to the command.

    Arguments:
        decrement (bool): decrement reference count
            of *Info* object to *Command* object ?
        clear (bool): delete *Info* object if no longer
            used in any command ?
    """
    # Get all UNITE keywords
    visitor = UnitVisitor()
    try:
        command.accept(visitor) # the command is probably invalid
    except KeyError:
        return

    stage = command.stage
    for keyword in visitor.keywords:

        # Value of UNITE keyword (see Simple.value)
        # (as stored in the `storage` dictionnary of command content)
        value = keyword.value

        # TODO: common subfunction with `register_unit` to check validity
        # no need to test *None* value here,
        # will have been discarded by visitor
        if isinstance(value, dict):
            if len(value) != 1:
                continue
            unit = next(iter(value.keys()))
            if unit is None:
                continue
        if isinstance(value, int):
            unit = value

        info = stage.handle2info.get(unit)
        if not info:
            continue

        # Decrement reference count
        del info[command]

        # Delete info if reference count has dropped to zero
        if clear and not info:
            del stage.handle2info[unit]


def register_unit(command):
    """
    Find out and register all units assigned to the command.

    Note: this function also has the responsability to check
        that the values it provides to UNITE keywords are valid.
    """
    # Get all UNITE keywords
    visitor = UnitVisitor()
    command.accept(visitor)

    stage = command.stage
    for keyword in visitor.keywords:
        value = keyword.value

        # If the provided value is an *int*
        # The corresponding filename is assumed to be given by the dictionary
        if isinstance(value, int):
            info = stage.handle2info[value]
            val = keyword.cata.definition['inout']
            attr = FileAttr.str2value(val)
            info[command] = attr
            continue

        # Put *None* in the event of an empty or invalid *dict*
        if value is None or len(value) != 1:
            keyword.value = None
            continue

        unit, filename = next(iter(value.items()))

        if unit is None:
            keyword.value = None
            continue

        info = stage.handle2info[unit]
        info.filename = filename if filename else None

        val = keyword.cata.definition['inout']
        attr = FileAttr.str2value(val)

        info[command] = attr
        keyword.value = unit

def used_units(command):
    """
    Used file in commands. Assumes that `register_unit` and they
    are given as integers.
    """
    visitor = UnitVisitor()
    command.accept(visitor)
    return [keyword.value for keyword in visitor.keywords if keyword.value is not None]


def register_deleter(command, just_created):
    """Register existing deleters as parent of *command*.

    Only the deleters that already exist before *command* are considered at
    creation.
    For other modifications add deleters from preceding stages only.

    Arguments:
        command (*Command*): Command in which the parent will be added.
        just_created (bool): If *True*, *command* is just being created.
    """
    deleters = command.preceding_deleters(only_preceding=not just_created)
    register_parent(command, deleters)

def init_deleter(deleter, just_created):
    """A new deleter depends on all commands that already exist in the Stage.
    """
    if not deleter.is_deleter or not just_created:
        return
    register_parent(
        deleter, [cmd for cmd in deleter.stage.commands if not cmd.is_epilogue]
    )

def unregister_deleter(deleter):
    """Unregister commands that are children of a *deleter* command (called
    before the deleter is deleted).

    Arguments:
        deleter (*Command*): The deleter that is unparented.
    """
    from .basic import Command
    if not deleter.is_deleter:
        return

    for cmd in deleter.child_nodes:
        if isinstance(cmd, Command):
            remove_parent(cmd, deleter)
            cmd.reset_validity()

def avail_meshes(storage):
    """Mesh concepts of whom the commands in storage depend."""
    res = _scan_storage_top(storage, avail_meshes_in_cmd, list)

    # eliminate duplicates in list
    return list(set(res))

def _scan_storage(storage, callback, rettype, title=None):
    """
    Helper function that applies callback to Command instances in dict.

    Arguments:
        storage (dict): dict to explore for *Command* values
        callback (func): function to invoke on those commands
        rettype (type): return type, should be *dict* or *list*
        title (str): name of the command corresponding to storage
    """
    # TODO: merge with _walk_storage
    from .basic import Command
    res = rettype()
    res_extend = list.extend if rettype is list \
                             else _no_override_update

    for val in storage.values():
        if isinstance(val, dict):
            res_extend(res, _scan_storage(val, callback, rettype, title))
        elif isinstance(val, (list, tuple)):
            for elem in val:
                if isinstance(elem, dict):
                    res_extend(res, _scan_storage(elem, callback, rettype, title))

                elif isinstance(elem, Command):
                    _helper_process_command(elem, res, callback, res_extend, rettype, title)

        elif isinstance(val, Command):
            _helper_process_command(val, res, callback, res_extend, rettype, title)

    return res

def _helper_process_command(command, res, callback, res_extend, rettype, title):
    """
    Helper to `_scan_storage`, process a command

    Arguments:
        command (Command): command to build output from
        res (dict): result under construction
        callback (func): function to build the result
        res_extend (func): function to extend the result to that already built
        rettype (type): should be dict or list
        title (str): title of the command `_scan_storage` was called with
            in the first place
    """
    from .hidden import Hidden
    if isinstance(command, Hidden):
        command = command.storage_nocopy['PARENT']

    if rettype is dict and title in LEVEL_2_COMMANDS:
        # Make a recursive call to _scan_storage
        #     with storage of the friend command as an argument
        res_extend(res, _scan_storage(command.storage_nocopy, callback, rettype, command.title))

    if command not in _scan_storage.found_cmds:
        _scan_storage.found_cmds.append(command)
        res_extend(res, callback(command))

def _scan_storage_top(storage, callback, rettype, title=None):
    """To distinguish first call to `_scan_storage` to recursive ones"""
    _scan_storage.found_cmds = []
    return _scan_storage(storage, callback, rettype, title)

def _walk_storage(storage, afilter, callback, rettype, curpath):
    """
    Helper function to walk though dictionary of command.

    Arguments:
        afilter (func):  filter on the *Simple* values.
        storage (dict): dict to explore for *Command* values.
        callback (func): function to invoke on those commands.
        rettype (type): return type, should be *dict* or *list*.
        curpath (str): current search path, to build a dict key.
    """
    res = rettype()
    res_extend = list.extend if rettype is list \
                             else dict.update
    for key, val in storage.items():
        if isinstance(val, dict):
            res_extend(res, _walk_storage(val,
                                          afilter, callback,
                                          rettype,
                                          curpath + [key]))
        elif isinstance(val, (list, tuple)):
            for i, elem in enumerate(val):
                if isinstance(elem, dict):
                    res_extend(res, _walk_storage(elem,
                                                  afilter, callback,
                                                  rettype,
                                                  curpath + [key, str(i)]))
                elif afilter(key, elem, curpath + [key]):
                    # GROUP_MA and GROUP_NO are taken
                    # They should be hidden later on if necessary
                    res_extend(res, callback(val,
                                             curpath + [key],
                                             storage))
                    break
        elif afilter(key, val, curpath + [key]):
            res_extend(res, callback([val], curpath + [key], storage))
    return res

def avail_groups_in_storage(storage, title):
    """
    Same than `avail_groups_in_cmd` but acts on the storage
        dictionary. Allows to work on content not yet commited.

    Arguments:
        storage (dict): content of the dictionnary.
        title (str): name of corresponding command.
    """

    def _register_group(val, curpath, fstorage):
        key = '.'.join(curpath)
        grtype = MeshGroupType.GElement if expects_grma(curpath)\
                                        else MeshGroupType.GNode
        ppath = curpath[:-1]
        return {key: (grtype,
                      list(val),
                      get_related(ppath, fstorage))}

    return _walk_storage(storage,
                         lambda x, y, curpath: filter_groups(curpath),  # pragma pylint: disable=unused-argument
                         _register_group,
                         dict,
                         ['', title])

def _no_override_update(dict1, dict2):
    """
    Similar to `dict.update` but seeks common keys before.
    If found, add an occurence number to the key before to do
    the update, so that both occurences are kept.

    Arguments:
        dict1 (dict): first dict, modified in place.
        dict2 (dict): second dict, whose entries will be added to dict1.
    """
    # keys w/o the command occurence number
    keys_no_occ = []
    for k in dict1.keys():
        path = k.split('.')
        if path[2].isdigit():
            path.pop(2)
        keys_no_occ.append('.'.join(path))

    # search and distinguish common keys accordingly
    kset = set(keys_no_occ).intersection(dict2.keys())
    for k in kset:
        occ_nb = keys_no_occ.count(k)
        #
        if k in dict1:
            path = k.split('.')
            path.insert(2, str(0))
            key1 = '.'.join(path)
            dict1[key1] = dict1.pop(k)
        #
        path = k.split('.')
        path.insert(2, str(occ_nb))
        key2 = '.'.join(path)
        dict1[key2] = dict2.pop(k)

    # remaining update
    return dict1.update(dict2)

def avail_meshes_in_cmd(command):
    """Mesh concepts of whom the command depends."""
    from .basic import Command
    res = []
    # `command` may be None if the user did not specify any command
    if command is None:
        return res
    typ = command.gettype(ConversionLevel.NoFail)
    if typ is CATA.package("DataStructure").maillage_sdaster:
        res.append(command)
    parents = [cmd for cmd in command.parent_nodes \
                           if isinstance(cmd, Command)]
    for par in parents:
        res += avail_meshes_in_cmd(par)

    # eliminate duplicates in list
    return list(set(res))

def avail_groups_in_cmd(command):
    """Returns {path: groupname} list of all groups in Command."""
    visitor = GroupFilterVisitor(lambda x: True)
    command.accept(visitor)
    return visitor.group_dict

def paths_using_group(command, group):
    """Returns [path1, ...] list of all paths in Command using group."""
    visitor = GroupNameFilterVisitor(lambda x: True, group)
    command.accept(visitor)
    return visitor.path_list

def avail_groups(storage, title):
    """Applies `avail_groups_in_cmd` to all Commands in storage."""
    res = _scan_storage_top(storage, avail_groups_in_cmd, dict, title)
    _no_override_update(res, avail_groups_in_storage(storage, title))
    return res

def tout_usage_in_cmd(command):
    """Usage of TOUT='OUI' in command."""
    return tout_usage_in_storage(command.storage_nocopy, command.title)

def tout_usage_in_storage(storage, title):
    """Usage of TOUT='OUI' in not yet commited storage."""

    def _register_tout(_, curpath, fstorage):
        key = '.'.join(curpath)
        ppath = curpath[:-1]
        return {key: get_related(ppath, fstorage)}

    return _walk_storage(storage,
                         lambda key, x, y: filter_tout(key), # pragma pylint: disable=unused-argument
                         _register_tout,
                         dict,
                         ['', title])


def tout_usage(storage, title):
    """Applies `tout_usage_in_cmd` to all commands in storage."""
    res = _scan_storage_top(storage, tout_usage_in_cmd, dict, title)
    _no_override_update(res, tout_usage_in_storage(storage, title))
    return res
