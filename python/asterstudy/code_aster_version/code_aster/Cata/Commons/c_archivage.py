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

# person_in_charge: mickael.abbas at edf.fr

from ..Language.DataStructure import listr8_sdaster
from ..Language.Syntax import BLOC, FACT, SIMP, UN_PARMI, NoRepeat


def C_ARCHIVAGE():
    return FACT(
        statut="d",
        max=1,
        regles=(UN_PARMI("PAS_ARCH", "LIST_INST", "INST", PAS_ARCH=1),),
        PAS_ARCH=SIMP(statut="f", typ="I"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        b_crit=BLOC(
            condition="""exists("INST") or exists("LIST_INST")""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""equal_to("CRITERE", 'RELATIF')""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""equal_to("CRITERE", 'ABSOLU')""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
        CHAM_EXCLU=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    )
