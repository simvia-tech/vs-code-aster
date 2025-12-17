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

MACR_ELEM_DYNA = OPER(
    nom="MACR_ELEM_DYNA",
    op=81,
    sd_prod=macr_elem_dyna,
    fr=tr(
        "Definition d'un macro element pour analyse modale ou harmonique par sous structuration dynamique"
    ),
    reentrant="f:MACR_ELEM_DYNA",
    regles=(
        # AMOR_REDUIT et MATR_AMOR sont redondants
        EXCLUS("MATR_AMOR", "AMOR_REDUIT"),
        # Si MODELE_MESURE, on ne rentre pas de donnees pour le calcul
        EXCLUS("MODELE_MESURE", "MATR_RIGI"),
        EXCLUS("MODELE_MESURE", "MATR_MASS"),
        EXCLUS("MODELE_MESURE", "MATR_AMOR"),
        EXCLUS("MODELE_MESURE", "AMOR_REDUIT"),
        EXCLUS("MODELE_MESURE", "MATR_IMPE"),
        EXCLUS("MODELE_MESURE", "MATR_IMPE_RIGI"),
        EXCLUS("MODELE_MESURE", "MATR_IMPE_MASS"),
        EXCLUS("MODELE_MESURE", "MATR_IMPE_AMOR"),
        EXCLUS("SANS_GROUP_NO", "GROUP_NO"),
        PRESENT_ABSENT("MATR_IMPE", "MATR_IMPE_RIGI"),
        PRESENT_ABSENT("MATR_IMPE", "MATR_IMPE_MASS"),
        PRESENT_ABSENT("MATR_IMPE", "MATR_IMPE_AMOR"),
        PRESENT_ABSENT("MATR_IMPE", "MATR_RIGI", "MATR_MASS"),
        PRESENT_ABSENT("MATR_IMPE_MASS", "MATR_RIGI", "MATR_MASS"),
        PRESENT_ABSENT("MATR_IMPE_RIGI", "MATR_RIGI", "MATR_MASS"),
        PRESENT_ABSENT("MATR_IMPE_AMOR", "MATR_RIGI", "MATR_MASS"),
    ),
    reuse=SIMP(statut="c", typ=CO),
    MACR_ELEM_DYNA=SIMP(statut="f", typ=macr_elem_dyna),
    BASE_MODALE=SIMP(statut="o", typ=mode_meca),
    MATR_RIGI=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_depl_c)),
    MATR_MASS=SIMP(statut="f", typ=matr_asse_depl_r),
    MATR_AMOR=SIMP(statut="f", typ=matr_asse_depl_r),
    AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
    SANS_GROUP_NO=SIMP(statut="f", typ=grno),
    GROUP_NO=SIMP(statut="f", typ=grno),
    MATR_IMPE=SIMP(statut="f", typ=matr_asse_gene_c),
    MATR_IMPE_RIGI=SIMP(statut="f", typ=matr_asse_gene_c),
    MATR_IMPE_MASS=SIMP(statut="f", typ=matr_asse_gene_c),
    MATR_IMPE_AMOR=SIMP(statut="f", typ=matr_asse_gene_c),
    MODELE_MESURE=FACT(
        statut="f",
        FREQ=SIMP(statut="o", typ="R", max="**"),
        MASS_GENE=SIMP(statut="o", typ="R", max="**"),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
    ),
    b_matr_impe=BLOC(
        condition="""exists("MATR_IMPE")""",
        FREQ_EXTR=SIMP(statut="o", typ="R"),
        AMOR_SOL=SIMP(statut="f", typ="R", defaut=0.0e0),
        MATR_IMPE_INIT=SIMP(statut="f", typ=matr_asse_gene_c),
    ),
    CAS_CHARGE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("VECT_ASSE_GENE", "RESU_GENE"),),
        NOM_CAS=SIMP(statut="o", typ="TXM"),
        VECT_ASSE_GENE=SIMP(statut="f", typ=vect_asse_gene),
        RESU_GENE=SIMP(statut="f", typ=tran_gene),
    ),
)
