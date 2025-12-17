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
Catalogs
--------

Implementation of the catalogs container.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import os
import os.path as osp
import re
import traceback
from collections import OrderedDict
from itertools import chain

from .aster_syntax import IDS, get_cata_typeid, import_aster
from .dict_categories import CATEGORIES_DEFINITION, DEPRECATED
from .global_dict import GLOBAL_DICT


class Catalogs:
    """Class for the catalogs access"""

    def __init__(self):
        """Create catalogs object."""
        self._version = None
        self._pkgs = {}
        self._catalogs = {}
        self._categories = OrderedDict()
        self._command_to_category = {}
        self._command_to_subcategory = {}
        self._dockeys = {}
        self.read_catalogs()

    def reset(self):
        """Reset catalogs when version is changing."""
        self._pkgs.clear()
        self._catalogs.clear()
        self._categories.clear()
        self._command_to_category.clear()
        self._command_to_subcategory.clear()
        self._version = None

    def package(self, pkg_name):
        """
        Get the package of *code_aster.Cata* by its name.

        Returnds:
            package: Package being requested.
        """
        return self._pkgs[pkg_name]

    @staticmethod
    def version_path(version):
        """Return the path to a version.

        Arguments:
            version (str): Version label.

        Returns:
            str: Path to the version.
        """
        from ..common.configuration import CFG
        try:
            version_path = CFG.get("Versions", version)
        except KeyError:
            version_path = version
        return version_path

    def data_path(self, version, path):
        """Return the path where to find data for a version.

        Arguments:
            version (str): Version label.
            path (str): Path, relative to 'share/aster'.

        Returns:
            str: Path to the directory.
        """
        base = self.version_path(version)
        return osp.normpath(osp.join(base, os.pardir, os.pardir,
                                     "share", "aster", path))

    def read_catalogs(self, version=None):
        """
        Read all catalogs.

        Arguments:
            version (str): Version of code_aster catalogs.
        """
        from ..common.configuration import CFG
        from ..common.session import AsterStudySession
        from ..common.utilities import debug_message, info_message

        if version and version == self._version:
            debug_message("Catalog for {0!r}: already loaded".format(version))
            return

        self.reset()
        if not version:
            version = 'stable'
        debug_message("Loading catalog for {0!r}".format(version))
        # A FAIRE MODIFIER, : changer le chemin
        import pathlib as pl 
        version_path = pl.Path(__file__).parent.parent / "code_aster_version" / "code_aster"
        debug_message("from path {0!r}".format(version_path))

        # Enable marker
        AsterStudySession.set_cata()
        # try:
        self._pkgs = import_aster(version_path)
        commands = self._pkgs["Commands"].__dict__
        # except ImportError as exc:
        #     info_message("Can not import version {0!r}\nReason: {1}"
        #                  .format(version_path, exc))
        #     commands = {}

        if commands:
            self._add_conversion_commands()
        for key, value in list(commands.items()):
            if get_cata_typeid(value) == IDS.command:
                self._catalogs[key] = value

        self._fill_categories()
        self._version = version
        # TO DO : A remettre si on veut recuperer l'url de la doc d'une commande:
        # self._read_dockeys()

    @property
    def version(self):
        """str: Attribute that holds current catalog's version."""
        return self._version

    @property
    def version_number(self):
        """str: Attribute that holds current catalog's version number."""
        from ..common import CatalogError
        try:
            vers = self.package("aster_version")
        except KeyError as exc:
            details = traceback.format_exc()
            raise CatalogError("Package not found: {0}".format(exc), details) \
                from exc
        return vers.VERSION_MAJOR, vers.VERSION_MINOR, vers.VERSION_PATCH

    def _add_conversion_commands(self):
        """Add fake commands."""
        stx = self.package("Syntax")
        oper = stx.OPER
        simp = stx.SIMP
        variable = oper(nom="_CONVERT_VARIABLE",
                        sd_prod=stx.DS.PythonVariable,
                        fr="Definition of a user variable",
                        EXPR=simp(statut='o', typ='TXM'))
        comment = oper(nom="_CONVERT_COMMENT",
                       fr="A line of comment",
                       EXPR=simp(statut='o', typ='TXM'))

        hidden = oper(nom="_RESULT_OF_MACRO",
                      sd_prod=_hidden_prod,
                      fr="A hidden command",
                      DECL=simp(statut='o'),
                      PARENT=simp(statut='o'),
                      PATH=simp(statut='o'))

        fake = {'_CONVERT_VARIABLE': variable,
                '_CONVERT_COMMENT': comment,
                '_RESULT_OF_MACRO': hidden}

        self._catalogs.update(fake)

    # TODO Add a category for special "commands": _CONVERT_*
    def _fill_categories(self):
        """Fill categories map."""
        from ..common.utilities import debug_message
        not_found_msg = "Command {0} is not found in catalogue"

        # 0. First of all add special category for variables
        self._command_to_category['_CONVERT_VARIABLE'] = 'Variables'
        self._categories['Variables'] = []

        # 1. Fill in categories in proper order
        for category in CATEGORIES_DEFINITION:
            self._categories[category] = []
            for name in CATEGORIES_DEFINITION[category]:
                subcategory = name[0] \
                    if isinstance(name, (tuple, list)) else None
                commands = name[1] \
                    if isinstance(name, (tuple, list)) else [name]
                for command_name in commands:
                    command = self._catalogs.get(command_name)
                    if not command:
                        debug_message(not_found_msg.format(command_name))
                    else:
                        self._categories[category].append(command_name)
                        self._command_to_category[command_name] = category
                        self._command_to_subcategory[command_name] = subcategory

        # Finally, add a category for deprecated commands
        self._categories['Other'] = []
        self._categories['Deprecated'] = []
        self._categories['Hidden'] = []
        for name in DEPRECATED:
            self._categories['Deprecated'].append(name)
            self._command_to_category[name] = 'Deprecated'

        # 2. Put remaining commands to the 'Other' category
        for name in self._catalogs:
            if self._command_to_category.get(name):
                continue
            # fake commands starts with "_": hidden
            if name.startswith("_"):
                category = 'Hidden'
            else:
                category = 'Other'
            self._categories[category].append(name)
            self._command_to_category[name] = category
        self._categories['Other'].sort()

    def is_co(self, astype):
        """Tell if the given code_aster type is CO (result of
        macro-command).

        Arguments:
            astype (type): Type being checked.

        Returns:
            bool: Check status.
        """
        if isinstance(astype, (tuple, list)):
            return self.package("DataStructure").CO in astype

        return astype is self.package("DataStructure").CO

    @property
    def baseds(self):
        """Get the type on which all datastructures are based.

        Returns:
            type: Base data structure type.
        """
        return self.package("DataStructure").DataStructure

    @property
    def unitds(self):
        """Get the type on which all keywords that expect a file are based.

        Returns:
            type: Base type for file type (*UNITE* keywords).
        """
        return self.package("DataStructure").UnitBaseType

    @property
    def command(self):
        """Get the Command type.

        Returns:
            type: Command type.
        """
        return self.package("SyntaxObjects").Command

    def expects_result(self, command):
        """Tell if the given command must return a result (is an *Operator*).

        *Procedures* create no results, *Macros* may create 0 or 1 result.

        Arguments:
            command (object): Command to check.

        Returns:
            bool: *True* if the command must return a result, *False* otherwise.
        """
        need = isinstance(command, (self.package("Syntax").Operator,
                                    self.package("Syntax").Formule))
        if not need and isinstance(command, self.package("Syntax").Macro):
            types = command.get_all_types()
            if isinstance(types[0], (list, tuple)):
                # types[0] contains possible types of the main result
                need = None not in types[0]
            else:
                # simple sdprod
                need = None not in types
        return need

    def get_categories(self, usage=None):
        """Get all categories.

        Arguments:
            usage (str): By default, returns all categories. "toolbar" returns
                the categories for the toolbar, "showall" for the "Show All"
                dialog.

        Returns:
            list[str]: Names of all categories.
        """
        categ = list(self._categories.keys())
        if usage:
            categ.remove("Hidden")
        if usage in ("showall", "toolbar"):
            categ.remove("Variables")
        if usage == "toolbar":
            categ.remove("Other")
            categ.remove("Deprecated")
        return categ

    def get_category(self, category):
        """Get all commands in given category.

        Arguments:
            category (str): Name of the category.

        Returns:
            list[str]: Names of all commands in given category.
        """
        return self._categories.get(category, [])

    def get_command_category(self, command):
        """Get category owning the command.

        Arguments:
            command (str): Name of the command.

        Returns:
            str: Name of the category.
        """
        return self._command_to_category.get(command)

    def get_command_subcategory(self, command):
        """Get sub-category the command belongs to.

        Arguments:
            command (str): Name of the command.

        Returns:
            str: Name of the sub-category (*None* if sub-category
            is not specified).
        """
        return self._command_to_subcategory.get(command)

    def get_category_index(self, command):
        """Get index of category owning the command.

        Arguments:
            command (str): Name of the command.

        Returns:
            int: Index of the category in the catalogs.
        """
        category = self.get_command_category(command)
        return self.get_categories().index(category) if category else -1

    def get_catalog(self, command):
        """Get the catalog of a command.

        Arguments:
            command (str): Name of the command.

        Returns:
            PartOfSyntax: Command's catalog class.
        """
        return self._catalogs.get(str(command))

    def iteritems(self):
        """Return an iterator over the pairs (*command name*, *catalog*).
        """
        for key, value in self._catalogs.items():
            yield key, value

    def __iter__(self):
        """Iterator over command names."""
        for key in self._catalogs:
            yield key

    def get_translation(self, command, keyword=None, item=None):
        """Return the translation for a command or keyword name, or for
        keyword's value (to manage *into* attribute).

        The translation is provided by the catalog or a global dictionary.
        """
        key = item if item is not None else \
            keyword if keyword is not None else command
        cata = self.get_catalog(command)
        if cata is not None:
            dtr = cata.definition.get("translation", {})
            trans = dtr.get(key)
            if trans is not None:
                return trans
        return GLOBAL_DICT.get(key, key)

    def _read_dockeys(self):
        from ..common.configuration import CFG
        template = "clefs_docu_{0}"
        self._dockeys = {}
        for name in (self.version, "stable"):
            filename = CFG.rcfile(template.format(name))
            if filename:
                with open(filename, "r") as file:
                    for line in file:
                        cmd, url = line.split(":", 1)
                        self._dockeys[cmd] = url.strip()
                    break

    @staticmethod
    def possible_types(command):
        """Return possible Code_aster command types."""
        all_types = command.get_all_types()
        try:
            all_types = list(chain.from_iterable(all_types))
        except TypeError:
            return all_types

        types = []
        # keep order without twices
        for i in all_types:
            if i not in types:
                types.append(i)
        return types

    @property
    def type2command(self):
        """Returns commands that can create each type.

        Returns:
            dict: Dict of {"type name": *Command*}.
        """
        typ2cmd = dict()
        for _, command in self.iteritems():
            for typ in self.possible_types(command):
                if typ is None:
                    continue
                typname = typ.__name__
                if typname in typ2cmd:
                    continue
                typ2cmd[typname] = command
        return typ2cmd

    def get_command_url(self, command, base_url, language=None):
        """Return the url of the documentation for a command name.

        Arguments:
            command (str): Command name.
            base_url (str): Root documentation page's URL.
            language (Optional[str]): Documentation language. Defaults
                to *None* (in this case, default language 'fr' is used).

        Returns:
            str: Url of the documentation or *None*.
        """
        vers = self.package("aster_version")
        branch = "default"
        expl = re.search('^(v[0-9]+)', vers.BRANCH)
        if expl:
            branch = expl.group(1)
        if not language:
            language = "fr"
        info = dict(branch=branch, lang=language,
                    base_url=base_url.rstrip("/"))
        base = "{base_url}/{branch}/{lang}/".format(**info)
        failover = "index.php?man=commande"
        return base + self._dockeys.get(command, failover)

    def get_command_docstring(self, command):
        """Return the docstring for given command.

        Arguments:
            command (str): Command name.

        Returns:
            str: Command's docstring.
        """
        return self.get_catalog(command).udocstring
    
    def get_command_definition(self, command_name, context):
        """
        Retourne la définition détaillée d'une commande du catalogue AsterStudy sous forme de string.

        Args:
            command_name (str): Nom de la commande (ex: "LIRE_MAILLAGE")
        Returns:
            str: Description lisible de la commande et de ses arguments.
        """
        from asterstudy.datamodel.catalogs import CATA
        lines = []

        def _format_type(typ):
            if isinstance(typ, type):
                return typ.__name__
            elif isinstance(typ, (tuple, list)) and typ and all(isinstance(t, type) for t in typ):
                return '(' + ', '.join(t.__name__ for t in typ) + ')'
            elif isinstance(typ, str):
                return typ
            else:
                return str(typ)

        def _print_kwd(definition, prefix="", depth=0, context=None):
            indent = "  " * depth
            for key, kwd in definition.items():
                if not hasattr(kwd, "definition"):
                    continue
                statut = kwd.definition.get("statut", "?")
                typ = kwd.definition.get("typ", "?")
                typ_str = _format_type(typ)
                defaut = kwd.definition.get("defaut", None)
                into = kwd.definition.get("into", None)
                fac = "facultatif" if statut != "o" else "obligatoire"
                fullkey = f"{prefix}{key}"
                if "FactorKeyword" in str(type(kwd)):
                    lines.append(f"{indent}- {fullkey} | {fac} , contient :")
                    _print_kwd(kwd.definition, "", depth=depth + 1)
                elif "Bloc" in str(type(kwd)):  
                    if context is None:
                        lines.append(f"{indent}Si {kwd.getCondition()}:")
                        _print_kwd(kwd.definition, "" ,depth=depth + 1)
                    else:
                        if kwd.isEnabled(context):
                            _print_kwd(kwd.definition, "")
                else:
                    line = f"{indent}- {fullkey} | {fac} | type: {typ_str} | défaut: {defaut}"
                    if into:
                        line += f" | valeurs permises: {into}"
                    lines.append(line)

        # Recherche de la commande dans le catalogue
        for name, command_obj in self.iteritems():
            if name == command_name:
                lines.append(f"'{command_name}' : {self.get_command_docstring(command_name)}")
                lines.append(f"Liste des arguments :")
                _print_kwd(command_obj.definition, context = context)  
                return "\n".join(lines)
        return ""

    def parse_kwd(self, definition, context):
        params = []

        def _format_type(typ):
            if isinstance(typ, type):
                return typ.__name__
            elif isinstance(typ, (tuple, list)):
                return "(" + ", ".join(t.__name__ if isinstance(t, type) else str(t) for t in typ) + ")"
            elif isinstance(typ, str):
                return typ
            return str(typ)

        for key, kwd in definition.items():
            if not hasattr(kwd, "definition"):
                continue
            statut = kwd.definition.get("statut", "?")
            typ = kwd.definition.get("typ", "?")
            typ_str = _format_type(typ)
            defaut = kwd.definition.get("defaut", None)
            into = kwd.definition.get("into", None)

            param = {
                "name": key,
                "required": (statut == "o"),
                "type": typ_str,
                "default": defaut,
                "allowed": into,
                "children": [],
                "bloc": None
            }

            if "FactorKeyword" in str(type(kwd)) or "Bloc" in str(type(kwd)): 
                if "Bloc" in str(type(kwd)) :
                    param["bloc"] = kwd
                    if context is not None :
                        if not kwd.isEnabled(context):
                            continue
                param["children"] = self.parse_kwd(kwd.definition, context=context)

            params.append(param)

        return params
    
    def get_command_obj(self, command_name):
        for name, command_obj in self.iteritems():
            if name == command_name:
                return command_obj


    def parse_command(self, command_obj,context= None):
        return {
                "name": command_obj.name,
                "doc": self.get_command_docstring(command_obj.name),
                "params": self.parse_kwd(command_obj.definition,context)
            }

    def get_commands(self) -> list[dict]:
        commands = []
        for name, command_obj in self.iteritems():
            commands.append({
                "name": name,
                "doc": self.get_command_docstring(command_obj.name)
            })
        return commands



def _hidden_prod(**kwargs):
    decl = kwargs.get("DECL")
    if decl:
        return decl.gettype()
    return None

def reusable_keywords(reentrant):
    """Return the list of keywords that can contain the reusable object.

    Arguments:
        reentrant (str): Definition of 'reentrant' attribute of a Command.

    Returns:
        tuple: The first item of the tuple is a boolean telling if the command
        must modify an object or not. The second is a list of keywords.
        It can be a list of simple keywords at the
        toplevel ["MCS1", "MCS2"...] or a list of the sample simple keyword
        under different factor keywords ["MCF1/MCS", "MCF2/MCS"...].
    """
    raw = reentrant.split(':')
    required = raw.pop(0) == 'o'
    if not raw:
        keywords = []
    elif len(raw) > 1:
        keywords = ['/'.join([i, raw[1]]) for i in raw[0].split('|')]
    else:
        keywords = raw[0].split('|')
    return required, keywords




CATA = Catalogs()
