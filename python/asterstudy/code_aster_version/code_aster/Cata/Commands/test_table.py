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

TEST_TABLE = PROC(
    nom="TEST_TABLE",
    op=177,
    fr=tr("Tester une cellule ou une colonne d'une table"),
    #  concept table_sdaster à tester
    TABLE=SIMP(statut="o", typ=table_sdaster),
    FILTRE=FACT(
        statut="f",
        max="**",
        NOM_PARA=SIMP(statut="o", typ="TXM"),
        CRIT_COMP=SIMP(
            statut="f",
            typ="TXM",
            defaut="EQ",
            into=(
                "EQ",
                "LT",
                "GT",
                "NE",
                "LE",
                "GE",
                "VIDE",
                "NON_VIDE",
                "MAXI",
                "MAXI_ABS",
                "MINI",
                "MINI_ABS",
            ),
        ),
        b_vale=BLOC(
            condition="""(is_in("CRIT_COMP", ('EQ','NE','GT','LT','GE','LE')))""",
            regles=(UN_PARMI("VALE", "VALE_I", "VALE_K", "VALE_C"),),
            VALE=SIMP(statut="f", typ="R"),
            VALE_I=SIMP(statut="f", typ="I"),
            VALE_C=SIMP(statut="f", typ="C"),
            VALE_K=SIMP(statut="f", typ="TXM"),
        ),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ),
    NOM_PARA=SIMP(statut="o", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    **C_TEST_REFERENCE("TABLE", max="**")
)
