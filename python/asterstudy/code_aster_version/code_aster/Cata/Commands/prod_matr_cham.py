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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

PROD_MATR_CHAM = OPER(
    nom="PROD_MATR_CHAM",
    op=156,
    sd_prod=cham_no_sdaster,
    fr=tr("Effectuer le produit d'une matrice par un vecteur"),
    reentrant="n",
    MATR_ASSE=SIMP(
        statut="o", typ=(matr_asse_depl_r, matr_asse_depl_c, matr_asse_temp_r, matr_asse_pres_c)
    ),
    CHAM_NO=SIMP(statut="o", typ=cham_no_sdaster),
    TITRE=SIMP(statut="f", typ="TXM"),
)
