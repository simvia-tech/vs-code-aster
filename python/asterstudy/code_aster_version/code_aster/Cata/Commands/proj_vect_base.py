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

PROJ_VECT_BASE = OPER(
    nom="PROJ_VECT_BASE",
    op=72,
    sd_prod=vect_asse_gene,
    fr=tr("Projection d'un vecteur assemblé sur une base (modale ou de RITZ)"),
    reentrant="n",
    regles=(UN_PARMI("VECT_ASSE", "VECT_ASSE_GENE"),),
    BASE=SIMP(statut="o", typ=(mode_meca, mode_gene)),
    NUME_DDL_GENE=SIMP(statut="o", typ=nume_ddl_gene),
    TYPE_VECT=SIMP(statut="o", typ="TXM", into=("FORC", "DEPL", "VITE", "ACCE")),
    VECT_ASSE=SIMP(statut="f", typ=cham_no_sdaster),
    VECT_ASSE_GENE=SIMP(statut="f", typ=vect_asse_gene),
)
