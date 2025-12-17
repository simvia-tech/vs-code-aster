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
Undo/redo
---------

Implementation of the undo-redo mechanism.

"""


import pickle
from ..common import debug_message

__all__ = ["UndoRedo", "TransactionUndoRedo"]


def deepcopy(src):
    """
    Make deep copy of source object.

    Arguments:
        any: Source object.

    Returns:
        any: A copy of source object.
    """
    return pickle.loads(pickle.dumps(src))


class UndoRedoItem:
    """An item in the undo/redo history."""

    def __init__(self):
        """Constructor."""
        self.state = {}
        self.ident = -1
        self.message = ''


class UndoRedo:
    """
    Undo-redo manager.

    `UndoRedo` class stores different states of the data model in a
    list.

    Current state of data model is defined by the pointer (index in a
    list of states).

    Method `commit()` pushes current state of the data model to the end
    of queue and moves the pointer; this also clears redo history.

    Methods `undo()` and `redo()` browse the history of the data model
    by moving the pointer in a queue. This cancels all changes made in
    the data model since last `commit()`.

    Method `revert()` reverts data model to last committed state, thus
    reverting all changes made in the data model.
    """

    def __init__(self, model, undo_limit=-1, disable_cbck=None):
        """
        Create UndoRedo object.

        Arguments:
            model (AbstractDataModel): Data model to manage.
            undo_limit (Optional[int]): Length of undo history. Defaults
                to -1 (no limit).
            disable_cbck (func): Callback that tells if the feature is
                disabled.

        See also:
            `undo_limit` attribute
        """
        self._model = model
        self._undo_limit = undo_limit
        self._items = []
        self._id = 0
        self._next_id = 0
        self._index = 0
        item = UndoRedoItem()
        item.ident = self._id
        item.state = deepcopy(self._model)
        debug_message("UNDO init with", self._index, id(item.state))
        self._items.append(item)
        self._disable_cbck = disable_cbck

    @property
    def model(self):
        """
        AbstractDataModel: Attribute that holds model being managed.
        """
        return self._model

    @property
    def last(self):
        """
        Get latest committed state of the model.

        This method is useful in such operations as 'save' since
        currently stored model state may be modified by some operation
        and not committed yet.
        """
        if self.disabled:
            return self.model
        debug_message("UNDO last is", self._index,
                      id(self._items[self._index].state))
        return self._items[self._index].state

    @property
    def undo_limit(self):
        """
        int: Attribute that holds current undo limit.

        Undo limit specifies the maximum number of stored back-up copies
        of the model. Setting undo limit to zero means no undo-redo
        capability. Negative value means unlimited undo-redo history.

        By default, undo limit is set to -1 (i.e. no limit).

        See also:
            `undo()`, `redo()`
        """
        return self._undo_limit

    @undo_limit.setter
    def undo_limit(self, limit):
        """Set undo limit."""
        self._undo_limit = max(-1, limit)
        if self._undo_limit >= 0 and self._undo_limit < len(self._items) - 1:
            new_len = self._undo_limit + 1
            old_len = len(self._items)
            upper = min(self._index + new_len, old_len)
            lower = max(0, upper - new_len)
            self._items = self._items[lower:upper]
            self._index = self._index - lower
            debug_message("UNDO undo_limit reached")

    @property
    def nb_undo(self):
        """
        int: Attribute that holds number of available undo actions.

        See also:
            `nb_redo`, `undo_messages` attributes; `undo()`
        """
        return self._index

    @property
    def nb_redo(self):
        """
        int: Attribute that holds number of available redo actions.

        See also:
            `nb_undo`, `redo_messages` attributes; `redo()`
        """
        return len(self._items) - (self._index + 1)

    @property
    def undo_messages(self):
        """
        list[str]: Attribute that holds available undo actions.

        Note:
            More recent operations come first.

        See also:
            `redo_messages`, `nb_undo` attributes; `undo()`
        """
        messages = [item.message for item in self._items[1:self._index + 1]]
        messages.reverse()
        return messages

    @property
    def redo_messages(self):
        """
        list[str]: Attribute that holds available redo actions.

        Note:
            More recently undone operations come first.

        See also:
            `undo_messages`, `nb_redo` attributes; `redo()`
        """
        return [item.message for item in self._items[self._index + 1:]]

    @property
    def current_state(self):
        """
        int: Attribute that holds current model state's identifier.
        """
        return self._id

    def commit(self, message=''):
        """
        Commit data model changes; return model state identifier.

        Pushes data model state to the end of the history and moves the
        pointer; clears redo history.

        Arguments:
            message (Optional[str]): Name of operation. Default to empty
                string.

        Returns:
            int: New model state's identifier.

        See also:
            `current_state` attribute; `revert()`, `undo()`, `redo()`
        """
        if self.disabled:
            return self._always_change()
        self._next_id = self._next_id + 1
        self._id = self._next_id
        item = UndoRedoItem()
        item.ident = self._id
        item.message = message
        item.state = deepcopy(self._model)
        self._items = self._items[:self._index + 1]
        if self._undo_limit >= 0 and len(self._items) - 1 == self._undo_limit:
            self._items.pop(0)
        else:
            self._index = self._index + 1
        self._items.append(item)
        debug_message("UNDO commit", self._index, id(item.state))
        debug_message(caller=True, limit=5)
        return self._id

    def undo(self, nb_undo=1):
        """
        Undo last action(s); return model state identifer.

        Arguments:
            nb_undo (Optional[int]): Number of actions to undo.
                Defaults to 1.

        Returns:
            int: Model state's identifier.

        See also:
            `redo()`; `current_state` attribute
        """
        if self.disabled:
            return self._always_change()
        self._move(-nb_undo)
        return self._id

    def redo(self, nb_redo=1):
        """
        Redo last undone action(s); return model state identifer.

        Arguments:
            nb_redo (Optional[int]): Number of actions to redo.
                Defaults to 1.

        Returns:
            int: Model state's identifier.

        See also:
            `undo()`; `current_state` attribute
        """
        if self.disabled:
            return self._always_change()
        self._move(nb_redo)
        return self._id

    def revert(self):
        """
        Revert data model to the last stored state; return model state
        identifer.

        This method can be used to revert currently made changes.

        Returns:
            int: Model state's identifier.

        See also:
            `commit()`; `current_state` attribute
        """
        if self.disabled:
            return self._always_change()
        self._model = deepcopy(self._items[self._index].state)

        return self._id

    def _move(self, delta):
        """
        Move internal index in the states history.

        Arguments:
            delta (int): Number of steps (negative for undo, positive
                for redo).
        """
        if self.disabled:
            self._always_change()
            return
        prev_index = self._index
        self._index = max(0, min(self._index + delta, len(self._items) - 1))
        if self._index != prev_index:
            debug_message("UNDO move at", self._index,
                          id(self._items[self._index].state))
            self._model = deepcopy(self._items[self._index].state)
            self._id = self._items[self._index].ident

    def _always_change(self):
        """Ensure the current state is changing"""
        self._id += 1
        return self._id

    @property
    def disabled(self):
        """Tell if the feature is disabled."""
        return self._disable_cbck is not None and self._disable_cbck()


class TransactionUndoRedo:
    """
    Undo-redo manager, based on mechanism of transactions.

    `TransactionUndoRedo` class manages different states of the data
    model.

    Any modification of the data model should be made within the
    transaction. New transaction is initialized by `open()` method.
    Then call `commit()` to apply changes and record new state of
    data model or `abort()` to reject changes and revert to last
    stored state.

    Methods `undo()` and `redo()` browse the history of the data model.

    For proper usage of the transaction mechanism within the application
    it is necessary to ensure that no any change to the data model is
    made without opening a transaction. In other words, if there is no
    open transaction, any change should raise an exception.
    """

    def __init__(self, model, undo_limit=-1):
        """
        Create TransactionUndoRedo object.

        Arguments:
            model (AbstractDataModel): Data model to manage.
            undo_limit (Optional[int]): Length of undo history. Defaults
                to -1 (no limit).

        See also:
            `undo_limit` attribute.
        """
        self._model = model
        self._undo_limit = undo_limit
        self._backup = None
        self._undo = []
        self._redo = []
        self._id = 0
        self._next_id = 0

    @property
    def model(self):
        """
        AbstractDataModel: Attribute that holds model being managed.
        """
        return self._model

    @property
    def undo_limit(self):
        """
        int: Attribute that holds current undo limit.

        Undo limit specifies the maximum number of stored back-up copies
        of the model. Setting undo limit to zero means no undo-redo
        capability. Negative value means unlimited undo-redo history.

        By default, undo limit is set to -1 (i.e. no limit).

        See also:
            `undo()`, `redo()`
        """
        return self._undo_limit

    @undo_limit.setter
    def undo_limit(self, limit):
        """Set undo limit."""
        self._undo_limit = max(-1, limit)
        if self._undo_limit >= 0:
            lower = max(0, len(self._undo) - self._undo_limit)
            self._undo = self._undo[lower:]

    @property
    def nb_undo(self):
        """
        int: Attribute that holds number of available undo actions.

        See also:
            `nb_redo`, `undo_messages` attributes; `undo()`
        """
        return len(self._undo)

    @property
    def nb_redo(self):
        """
        int: Attribute that holds number of available redo actions.

        See also:
            `nb_undo`, `redo_messages` attributes; `redo()`
        """
        return len(self._redo)

    @property
    def undo_messages(self):
        """
        list[str]: Attribute that holds available undo actions.

        Note:
            More recent operations come first.

        See also:
            `redo_messages`, `nb_undo` attributes; `undo()`
        """
        messages = [item.message for item in self._undo]
        messages.reverse()
        return messages

    @property
    def redo_messages(self):
        """
        list[str]: Attribute that holds available redo actions.

        Note:
            More recently undone operations come first.

        See also:
            `undo_messages`, `nb_redo` attributes; `redo()`
        """
        messages = [item.message for item in self._redo]
        messages.reverse()
        return messages

    @property
    def current_state(self):
        """
        int: Attribute that holds current model state's identifier.
        """
        return self._id

    def open(self, message=""):
        """
        Open transaction.

        Arguments:
            message (Optional[str]): Name of operation. Default to empty
                string.

        Raises:
            RuntimeError: If there is already open transaction.

        See also:
            `commit()`, `abort()`; `opened` attribute
        """
        if self.opened:
            raise RuntimeError("There is already open transaction.")
        self._backup = UndoRedoItem()
        self._backup.ident = self._id
        self._backup.message = message
        self._backup.state = deepcopy(self._model)

    @property
    def opened(self):
        """
        bool: Attribute which is *True* when there is open transaction.

        See also:
            `open()`, `commit()`, `abort()`
        """
        return self._backup is not None

    def commit(self):
        """
        Commit transaction; return model state identifier.

        Pushes previous model state to the end of the history;
        clears redo history.

        Returns:
            int: New model state's identifier.

        Raises:
            RuntimeError: If there is no open transaction.

        See also:
            `abort()`, `open()`; `opened` attribute
        """
        if not self.opened:
            raise RuntimeError("There is no open transaction.")
        self._redo = []
        self._undo.append(self._backup)
        if self._undo_limit >= 0:
            lower = max(0, len(self._undo) - self._undo_limit)
            self._undo = self._undo[lower:]
        self._backup = None
        self._next_id = self._next_id + 1
        self._id = self._next_id
        return self._id

    def abort(self):
        """
        Abort transaction; return model state identifier.

        Returns:
            int: Model state's identifier.

        Raises:
            RuntimeError: If there is no open transaction.

        See also:
            `commit()`, `open()`; `opened` attribute
        """
        if not self.opened:
            raise RuntimeError("There is no open transaction.")
        self._model = deepcopy(self._backup.state)
        self._backup = None
        return self._id

    def undo(self, nb_undo=1):
        """
        Undo last action(s); return model state identifer.

        Arguments:
            nb_undo (Optional[int]): Number of actions to undo.
                Defaults to 1.

        Returns:
            int: Model state's identifier.

        Raises:
            RuntimeError: If there is open transaction.

        See also:
            `redo()`; `current_state` attribute
        """
        if self.opened:
            raise RuntimeError("There is already open transaction.")
        if self._undo:
            redo_item = UndoRedoItem()
            redo_item.ident = self._id
            redo_item.message = self._undo[-1].message
            redo_item.state = deepcopy(self._model)
            self._redo.append(redo_item)
            undo_item = self._undo.pop()
            nb_undo = nb_undo - 1
            while nb_undo and self._undo:
                undo_item.message = self._undo[-1].message
                self._redo.append(undo_item)
                undo_item = self._undo.pop()
                nb_undo = nb_undo - 1
            self._model = deepcopy(undo_item.state)
            self._id = undo_item.ident
        return self._id

    def redo(self, nb_redo=1):
        """
        Redo last undone action(s); return model state identifer.

        Arguments:
            nb_redo (Optional[int]): Number of actions to redo.
                Defaults to 1.

        Returns:
            int: Model state's identifier.

        Raises:
            RuntimeError: If there is open transaction.

        See also:
            `undo()`; `current_state` attribute
        """
        if self.opened:
            raise RuntimeError("There is already open transaction.")
        if self._redo:
            redo_item = self._redo.pop()
            if self._undo_limit < 0 or len(self._undo) < self._undo_limit:
                undo_item = UndoRedoItem()
                undo_item.ident = self._id
                undo_item.message = redo_item.message
                undo_item.state = deepcopy(self._model)
                self._undo.append(undo_item)
            nb_redo = nb_redo - 1
            while nb_redo and self._redo:
                redo_item.message = self._redo[-1].message
                self._undo.append(redo_item)
                redo_item = self._redo.pop()
                nb_redo = nb_redo - 1
            self._model = deepcopy(redo_item.state)
            self._id = redo_item.ident
        return self._id
