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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

RECU_GENE = OPER(
    nom="RECU_GENE",
    op=76,
    sd_prod=vect_asse_gene,
    reentrant="n",
    fr=tr(
        "Extraire d'un champ de grandeur (déplacements, vitesses ou accélérations) à partir de résultats"
        " en coordonnées généralisées"
    ),
    regles=(UN_PARMI("FREQ", "INST"),),
    RESU_GENE=SIMP(statut="o", typ=(tran_gene, harm_gene)),
    INST=SIMP(statut="f", typ="R"),
    FREQ=SIMP(statut="f", typ="R"),
    NOM_CHAM=SIMP(statut="f", typ="TXM", defaut="DEPL", into=("DEPL", "VITE", "ACCE")),
    b_interp_temp=BLOC(
        condition="""exists("INST") and not exists("FREQ")""",
        INTERPOL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "LIN")),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
)
