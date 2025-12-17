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

ASSE_VECT_GENE = OPER(
    nom="ASSE_VECT_GENE",
    op=140,
    sd_prod=vect_asse_gene,
    fr=tr("Projection des chargements sur la base modale d'une sous structure"),
    reentrant="n",
    NUME_DDL_GENE=SIMP(statut="o", typ=nume_ddl_gene),
    METHODE=SIMP(statut="f", typ="TXM", defaut="CLASSIQUE", into=("CLASSIQUE", "INITIAL")),
    b_nume=BLOC(
        condition="""equal_to("METHODE", 'CLASSIQUE')""",
        CHAR_SOUS_STRUC=FACT(
            statut="o",
            max="**",
            SOUS_STRUC=SIMP(statut="o", typ="TXM"),
            VECT_ASSE=SIMP(statut="o", typ=cham_no_sdaster),
        ),
    ),
)
