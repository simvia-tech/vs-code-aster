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
Command Mixings
---------------

Implementation of Mixing classes used for Command definition.

"""


import copy
import inspect

from ...common import CachedValues, no_new_attributes
from ..general import CataMixing
from ..aster_syntax import IDS, get_cata_typeid
from ..catalogs import CATA
from .helper import unregister_parent, register_parent, register_cos
from .helper import unregister_unit, register_unit
from .constancy import ModifiesCommandInstance as ModifiesInstance


def _type_check(astype, value):
    from .basic import Command

    if type(value) is not Command: # pragma pylint: disable=unidiomatic-typecheck
        return

    value_type = value.gettype()

    if isinstance(astype, (list, tuple)):
        for subtype in astype:
            try:
                _type_check(subtype, value)
                return
            except: # pragma pylint: disable=bare-except
                pass
    elif inspect.isclass(astype):
        if issubclass(value_type, astype):
            return

    message = "Expected (%s) and value (%s) types are incompatible"
    raise TypeError(message % (astype, value_type))


def _update_value(command, astype, name2value, name, value):
    """Assign the value of a keyword into the storage dict of a command."""
    _type_check(astype, value)

    if name in name2value:
        unregister_parent(command, name2value[name])

    name2value[name] = value

    register_parent(command, value)


class StorageMixing:
    """Mixing class to share *storage* and *command* instances"""

    _storage = _engine = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, storage, engine):
        self._storage = storage
        self._engine = engine


class CompositeMixing:
    """Mixing class to refer to a keywords related description"""

    _keywords = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, keywords):
        self._keywords = keywords

_CONTEXT_CACHE = CachedValues()

class KeysMixing(CataMixing, CompositeMixing, StorageMixing):
    """Mixing class that provides access to its elements as Python *dict*"""

    def __init__(self, cata, keywords, storage, engine):
        StorageMixing.__init__(self, storage, engine)
        CompositeMixing.__init__(self, keywords)
        CataMixing.__init__(self, cata)

    @staticmethod
    def _rkeys(keywords, rkeys):
        for key, item in keywords.items():
            if get_cata_typeid(item) < 0:
                continue

            if get_cata_typeid(item) != IDS.bloc:
                rkeys.append(key)
                continue

            definition = item.entities
            KeysMixing._rkeys(definition, rkeys)

    def rkeys(self):
        """Returns definition *keys* in the composite structure"""
        rkeys = []
        KeysMixing._rkeys(self._keywords, rkeys)
        return rkeys

    def keys(self):
        """Returns actual *keys* in the composite structure"""
        return self._storage.keys() if self._storage else []

    def undefined(self):
        """Return *True* if there is no keywords, *False* otherwise."""
        # TODO: After _getitem, _storage is never None.
        # It may be a problem for empty factor keywords.
        return self._storage is None

    @staticmethod
    def _is_dict_stored(storage, name, keywords):
        if keywords.get('max', 1) == 1:
            return True

        return name in storage and isinstance(storage[name], dict)
    calling_key = None
    __setattr__ = no_new_attributes(object.__setattr__)

    @staticmethod
    def is_item_enabled(item, storage):
        """
        Returns *True* if the specified keyword is enabled
        in current context described by given storage.

        item (Item): Bloc element to test.
        """
        _storage = copy.deepcopy(storage)
        # use evaluation of expressions for user variables
        for key, value in _storage.items():
            if hasattr(value, 'evaluation'):
                _storage[key] = value.evaluation
        return item.isEnabled(_storage)

    @staticmethod
    def _getitem(keywords, name, storage, engine, cond_context):
        # TODO Using `setdefault` initializes Simple to None, Factor to {}
        # and Sequence to []: these values should be considered as 'undefined'.
        # But what about Factor keywords without Simple keyword?
        for key, item in keywords.items():
            typeid = get_cata_typeid(item)

            if typeid < 0:
                continue
            # _debug_getitem(key)

            if key != name and typeid != IDS.bloc:
                continue
            if typeid == IDS.simp:
                if isinstance(storage, dict):
                    storage.setdefault(name, None)
                    return Simple.factory(name, item, storage, engine)
                if isinstance(storage, (list, tuple)):
                    return Simple.factory(name, item, storage[0], engine)

            if typeid == IDS.fact:
                keywords = item.definition
                if KeysMixing._is_dict_stored(storage, name, keywords):
                    _storage = storage.setdefault(name, {})
                    if not isinstance(_storage, dict) and len(_storage) == 1:
                        _storage = _storage[0]
                    return Factor(name, item, keywords, _storage, engine)
                _storage = storage.setdefault(name, [])
                return Sequence(name, item, keywords, _storage, engine)


            if not KeysMixing.is_item_enabled(item, cond_context):
                continue

            try:
                kwargs = item.entities
                return KeysMixing._getitem(kwargs, name, storage, engine,
                                           cond_context)
            except KeyError:
                continue

        raise KeyError("There is no handler for the %s keyword" % name)

    def __getitem__(self, name):
        """Returns composite structure item for the given *key*"""
        cond_context = _CONTEXT_CACHE.get(self)
        if cond_context is None:
            # this makes a deepcopy of the Command._storage
            cond_context = self._engine.storage
            # add default keywords according to other provided keywords
            self._engine.cata.addDefaultKeywords(cond_context)
            # this storage dict will allow to evaluate block conditions in
            # the underlying factor keyword
            # keep "local" (factor) values first
            if isinstance(self, (Factor, Sequence, Item)):
                _storage = cond_context[self.name] # pragma pylint: disable=no-member
                if not isinstance(_storage, dict):
                    idx = 0
                    if isinstance(self, Item):
                        idx = self.idx # pragma pylint: disable=no-member
                    _storage = _storage[idx]
            else:
                _storage = self._storage
            # _debug_getitem(name, self._engine.title, _storage, stop=True)
            cond_context.update(_storage)
            _CONTEXT_CACHE.set(self, cond_context)
        return KeysMixing._getitem(self._keywords, name, self._storage,
                                   self._engine, cond_context)

    @staticmethod
    def _gettype(keywords, name):
        """Returns code_aster type for the given argument name"""
        for key, item in keywords.items():
            typeid = get_cata_typeid(item)

            if typeid < 0:
                continue

            if key != name and typeid != IDS.bloc:
                continue

            if typeid == IDS.simp:
                return item.definition['typ']

            try:
                kwargs = item.entities
                return KeysMixing._gettype(kwargs, name)
            except KeyError:
                continue

        raise KeyError("There is no handler for the %s keyword" % name)

    def gettype(self, name):
        """Returns code_aster type for the given argument name"""
        return KeysMixing._gettype(self._keywords, name)

    @ModifiesInstance(True)
    def __setitem__(self, name, value):
        self.clear_cache()
        if name not in self.rkeys():
            raise KeyError("There is no item for the given name - '%s'" % name)

        astype = self.gettype(name)

        # declared result of a macro-command
        is_co = CATA.is_co(astype)
        if is_co:
            value = CO(value)

        if isinstance(self._storage, dict):
            _storage = self._storage
        else:
            if not self._storage:
                self._storage.append({})
            _storage = self._storage[0]

        _update_value(self._engine, astype, _storage, name, value)
        self._engine.reset_validity()

        # automatically add a Hidden that creates the CO result
        if not is_co:
            return

        stage = self._engine.stage
        register_cos(stage, self._engine)

    def __delitem__(self, name):
        """Remove an item"""
        if name not in self.keys():
            raise KeyError("There is no value for the given name: '%s'" % name)
        unregister_parent(self._engine, self._storage[name])
        self._engine.reset_validity()
        del self._storage[name]

    def clear_cache(self):
        """Reset cond_context cache."""
        _CONTEXT_CACHE.discard(self)


class NameMixing:
    """Mixing class that represents named objects"""

    _name = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """Attribute that holds unique *name*"""
        return self._name

class ResultMixing:
    """Mixing class that represents result objects"""
    is_co = False

    @classmethod
    def is_typco(cls):
        """Tells if it is an additional result built by a MACRO."""
        return cls.is_co

class CO(NameMixing, ResultMixing):
    """Object to store the declaration of a result of a macro-command that will
    be created *later* by a *Hidden*.

    Args:
        name (str): Name of the result to declare.
    """
    is_co = True
    _type = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name):
        self._type = CATA.baseds
        ResultMixing.__init__(self)
        NameMixing.__init__(self, name)

    def settype(self, astype):
        """Define the type of the result."""
        self._type = astype

    def gettype(self):
        """Return the type of the result."""
        return self._type


class Item(NameMixing, KeysMixing):
    """Represents *Command* argument described as a *Sequence* item"""

    idx = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name, idx, cata, keywords, storage, engine):
        self.idx = idx
        KeysMixing.__init__(self, cata, keywords, storage, engine)
        NameMixing.__init__(self, name)


class Sequence(NameMixing, KeysMixing):
    """Represents *Command* argument described as a *sequence*"""
    # == list of factor keywords
    def __init__(self, name, cata, keywords, storage, engine):
        KeysMixing.__init__(self, cata, keywords, storage, engine)
        NameMixing.__init__(self, name)

    def __iter__(self):
        for idx, item in enumerate(self._storage):
            yield Item(self.name, idx, self._cata, self._keywords, item,
                       self._engine)

    def __len__(self):
        return len(self._storage) if self._storage is not None else 0

    def __getitem__(self, idx):
        return KeysMixing.__getitem__(self, idx)

    def undefined(self):
        """Return *True* if the sequence is empty, *False* otherwise."""
        return len(self) == 0

    def append(self):
        """Appends a new item at the end"""
        item = {}
        self._storage.append(item)
        return Item(self.name, len(self) - 1, self._cata, self._keywords,
                    item, self._engine)

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_sequence(self)


class Simple(NameMixing, CataMixing, StorageMixing):
    """Represents *Command* argument described as a *simple*"""

    calling_key = None
    __setattr__ = no_new_attributes(object.__setattr__)

    @staticmethod
    def factory(name, cata, storage, engine):
        """Create a generic or specific Simple object."""
        if name.startswith('UNITE'):
            return Unit(name, cata, storage, engine)

        return Simple(name, cata, storage, engine)

    def __init__(self, name, cata, storage, engine):
        CataMixing.__init__(self, cata)
        StorageMixing.__init__(self, storage, engine)
        NameMixing.__init__(self, name)

    @property
    def value(self):
        """Returns the value"""
        return self._storage.get(self._name, None)

    def __eq__(self, value):
        """Supports native '==' Python operator protocol"""
        return self._storage[self._name] == value

    def gettype(self):
        """Returns code_aster type for the given argument"""
        return self._cata.definition['typ']

    @value.setter
    @ModifiesInstance(True)
    def value(self, value):
        """Updates the value"""
        if value is None:
            if self._name in self._storage:
                del self._storage[self._name]
            return

        astype = self.gettype()
        _update_value(self._engine, astype, self._storage, self._name, value)
        self._engine.reset_validity()

    def undefined(self):
        """Return *True* if the keyword has no value, *False* otherwise."""
        return self.value is None

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_simple(self)


class Unit(Simple):
    """Represents *Simple* argument that refer to a  *unite* object"""

    @property
    def filename(self):
        """Returns the filename"""
        return self._engine.stage.handle2file(self.value)

    @filename.setter
    def filename(self, value):
        """Updates the value"""
        info = self._engine.stage.handle2info[self.value]
        info.filename = value

    @Simple.value.setter # pragma pylint: disable=no-member
    @ModifiesInstance(True)
    def value(self, value):
        """Updates the value"""
        unregister_unit(self._engine, clear=False)

        Simple.value.fset(self, value) # pragma pylint: disable=no-member

        register_unit(self._engine)


class Factor(NameMixing, KeysMixing):
    """Represents *Command* argument described as a *factor*"""

    calling_key = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name, cata, keywords, storage, engine):
        KeysMixing.__init__(self, cata, keywords, storage, engine)
        NameMixing.__init__(self, name)

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_factor(self)


# def _debug_getitem(keyword, title="", storage=None, \
#                    stop=False):
#     """Debug helper"""
#     print "DEBUG: keyword:", keyword
#     if not stop:
#         return
#     if title and title not in ("MECA_STATIQUE",):
#         return
#     if keyword in ("RENUM",):
#         if storage:
#             print "DEBUG: storage =", storage
#         # now just go upper in the stack
#         import pdb
#         pdb.set_trace()
