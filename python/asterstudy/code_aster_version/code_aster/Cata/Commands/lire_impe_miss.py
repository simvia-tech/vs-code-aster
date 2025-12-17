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

LIRE_IMPE_MISS = OPER(
    nom="LIRE_IMPE_MISS",
    op=164,
    sd_prod=matr_asse_gene_c,
    fr=tr("Création d une matrice assemblée à partir de base modale"),
    reentrant="n",
    BASE=SIMP(statut="o", typ=mode_meca),
    NUME_DDL_GENE=SIMP(statut="o", typ=nume_ddl_gene),
    FREQ_EXTR=SIMP(statut="f", typ="R", max=1),
    INST_EXTR=SIMP(statut="f", typ="R", max=1),
    UNITE_RESU_IMPE=SIMP(statut="f", typ=UnitType(), defaut=30, inout="in"),
    ISSF=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "OUI")),
    TYPE=SIMP(statut="f", typ="TXM", defaut="ASCII", into=("BINAIRE", "ASCII")),
    SYME=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "OUI")),
)
