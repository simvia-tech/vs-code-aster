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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

LIRE_FORC_MISS = OPER(
    nom="LIRE_FORC_MISS",
    op=179,
    sd_prod=vect_asse_gene,
    fr=tr("Création d'un vecteur assemblé à partir d'une base modale"),
    reentrant="n",
    BASE=SIMP(statut="o", typ=mode_meca),
    NUME_DDL_GENE=SIMP(statut="o", typ=nume_ddl_gene),
    FREQ_EXTR=SIMP(statut="o", typ="R", max=1),
    NOM_CMP=SIMP(statut="f", typ="TXM", into=("DX", "DY", "DZ")),
    NOM_CHAM=SIMP(statut="f", typ="TXM", into=("DEPL", "VITE", "ACCE"), defaut="DEPL"),
    NUME_CHAR=SIMP(statut="f", typ="I"),
    ISSF=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "OUI")),
    UNITE_RESU_FORC=SIMP(statut="f", typ=UnitType(), defaut=30, inout="in"),
    NOM_RESU_FORC=SIMP(statut="f", typ="TXM"),
)
