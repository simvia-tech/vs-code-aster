# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2022 - EDF R&D - www.code-aster.org
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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

TEST_FICHIER = MACRO(
    nom="TEST_FICHIER",
    op=OPS("code_aster.MacroCommands.test_fichier_ops.test_fichier_ops"),
    fr=tr("Tester la non régression de fichiers produits par " "des commandes aster"),
    FICHIER=SIMP(statut="o", typ="TXM", validators=LongStr(1, 255)),
    EXPR_IGNORE=SIMP(
        statut="f",
        typ="TXM",
        max="**",
        fr=tr("Liste d'expressions régulières permettant " "d'ignorer certaines lignes"),
    ),
    NB_VALE=SIMP(statut="o", typ="I", fr=tr("Nombre de réels")),
    NB_VALE_I=SIMP(statut="f", typ="I", fr=tr("Nombre d'entiers si VALE_CALC_I est présent")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    **C_TEST_REFERENCE("FICHIER", max=1)
)
