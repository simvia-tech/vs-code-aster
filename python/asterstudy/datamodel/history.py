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
History
-------

Implementation of the history (collection of cases).

"""

import os.path as osp

from ..common import (AsterStudyError, AsterStudyInterrupt, CatalogError,
                      Features, debug_message, no_new_attributes, translate)
from .abstract_data_model import AbstractDataModel
from .case import Case
from .catalogs import CATA
from .engine.engine_utils import add_stages_from_astk
from .recovery import recover_from_ajs
from .result import HistoryMixing as RHistoryMixing
from .serializer import STRICT_DEFAULT
from .serializer import factory as serializer_factory


class History(AbstractDataModel, RHistoryMixing):
    """History: a collection of study Cases.

    There is always a single *current* Case - the only one which is
    modifiable: see `current_case` property.

    Read-only Cases can be accessed via `run_cases` property.
    """
    __version = None

    __version_number = _autocopy_enabled = _hid = _features = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, version=None):
        """
        Create History.

        Attributes:
            version (Optional[str]): Version of code_aster to use.
                Defaults to *None*; in this case default version is
                used.
        """
        super().__init__()
        RHistoryMixing.__init__(self)
        self._hid = id(self)
        self.create_case("CurrentCase")
        if version is not None:
            if History.__version and History.__version != version:
                raise CatalogError(
                    "Another History object is currently using version '{0}', "
                    "not '{1}'. Only one catalog can be used at a time.".
                    format(History.__version, version))
            CATA.read_catalogs(version)
        History.__version = CATA.version
        self.__version_number = CATA.version_number
        self._autocopy_enabled = False
        self._features = Features(self.__version_number)

    def __getstate__(self):
        """Be care to the version attribute during pickling."""
        state = self.__dict__
        state['History.__version'] = History.__version
        return state

    def __setstate__(self, state):
        """Be care to the version attribute during unpickling."""
        History.__version = state.pop('History.__version')
        self.__dict__.update(state)

    @classmethod
    def reset_catalog(cls):
        """Reset the attached catalog.

        Must be called with care because all existing History instances will
        become invalid if a different catalog is read (the code_aster package
        will change).
        """
        cls.__version = None

    @property
    def support(self):
        """Attribute that holds the 'support' property.

        Returns:
            Feature: Object that holds the supported feature.
        """
        return self._features

    @property
    def nodes(self):
        """list[int]: Attribute that provides access to uids of all
        stored nodes."""
        return sorted(self._nodes.keys())

    @property
    def version(self):
        """str: Attribute that holds code_aster version associated with
        this History object."""
        return History.__version

    @property
    def version_number(self):
        """str: Attribute that holds code_aster version number associated with
        this History object."""
        return self.__version_number

    @property
    def tests_path(self):
        """str: Attribute that holds path of the testcases."""
        return CATA.data_path(History.__version, "tests")

    @property
    def extern_data_path(self):
        """str: Attribute that holds path of the external data."""
        return CATA.data_path(History.__version, "datg")

    @property
    def nb_cases(self):
        """int: Attribute that holds number of Cases."""
        return len(self._cases)

    def create_case(self, name=None, replace=False):
        """
        Create a new Case in the history.

        Attributes:
            name (Optional[str]): Name of Case being created. Default to
                *None* (in this case name is auto-assigned to Case).
            replace (Optional[bool]): Specifies if *current* Case should
                be replaced (*True*) or kept (*False*). Defaults to
                *False*.

        Returns:
            Case: New Case.

        Note:
            New Case becomes a *current* one; previous *current* Case is
            added to the list of *run* Cases (if `replace` is *False*) or
            replaced by new one (if `replace` is *True*).
        """
        if replace:
            name = "CurrentCase"
        elif not name or name in [node.name for node in self.cases]:
            name = self.new_case_name(name)

        case = Case(name)
        self.insert_case(case, replace)
        return case

    def add_case(self, case):
        """
        Add Case.

        This function is only used if Case is created outside of the
        `History`.

        Attributes:
            case (Case): Case being added.

        Note:
            - Case is not added if it is already present in the history.
            - Case being added becomes a *current* one; previous
              *current* Case is added to the list of *run* Cases.
        """
        self.insert_case(case)

    def insert_case(self, case, replace=False, index=None):
        """
        Inserts Case into the given position in the list of Cases.

        Attributes:
            case (Case): Case being inserted.
            replace (Optional[bool]): Specifies if existing Case at
                given position should be kept (*False*) or replaced by
                new one (*True*). Defaults to *False*.
            index (int): Position in the cases list. Defaults to *None*
                that means last position in the list (i.e. "current"
                Case).
        """
        if case not in self.cases:
            self.add(case, None)
            if self.cases and replace:
                old_case = self._cases.pop(index if index is not None else -1)
                old_case.delete()
            idx = index if index is not None else len(self._cases)
            self._cases[idx:idx] = [case]

    def import_case(self, filename, replace=False, force_text=False):
        """
        Create a new Case in the history by importing an export file from ASTK.

        Attributes:
            filename (str): Filename of the export file to import.
            replace (Optional[bool]): Specifies if *current* Case should
                be replaced (*True*) or kept (*False*). Defaults to
                *False*.
            force_text (Optional[bool]): Keep stages in text mode.

        Returns:
            Case: New Case.

        Note:
            New Case becomes a *current* one; previous *current* Case is
            added to the list of *run* Cases (if `replace` is *False*) or
            replaced by new one (if `replace` is *True*).
        """
        case = self.create_case(replace=replace)
        if osp.splitext(filename)[-1] != ".ajs":
            add_stages_from_astk(case, filename, force_text=force_text)
        else:
            # parameters are not recovered
            recover_from_ajs(case, filename)
        return case

    def remove_node(self, node):
        """
        Execute a common code for removing the node from the model.

        Arguments:
            node (Node): Node being removed.

        Note:
            Removes child nodes according to node's type.
        """
        super().remove_node(node)
        if node in self._cases:
            self._cases.remove(node)

            # is there any stage that uses a remote database?
            if True not in [rc.has_remote for rc in self.run_cases]:
                # no, 'remote_folder' may be change
                self._remote_folder_base = None  # pylint: disable=no-member

    def check_dir(self, task):
        """
        Check study directory after a load.

        Arguments:
            task (func): the checking operation to perform, among:
                `RHistoryMixing.warn`,
                `RHistoryMixing.full_warn`,
                `RHistoryMixing.clean`
        """
        import traceback
        try:
            task(self)
        except AsterStudyError:
            raise
        except Exception as err:  # pragma: no cover
            debug_message("check_dir error:", traceback.format_exc())
            trbk = "Error: {0}\n\n{1}".format(err, traceback.format_exc())
            raise AsterStudyInterrupt(
                translate(
                    "AsterStudy", "Errors occurred during checking the "
                    "study directory"), str(trbk)) from err

    def __call__(self, uid):
        """
        Support native Python '()' operator protocol.

        Arguments:
            uid (int): Node's uid.

        Returns:
            Node: Data model node.

        Raises:
            KeyError: If `uid` is invalid.
        """
        return self._nodes[uid]

    def __getitem__(self, given):
        """
        Support native Python '[]' operator protocol.
        """
        cases = self._cases

        if isinstance(given, int):
            return cases[given]

        return next(item for item in cases if item.name == given)

    def __eq__(self, other):
        """Support native Python '==' operator protocol."""
        return self is other

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        lcases = self.cases
        rcases = other.cases
        assert len(lcases) == len(rcases)

        for idx, lcase in enumerate(lcases):
            rcase = rcases[idx]
            assert lcase * rcase is None

        RHistoryMixing.__mul__(self, other)

    @staticmethod
    def save(model, file_name, serializer=None):
        """
        Save model to a file.

        If `serializer` is not given, a default one is used.

        Arguments:
            model (AbstractDataModel): Model object.
            file_name (str): Path to the file.
            serializer (Optinal[any]): Serializer object.
                Defaults to *None*.
        """
        serializer = serializer_factory(file_name, serializer)
        AbstractDataModel.save(model, file_name, serializer)

    @classmethod
    def load(cls, file_name, serializer=None, strict=STRICT_DEFAULT, **kwargs):
        """
        Load model from a file.

        If `serializer` is not given, a default one is used.

        Arguments:
            file_name (str): Path to Asterstudy persistence file.
            serializer (Optinal[any]): Serializer object.
                Defaults to *None*.
            kwargs (Optional): Keywords arguments passed to the serializer.

        Returns:
            AbstractDataModel: Model object.
        """
        # pragma pylint: disable=arguments-differ
        serializer = serializer_factory(file_name, serializer, strict)
        return AbstractDataModel.load(file_name,
                                      serializer,
                                      class_=cls,
                                      **kwargs)

    @property
    def autocopy_enabled(self):
        """Is auto copy enabled?"""
        return self._autocopy_enabled

    @autocopy_enabled.setter
    def autocopy_enabled(self, value):
        """Set automatic copy mode."""
        self._autocopy_enabled = value

    def reset_current_embedded(self):
        """
        Reset path for the embedded files of the current case.

        Useful at load time.
        """
        # pragma pylint: disable=not-an-iterable
        for stage in self.current_case:
            for info in stage.handle2info.values():
                if info.embedded:
                    bname = osp.basename(info.filename)
                    info.filename = osp.join(self.tmpdir, bname)

    def new_case_name(self, root):
        """Returns an inexisting name for a case.

        Arguments:
            root (str): Root for the new case. If *None*, "Case" is used.

        Returns:
            str: Name based on *root* that doesn't yet exist in children.
        """
        return self.new_name(root or "Case", self.cases)
