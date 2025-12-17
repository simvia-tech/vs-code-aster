# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2023 - EDF R&D - www.code-aster.org
# This file is part of code_aster.
#
# code_aster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# code_aster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with code_aster.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


EXEC_LOGICIEL = MACRO(
    nom="EXEC_LOGICIEL",
    op=OPS("code_aster.MacroCommands.exec_logiciel_ops.exec_logiciel_ops"),
    sd_prod=None,
    fr=tr("Exécute un logiciel ou une commande système depuis Aster"),
    LOGICIEL=SIMP(statut="o", typ="TXM", fr=tr("Programme ou script à exécuter")),
    ARGUMENT=SIMP(statut="f", max="**", typ="TXM", fr=tr("Arguments à transmettre à LOGICIEL")),
    SHELL=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="NON",
        fr=tr(
            "Execution dans un shell, nécessaire si LOGICIEL n'est pas "
            "un exécutable mais une ligne de commande complète utilisant "
            "des redirections ou des caractères de completions"
        ),
    ),
    CODE_RETOUR_MAXI=SIMP(
        statut="f",
        typ="I",
        defaut=0,
        val_min=-1,
        fr=tr("Valeur maximale du code retour toléré " "(-1 pour l'ignorer)"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=2, into=(1, 2)),
)
