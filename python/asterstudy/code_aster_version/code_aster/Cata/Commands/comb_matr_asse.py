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

# person_in_charge: nicolas.sellenet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def comb_matr_asse_prod(COMB_R, COMB_C, CALC_AMOR_GENE, **args):
    if args.get("__all__"):
        return (
            matr_asse_depl_c,
            matr_asse_gene_c,
            matr_asse_temp_c,
            matr_asse_pres_c,
            matr_asse_depl_r,
            matr_asse_gene_r,
            matr_asse_temp_r,
            matr_asse_pres_r,
        )

    if COMB_C:
        type_mat = AsType(COMB_C[0]["MATR_ASSE"])
        if type_mat in (matr_asse_depl_c, matr_asse_depl_r):
            return matr_asse_depl_c
        if type_mat in (matr_asse_gene_c, matr_asse_gene_r):
            return matr_asse_gene_c
        if type_mat in (matr_asse_temp_c, matr_asse_temp_r):
            return matr_asse_temp_c
        if type_mat in (matr_asse_pres_c, matr_asse_pres_r):
            return matr_asse_pres_c
    elif COMB_R:
        type_mat = AsType(COMB_R[0]["MATR_ASSE"])
        if type_mat in (matr_asse_depl_c, matr_asse_depl_r):
            return matr_asse_depl_r
        if type_mat in (matr_asse_temp_c, matr_asse_temp_r):
            return matr_asse_temp_r
        if type_mat in (matr_asse_pres_c, matr_asse_pres_r):
            return matr_asse_pres_r
        if type_mat in (matr_asse_gene_c, matr_asse_gene_r):
            return matr_asse_gene_r
    elif CALC_AMOR_GENE:
        return matr_asse_gene_r
    raise AsException("type de concept resultat non prevu")


COMB_MATR_ASSE = OPER(
    nom="COMB_MATR_ASSE",
    op=31,
    sd_prod=comb_matr_asse_prod,
    fr=tr("Effectuer la combinaison linéaire de matrices assemblées"),
    reentrant="f:MATR_ASSE",
    regles=(UN_PARMI("COMB_R", "COMB_C", "CALC_AMOR_GENE"),),
    reuse=SIMP(statut="c", typ=CO),
    MATR_ASSE=SIMP(
        statut="f",
        typ=(
            matr_asse_depl_r,
            matr_asse_depl_c,
            matr_asse_temp_r,
            matr_asse_temp_c,
            matr_asse_pres_r,
            matr_asse_pres_c,
            matr_asse_gene_r,
            matr_asse_gene_c,
        ),
        fr=tr("Objet qui sera réutilisé pour l'opération"),
    ),
    COMB_R=FACT(
        statut="f",
        max="**",
        PARTIE=SIMP(statut="f", typ="TXM", into=("REEL", "IMAG")),
        MATR_ASSE=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_depl_c,
                matr_asse_temp_r,
                matr_asse_temp_c,
                matr_asse_pres_r,
                matr_asse_pres_c,
                matr_asse_gene_r,
                matr_asse_gene_c,
            ),
        ),
        COEF_R=SIMP(statut="o", typ="R"),
    ),
    COMB_C=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("COEF_R", "COEF_C"),),
        MATR_ASSE=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_depl_c,
                matr_asse_temp_r,
                matr_asse_temp_c,
                matr_asse_pres_r,
                matr_asse_pres_c,
                matr_asse_gene_r,
                matr_asse_gene_c,
            ),
        ),
        COEF_R=SIMP(statut="f", typ="R"),
        COEF_C=SIMP(statut="f", typ="C"),
    ),
    CALC_AMOR_GENE=FACT(
        statut="f",
        RIGI_GENE=SIMP(statut="o", typ=matr_asse_gene_r),
        MASS_GENE=SIMP(statut="o", typ=matr_asse_gene_r),
        regles=(UN_PARMI("AMOR_REDUIT", "LIST_AMOR"),),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
        LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
    ),
    SANS_CMP=SIMP(statut="f", typ="TXM", into=("LAGR",)),
)
