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
Basic Command
-------------

Implementation of the basic Command.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import copy

from ...common import mixedcopy, no_new_attributes, recursive_items
from ..abstract_data_model import Node, add_parent, remove_parent
from ..catalogs import CATA, reusable_keywords
from ..general import CataMixing, ConversionLevel
from ..general import CopyContext as Ctx
from ..general import Validity
from ..visit_study import FilterVisitor
from .constancy import ModifiesCommandInstance as ModifiesInstance
from .helper import (clean_undefined, init_deleter, register_cos,
                     register_deleter, register_parent, register_unit,
                     unregister_cos, unregister_deleter, unregister_parent,
                     unregister_unit, update_dependence_up)
from .mixing import CO, KeysMixing, ResultMixing
from .text import TextMixing


class Command(TextMixing, CataMixing, ResultMixing):
    """Implementation of the command"""
    name_length = 8
    subclass_dict_cache = None
    specific_name = None
    is_co = False
    _cache_type = None
    _validity = _check_validity = None
    _engine = _storage = _syntax_checker = _title = _active = None
    _reuse_input_name = None
    ccopy = None
    __setattr__ = no_new_attributes(object.__setattr__)

    @staticmethod
    def factory(name, title, cata, syntax_checker):
        """Create a generic or specific Command object."""
        if not Command.subclass_dict_cache:
            dict_sub = {}
            for cls in Command.__subclasses__(): # pragma pylint: disable=no-member
                if cls.specific_name:
                    dict_sub[cls.specific_name] = cls
            Command.subclass_dict_cache = dict_sub

        cls = Command.subclass_dict_cache.get(title, Command)

        return cls(name, title, cata, syntax_checker)

    def __init__(self, name, title, cata, syntax_checker):
        """Constructor"""
        TextMixing.__init__(self, name)
        CataMixing.__init__(self, cata)
        self._active = True
        self._engine = None
        self._storage = {}
        self.cata = cata
        self._syntax_checker = syntax_checker
        self._title = title
        self.ignore_copy = Command
        self.ignore_parent = Command

        self._validity = Validity.Nothing
        self._check_validity = True
        self.ccopy = None
        self.reset_cache_type()

    def __deepcopy__(self, memodict):
        # pragma pylint: disable=unused-argument
        """Supports native Python 'deepcopy' function protocol"""
        return self

    @property
    def active(self):
        """Attribute that holds 'active' status"""
        return self._active

    @active.setter
    def active(self, value):
        self._active = value

        comment = self.comment
        if comment:
            comment.active = value

        if value:
            register_unit(self)
        else:
            unregister_unit(self)

        from .hidden import Hidden
        for concept in self.child_nodes:
            if isinstance(concept, Hidden):
                concept.active = value

        self.reset_validity()

    @property
    def storage(self):
        """Attribute that holds parameter's internal representation"""
        return copy.deepcopy(self._storage)

    @property
    def storage_nocopy(self):
        """Return the parameter's internal representation (for performance).

        Warning: The caller must ensure that the object won't be changed.
        """
        return self._storage

    @CataMixing.cata.setter # pragma pylint: disable=no-member
    def cata(self, value):
        "Declares setter for so named property"
        keywords = value.definition
        CataMixing.cata.fset(self, value) # pragma pylint: disable=no-member
        self._engine = KeysMixing(value, keywords, self._storage, self)

    def rkeys(self):
        """Returns definition *keys* in the composite structure"""
        return self._engine.rkeys()

    def keys(self):
        """Returns actual *keys* in the composite structure"""
        return self._engine.keys()

    def __getitem__(self, name):
        """Returns composite structure item for the given *key*"""
        # self.reset_validity() has been added by 3c3d87ec4168
        # but __getitem__ is a read-only action because KeysMixing.__getitem__
        # works on a copy of 'storage'.
        return self._engine[name]

    @ModifiesInstance(True)
    def __setitem__(self, name, value):
        """Assigns a value for the given *key*"""
        self.reset_validity()
        self._engine[name] = value

    def gettype(self, strict=ConversionLevel.Type):
        """Returns code_aster type for the given command"""
        if strict & ConversionLevel.Type:
            # use safe function in text mode
            parent_stage = self.stage
            if parent_stage and parent_stage.is_text_mode():
                return self.safe_type()
            return self.unsafe_type()
        return self.safe_type()

    def unsafe_type(self):
        """Calculates code_aster type; raises exception in case of error."""
        if self._cache_type:
            return self._cache_type
        args = mixedcopy(self._storage)
        typ = self.cata.get_type_sd_prod(**args)
        # if the function returns None but it should not, return `baseds`
        if CATA.expects_result(self.cata):
            if not typ or isinstance(None, typ):
                raise TypeError
        self._cache_type = typ
        return typ

    def safe_type(self,):
        """Returns code_aster type for the given command in a safe way"""
        try:
            return self.unsafe_type()
        except: # pragma pylint: disable=bare-except
            # if sd_prod failed or should not return None,
            # returns the first possible type
            return self.type

    def get_possible_types(self):
        """Returns the list of all possible types that a command may create.

        Returns:
            list[DataStructure] or list[list[DataStructure]]: List of possible
            types or a list of list if there are additional results for
            macro-commands.
        """
        if self._model.support["all_types"]:
            return self.cata.get_all_types()
        return [CATA.baseds]

    def submit(self, file_check=False):
        """Submits the command changes into the Study"""
        self.reorder()
        if file_check:
            self.stage.check_reused_out_file_in_cmd(self)
        self.reset_validity()
        self.reset_cache_type()
        self._auto_naming()

    def get_list_co(self):
        """Return the list of *CO* found in a storage dict with their path
        in the storage dict."""
        cos = []
        for key, node in recursive_items(self._storage):
            if isinstance(node, CO):
                cos.append((key, node))
        return cos

    @property
    def list_co(self):
        """Return the list of *CO* passed as argument."""
        return [i[1] for i in self.get_list_co()]

    @property
    def hidden(self):
        """Return the list of produced *Hidden* commands."""
        hidden = []
        from .hidden import Hidden
        for node  in self.child_nodes:
            if isinstance(node, Hidden):
                hidden.append(node)
        return hidden

    def _register_cos(self, pool_co, conversion):
        """
        Properly register all CO command args via producing corresponding
        hiddens
        """
        register_cos(self.stage, self, pool_co, conversion)

    @ModifiesInstance(True)
    def init(self, storage, duplication=False, conversion=False, file_check=False):
        """
        Set command content dictionary to `storage`, discards earlier content

        Initializes its context from an outside dictionary.

        During the duplication process, do not create Hidden objects from CO
        because they will be created by duplication of the previously existing
        ones.

        Arguments:
            storage (dict): dictionnary of command content
            duplication (bool): *True* if this is done in the context
                of a duplication
            conversion (bool): *True* if this is done in the context
                of a comm2study conversion
            file_check (bool): if *True*, an error is raised if the command
                leads to an out file being used for a second time
        """
        pool_co = unregister_cos(self, delete=False)
        unregister_unit(self, clear=False)
        unregister_parent(self, self._storage)

        just_created = len(self._storage) == 0
        self._storage.clear()
        self._engine.clear_cache()

        clean_undefined(storage)
        update_dependence_up(storage)

        self._storage.update(storage)

        register_parent(self, self._storage)
        init_deleter(self, just_created)
        register_deleter(self, just_created)

        # in case of duplication, do not create new COs
        if not duplication:
            self._register_cos(pool_co, conversion)
        for hid in pool_co.values():
            hid.delete()

        if self.active:
            register_unit(self)

        self.submit(file_check)

        if not conversion:
            self.stage.track_unused()

        return self

    def __call__(self, storage):
        """Initializes its context from an outside dictionary"""
        self.init(storage)
        return self

    def __mul__(self, other):
        """Supports native Python '*' operator protocol."""
        assert str(self) == str(other)

    def __eq__(self, other):
        """Supports native Python '==' operator protocol."""
        return self is other

    def __hash__(self):  # pragma pylint: disable=useless-super-delegation
        return super().__hash__()

    def short_repr(self):
        """Returns a short textual representation."""
        return "{0.name} <from {0._title}>".format(self)

    def node_repr(self):
        """Native node representation that shows dependencies."""
        return Node.__repr__(self)

    def __str__(self, rename=False):
        """Stringifies a command: returns is code_aster syntax"""
        from ..study2comm import ExportToCommVisitor
        support = self.model and self.model.support
        export = ExportToCommVisitor(support, rename=rename)

        comment = self.comment # Print corresponding comment first
        if comment is not None:
            comment.accept(export) # pragma pylint: disable=no-member

        self.accept(export)

        return export.get_text()

    def __repr__(self):
        """Raw representation"""
        return self.node_repr()

    def preceding_deleters(self, only_preceding):
        """Collects all the previously existing deleters.

        Arguments:
            only_preceding (bool): If *True* only returns the deleters from the
                preceding stages, not from the current. If *False* all the
                existing deleters are returned.

        Returns:
            list[Command]: List of deleters.
        """
        preceding_commands = self.stage.preceding_commands(self, only_preceding)
        return [cmd for cmd in preceding_commands if cmd.is_deleter]

    @staticmethod
    def filterby(stage, astype, command=None):
        """Collects all commands with given *astype*.

        Commands that returned in the reversed order of *sorted_commands*.
        """
        excommands = reversed(stage.preceding_commands(command))

        filtered = []
        for item in excommands:
            typ = item.gettype(strict=ConversionLevel.NoFail)

            if typ is None:
                continue

            if isinstance(astype, str) and isinstance(typ, str):
                if typ in ['R', 'I'] and astype in ['R', 'I']:
                    filtered.append(item)
                elif typ == astype:
                    filtered.append(item)
            elif (not isinstance(astype, str) and
                  not isinstance(typ, str) and
                  issubclass(typ, astype)):
                filtered.append(item)

        return filtered

    def groupby(self, astype):
        """Collects all commands in the Aster-Study Case with given *astype*"""
        return Command.filterby(self.stage, astype, self)

    @property
    def title(self):
        """Attribute that holds unique *title*"""
        return self._title

    @title.setter
    def title(self, value):
        """Attribute that holds unique *title*"""
        self._title = value

    def need_reuse(self):
        """Tell if the command needs the 'reuse' argument.
        It is required if it the same name of an input keyword is used as the
        result name."""
        for _, node in recursive_items(self._storage):
            if isinstance(node, Command) and node.name == self.name:
                return True
        return False

    def can_reuse(self):
        """Tell if the command can reuse the result name."""
        return self._cata.can_reuse()

    def reused(self, storage=None):
        """Return the object that is reused if any.

        The rules of the catalog should limit the possibility to only
        one object.

        Returns:
            tuple: A tuple containing a boolean telling if the command must
            modify an object or not, and the object that is or can be reused or
            *None* if it isn't found.
        """
        storage = storage or self._storage
        required, keywords = self.reusable_keywords()
        found = None
        for mcs in keywords:
            if '/' not in mcs:
                obj = storage.get(mcs, None)
                if obj is not None:
                    found = obj
            else:
                mcf, mcs = mcs.split('/')
                obj = storage.get(mcf, None)
                if obj is None:
                    continue
                iobj = obj
                if not isinstance(obj, (list, tuple)):
                    iobj = [obj, ]
                for obj in iobj:
                    obj = obj.get(mcs, None)
                    if obj is not None:
                        found = obj
            if found:
                break
        return required, found

    def reusable_keywords(self):
        """Return the list of keywords that can contain the reusable object.

        Returns:
            list[str]: List of keywords. See `reusable_keywords` for details.
        """
        return reusable_keywords(self._cata.definition.get("reentrant", ""))

    @property
    def reuse_input_name(self):
        """Attribute that tells if the user want to name the result as an
        input objects"""
        return self._reuse_input_name

    @reuse_input_name.setter
    def reuse_input_name(self, value):
        """Set value of the property.

        Arguments:
            value (bool): *True* to reuse the name of an input object if found.
        """
        self._reuse_input_name = value

    def keywords_equal_to(self, value):
        """Return the keywords that are equal to *value*."""
        def _predicate(simple):
            return simple.value == value

        visitor = FilterVisitor(_predicate)
        self.accept(visitor)
        return visitor.keywords

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_command(self)

    @ModifiesInstance(True)
    def rename(self, name):
        """Renames the result of the command."""
        self.name = name

    @ModifiesInstance(True)
    def copy(self):
        """Create and return copied Command node."""
        return self._model.copy(self, context=Ctx.UserCopy)

    def initialize_copy(self):
        """Creates a copy with no connections"""
        return Command.factory(self._name, self._title,
                               self._cata, self._syntax_checker)

    def finalize_copy(self, orig, **kwargs):
        """
        Hook: attune data model additionally after a Command
        has been copied. `self` is the copy.

        Updates storage of the newly created Command.

        Arguments:
            orig (Command): Original object.
            context (Ctx): Context of duplication.
        """
        context = kwargs.get('context', Ctx.Nothing)

        # tag copies
        if not context & Ctx.UserCopy:
            orig.ccopy = self

        if orig is not None:
            self.active = orig.active
            self.init(orig.storage, duplication=True)

        # update dependence downwards
        if not context & Ctx.UserCopy:
            from .helper import update_dependence_down
            update_dependence_down(orig, True)
            update_dependence_down(orig, False)

    def autocopy(self):
        """Calls parent stage's autocopy method"""
        self.stage.autocopy()

    @property
    def comment(self):
        "Returns related Comment Command instance"
        from .comment import Comment
        for command in self.parent_nodes:
            if isinstance(command, Comment):
                return command

        return None

    @comment.setter
    def comment(self, content):
        "Adds or updates Comment instance for the given command"
        if content is None:
            return

        comment = self.comment
        if comment is None:
            stage = self.stage
            comment = stage.add_comment(content, concatenate=False)
            add_parent(self, comment)
            comment.reorder()
        else:
            comment.content = content

    def delete(self, user_deletion=False):
        """Delete command from the model.

        Arguments:
            user_deletion (bool): *True* if this is an explicit individual
                command deletion from the user, *False* if this is called
                as a consequence of stage deletion.
        """
        if user_deletion:
            self._decorated_delete()
        else:
            self._undecorated_delete()

    @ModifiesInstance(True)
    def _decorated_delete(self):
        "Decorated delete method, trigger auto copy if necessary"
        Node.delete(self)

    @ModifiesInstance(False)
    def _undecorated_delete(self):
        "Undecorated delete method, never triggers autocopy"
        Node.delete(self)

    def before_remove(self):
        """Prepares to remove the command from the model.

        Removes child hidden commands that have been automatically added.
        """
        unregister_cos(self)
        unregister_deleter(self)

        comment = self.comment
        if comment is not None:
            comment.delete() # pragma pylint: disable=no-member

        unregister_unit(self, clear=self.stage.is_graphical_mode())

        self.stage.on_remove_command(self)

        self.reset_validity()

        self.reset_cache_type()

        return Node.before_remove(self)

    def reset_validity(self):
        """Recursively resets cachable validity flag"""
        for child in self.child_nodes:
            child.reset_validity()

        self._check_validity = True

    def reset_cache_type(self):
        """Recursively resets cachable type flag"""
        for child in self.child_nodes:
            child.reset_cache_type()

        self._cache_type = None

    def check(self, mode=Validity.Complete, safe=True):
        """Checks given validity aspect and returns corresponding status

        Arguments:
            mode (Validity): Defines the level of checking (see
                general.Validity for levels definition).
            safe (bool): If `safe` is False, an error is raised in case of
                Syntaxic error.

        Returns:
            Validity: Status of the validation.
        """
        if not self.active:
            return Validity.Nothing

        check_all = mode == Validity.Complete
        if not self._check_validity and check_all:
            return self._validity

        result = Validity.Nothing

        if mode & (Validity.Naming | Validity.Dependency):
            if not self._check_naming():
                result |= Validity.Naming
            if not self._check_naming_conflicts():
                result |= Validity.Naming

        # all commands are valid in a text stage: no keyword, no dependency
        if not self.stage.is_text_mode():
            if mode & Validity.Dependency:
                result |= self._check_dependencies(mode)

            if mode & Validity.Syntaxic:
                result |= self._check_syntax(safe)

        if check_all:
            self._validity = result
            self._check_validity = False

        return result

    def reorder(self):
        """Check the command position in the dataset."""
        if self.stage.is_graphical_mode():
            self.stage.reorder(self)

    def _auto_naming(self):
        """Automatically set the command result name in case of 'reuse'."""
        required, obj = self.reused()
        if (required or self.reuse_input_name) and obj:
            self.name = obj.name

    def _check_naming(self):
        """Check the validity of the command result name."""
        if self._name == "_":
            return True

        if (
            len(self._name) > self.name_length
            and not self._model.support["full_python"]
        ):  # pragma: no cover
            # used in versions < 15.4
            return False

        # is it a valid python variable?
        try:
            exec(self._name + " = 0") # pragma pylint: disable=exec-used
        except SyntaxError:
            return False

        return True

    def previous_names(self):
        """Returns command names to be considered for naming conflicts"""
        preceding_commands = self.stage.preceding_commands(self)
        names = set(cmd.name for cmd in preceding_commands if cmd != self)
        return names

    def _check_naming_conflicts(self):
        """Check the validity of the command result name relatively to all
        preceding commands of the case (including commands from preceding
        stages)."""
        if self.name == "_" or self.can_reuse():
            return True

        if self.name in self.previous_names():
            return False

        return True

    def _check_dependencies(self, mode):
        """Checks dependencies."""
        result = Validity.Nothing

        deleters = self.preceding_deleters(False)

        for parent in self.parent_nodes:
            if result & Validity.Dependency:
                break
            if parent not in self._model:
                result |= Validity.Dependency
            elif isinstance(parent, Command):
                if parent.active:
                    # do not propagate Naming conflict to children
                    # else all the model must be rechecked to fix it
                    result |= parent.check(mode) & ~Validity.Naming
                    # parent previously deleted?
                    if self.is_deleter:
                        # deleters depend on all previous commands, so a parent
                        # may have been deleted by a previous deleter
                        continue
                    for rmcmd in deleters:
                        if parent in rmcmd.deletes():
                            result |= Validity.Dependency
                else:
                    result |= Validity.Dependency

        return result

    def _check_syntax(self, safe):
        """Checks syntax of the command."""
        result = Validity.Nothing
        # copy may be done by checker but this also evaluates variables
        args = mixedcopy(self._storage)
        if not safe:
            self._syntax_checker(self._cata, args)
            return result

        try:
            self._syntax_checker(self._cata, args)
        except Exception: # pragma pylint: disable=broad-except
            result |= Validity.Syntaxic

        return result

    def repair(self, previous_commands):
        """Try to repair the stage in case of dependency error.

        - Search for broken dependencies: commands that are not in the model.

        - Try to fix these broken dependencies by using results with the same
          name and type.

        Returns:
            bool: True if a replacement has be done (but that does not ensure
                that the Case is valid).
        """
        def _search_compatible_commands(lost):
            for command in previous_commands:
                if command.name != lost.name:
                    continue
                if command.gettype() == lost.gettype():
                    return command
            return None

        valid = self.check(mode=Validity.Dependency)
        if valid & Validity.Dependency:
            # search for keywords with broken dependencies
            def _predicate(simple):
                cmd = simple.value
                if not isinstance(cmd, Command):
                    return False
                return cmd not in self._model

            visitor = FilterVisitor(_predicate)
            self.accept(visitor)

            # replace broken deps
            for kwd in visitor.keywords:
                replaceby = _search_compatible_commands(kwd.value)
                if replaceby is not None:
                    kwd.value = replaceby

    @property
    def is_prologue(self):
        """[bool]: True for the prologue commands, False for the rest."""
        return self._title in ("DEBUT", "POURSUITE")

    @property
    def is_epilogue(self):
        """[bool]: True for the epilogue command, False for the rest."""
        return self._title in ("FIN",)

    @property
    def is_deleter(self):
        """[bool]: *False*, only DETRUIRE command is a deleter!"""
        return False

    def deletes(self): # pragma pylint: disable=no-self-use
        """Return the list of results deleted by the command.

        Returns:
            []: Empty list.
        """
        return []

    @property
    def categ(self):
        """[int]: Category index of the command in the data tree."""
        if self.is_prologue:
            return -999
        if self.is_epilogue:
            return 999
        if self._title in ("_CONVERT_VARIABLE",):
            return -1000
        if self._title in ("_CONVERT_COMMENT",):
            children = [i for i in self.child_nodes if isinstance(i, Command)]
            if children:
                return children[0].categ
        return CATA.get_category_index(self._title)

    def _after_rename(self):
        """Called when command is renamed."""
        # Renaming could break validity in case of naming conflict
        self.reset_validity()

    @property
    def child_commands(self):
        """Commands that depend upon this one"""
        # Do NOT put `type(self)` instead of `Command` here
        return [i for i in self.child_nodes if isinstance(i, Command)]

    @property
    def parent_commands(self):
        """Commands this one depends on"""
        # Do NOT put `type(self)` instead of `Command` here
        return [i for i in self.parent_nodes if isinstance(i, Command)]

    def reset_dependencies(self):
        """Cleanup dependencies to other commands."""
        for parent in self.parent_commands:
            remove_parent(parent, self)
        for parent in self.child_commands:
            remove_parent(self, parent)
