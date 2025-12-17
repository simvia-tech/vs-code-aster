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

# liste des types de concept acceptes par la commande :
copier_ltyp = (
    cabl_precont,
    listr8_sdaster,
    listis_sdaster,
    fonction_sdaster,
    nappe_sdaster,
    table_sdaster,
    maillage_sdaster,
    modele_sdaster,
    evol_elas,
    evol_noli,
    evol_ther,
)


def copier_prod(CONCEPT, **args):
    if args.get("__all__"):
        return copier_ltyp

    return AsType(CONCEPT)


COPIER = OPER(
    nom="COPIER",
    op=185,
    sd_prod=copier_prod,
    reentrant="f:CONCEPT",
    fr=tr("Copier un concept utilisateur sous un autre nom"),
    reuse=SIMP(statut="c", typ=CO),
    CONCEPT=SIMP(statut="o", typ=copier_ltyp),
    INFO=SIMP(statut="f", typ="I", into=(1, 2), defaut=1),
)
