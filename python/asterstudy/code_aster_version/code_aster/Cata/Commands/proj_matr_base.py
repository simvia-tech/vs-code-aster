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


def matr_asse_gene_prod(MATR_ASSE, MATR_ASSE_GENE, **args):
    if args.get("__all__"):
        return (matr_asse_gene_r, matr_asse_gene_c)
    if AsType(MATR_ASSE) == matr_asse_depl_r:
        return matr_asse_gene_r
    if AsType(MATR_ASSE_GENE) == matr_asse_gene_r:
        return matr_asse_gene_r
    if AsType(MATR_ASSE) == matr_asse_depl_c:
        return matr_asse_gene_c
    if AsType(MATR_ASSE_GENE) == matr_asse_gene_c:
        return matr_asse_gene_c
    raise AsException("type de concept resultat non prevu")


PROJ_MATR_BASE = OPER(
    nom="PROJ_MATR_BASE",
    op=71,
    sd_prod=matr_asse_gene_prod,
    fr=tr("Projection d'une matrice assemblée sur une base (modale ou de RITZ)"),
    reentrant="n",
    regles=(UN_PARMI("MATR_ASSE", "MATR_ASSE_GENE"),),
    BASE=SIMP(statut="o", typ=(mode_meca, mode_gene)),
    NUME_DDL_GENE=SIMP(statut="o", typ=nume_ddl_gene),
    MATR_ASSE=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_depl_c)),
    MATR_ASSE_GENE=SIMP(statut="f", typ=(matr_asse_gene_r, matr_asse_gene_c)),
)
