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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

NUME_DDL_GENE = OPER(
    nom="NUME_DDL_GENE",
    op=127,
    sd_prod=nume_ddl_gene,
    fr=tr(
        "Etablissement de la numérotation des ddl d'un modèle etabli en coordonnées généralisees"
    ),
    reentrant="n",
    regles=UN_PARMI("MODELE_GENE", "BASE"),
    MODELE_GENE=SIMP(statut="f", typ=modele_gene),
    b_modele_gene=BLOC(
        condition="""exists("MODELE_GENE")""",
        STOCKAGE=SIMP(statut="f", typ="TXM", defaut="LIGN_CIEL", into=("LIGN_CIEL", "PLEIN")),
        METHODE=SIMP(
            statut="f", typ="TXM", defaut="CLASSIQUE", into=("INITIAL", "CLASSIQUE", "ELIMINE")
        ),
    ),
    BASE=SIMP(statut="f", typ=(mode_meca, mode_gene)),
    b_base=BLOC(
        condition="""exists("BASE")""",
        STOCKAGE=SIMP(statut="f", typ="TXM", defaut="PLEIN", into=("DIAG", "PLEIN")),
        NB_VECT=SIMP(statut="f", typ="I"),
    ),
)
