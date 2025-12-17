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
Comment
-------

Implementation of the Comment as a specfic Command sub class.

"""

# sometimes occurs, probably because of recursive imports
# pylint: disable=no-name-in-module

from ..abstract_data_model import Node
from ..catalogs import CATA
from .. import general
from ... import common

class TextMixing(Node):
    """Mixing class to handle command like a text"""

    __setattr__ = common.no_new_attributes(object.__setattr__)

    class StageProxy:
        "Simulates subset of study2comm 'Stage' API"
        _engine = _concept = _instance = None
        __setattr__ = common.no_new_attributes(object.__setattr__)

        def __init__(self, concept):
            """Constructor"""
            self._instance = None
            self._concept = concept
            self._engine = concept.stage

        def unregister(self):
            """Unregister 'comm2study' resulting command"""
            if self._instance and self._instance.model:
                self._instance.delete()

        def add_command(self, ctype, name):
            """Register 'comm2study' resulting command"""
            from .basic import Command
            cata = CATA.get_catalog(ctype)
            checker = CATA.package('SyntaxChecker').checkCommandSyntax
            concept = Command.factory(name, ctype, cata, checker)
            self._engine.model.add(concept, self._engine.dataset)

            assert self._instance is None
            self._instance = concept

            return concept

        def __len__(self):
            """Redirects call to the 'engine' attribute"""
            if self._instance and self._instance.model:
                return len(self._engine.commands)

            return self._engine.commands.index(self._concept)

        def is_empty(self):
            """Tell if the *DataSet* is empty (i.e. has no command or no text)."""
            return self._engine.is_empty()

        def __getitem__(self, given):
            """Redirects call to the 'engine' attribute"""
            if given < len(self):
                return self._engine[given]

            raise StopIteration()

        def __delitem__(self, _):
            """Redirects call to the 'engine' attribute"""
            self._instance.delete()

        @property
        def model(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.model

        @property
        def parent_case(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.parent_case

        @property
        def number(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.number

        def reorder(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.reorder()

        def is_graphical_mode(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.is_graphical_mode()

        @property
        def dataset(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.dataset

        @property
        def sorted_commands(self):
            """Redirects call to the 'engine' attribute"""
            return self._engine.sorted_commands

        @property
        def preceding_stages(self):
            """Redirects call to the 'engine' attribute"""
            stages = list(self.parent_case[:self._engine])
            stages.append(self)
            return stages

        def text2instance(self, text, strict):
            "Calculates 'storage' for the given text"
            from ..comm2study import comm2study
            comm2study(text, self, strict)
            return self._instance

        def text2concept(self, text, concept, strict):
            "Updates concept according to the given text"
            instance = self.text2instance(text, strict)
            concept.init(instance.storage, conversion=True)
            concept.title = instance.title
            concept.name = instance.name

    @property
    def stage(self):
        """Returns corresponding parent *Stage* instance"""
        if not self.parent_nodes:
            return None

        stage = None

        for node in self.parent_nodes:
            if not isinstance(node, TextMixing):
                stage = node.stage
                break

        return stage

    @property
    def text(self):
        """Stringifies a command: returns is code_aster syntax"""
        from ..study2comm import ExportToCommVisitor
        support = self.stage and self.stage.model and self.stage.model.support
        export = ExportToCommVisitor(support)

        self.accept(export) # pragma pylint: disable=no-member

        return export.get_text()

    def set_text(self, text, strict=general.ConversionLevel.NoFail):
        """Modifies contents according to the given string"""
        stage = TextMixing.StageProxy(self)
        try:
            stage.text2concept(text, self, strict)
        finally:
            stage.unregister()

    @text.setter
    def text(self, text):
        """Modifies contents according to the given string"""
        self.set_text(text, general.ConversionLevel.Syntaxic)

    def text2instance(self, text, strict=general.ConversionLevel.Syntaxic):
        """Checks whether given string is acceptable"""
        stage = TextMixing.StageProxy(self)
        try:
            return stage.text2instance(text, strict)
        except common.ConversionError:
            pass
        finally:
            stage.unregister()

        return None

    def check_text(self, text, strict=general.ConversionLevel.Syntaxic):
        """Checks whether given string is acceptable"""
        instance = self.text2instance(text, strict)
        if not instance:
            return False

        if instance.title != self.title: # pragma pylint: disable=no-member
            return False

        return  True
