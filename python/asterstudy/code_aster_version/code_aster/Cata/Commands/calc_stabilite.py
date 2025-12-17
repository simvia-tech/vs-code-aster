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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_STABILITE = MACRO(
    nom="CALC_STABILITE",
    sd_prod=table_container,
    op=OPS("code_aster.MacroCommands.calc_stabilite_ops.calc_stabilite_ops"),
    fr=tr("post-traitement modes non-linéaires : filtre resultats et calcul de stabilité"),
    reentrant="f:MODE_NON_LINE",
    reuse=SIMP(statut="c", typ=CO),
    MODE_NON_LINE=SIMP(statut="o", typ=table_container, max=1),
    SCHEMA_TEMPS=FACT(
        statut="d",
        max=1,
        SCHEMA=SIMP(statut="f", typ="TXM", into=("NEWMARK",), defaut="NEWMARK"),
        b_newmark=BLOC(
            condition="""equal_to("SCHEMA", 'NEWMARK')""",
            NB_INST=SIMP(statut="f", typ="I", defaut=1000),
        ),
    ),
    TOLERANCE=SIMP(statut="f", typ="R", defaut=1.0e-2),
    FILTRE=FACT(
        statut="f",
        max=1,
        regles=(UN_PARMI("NUME_ORDRE", "FREQ_MIN"),),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        FREQ_MIN=SIMP(statut="f", typ="R"),
        b_freq_min=BLOC(
            condition="""exists("FREQ_MIN")""",
            FREQ_MAX=SIMP(statut="o", typ="R"),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
