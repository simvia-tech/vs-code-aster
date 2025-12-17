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


def proj_mesu_modal_prod(MODELE_MESURE, **args):
    if args.get("__all__"):
        return (tran_gene, harm_gene, mode_gene)

    vale = MODELE_MESURE["MESURE"]
    if AsType(vale) == dyna_trans:
        return tran_gene
    if AsType(vale) == dyna_harmo:
        return harm_gene
    if AsType(vale) == mode_meca:
        return mode_gene
    if AsType(vale) == mode_meca_c:
        return mode_gene
    #     if  AsType(vale) == base_modale  : return mode_gene
    raise AsException("type de concept resultat non prevu")


PROJ_MESU_MODAL = OPER(
    nom="PROJ_MESU_MODAL",
    op=193,
    sd_prod=proj_mesu_modal_prod,
    reentrant="n",
    fr=tr(
        "Calcul des coordonnees généralisees de mesure experimentale relatives a une base de projection"
    ),
    MODELE_CALCUL=FACT(
        statut="o",
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        #           BASE            =SIMP(statut='o',typ=(mode_meca,base_modale,) ),
        BASE=SIMP(statut="o", typ=mode_meca),
    ),
    MODELE_MESURE=FACT(
        statut="o",
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        #           MESURE          =SIMP(statut='o',typ=(dyna_trans,dyna_harmo,base_modale,mode_meca,mode_meca_c,) ),
        MESURE=SIMP(statut="o", typ=(dyna_trans, dyna_harmo, mode_meca, mode_meca_c)),
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            defaut="DEPL",
            into=("DEPL", "VITE", "ACCE", "SIEF_NOEU", "EPSI_NOEU"),
            max="**",
        ),
    ),
    CORR_MANU=FACT(
        statut="f",
        max="**",
        regles=(PRESENT_PRESENT("NOEU_CALCUL", "NOEU_MESURE"),),
        NOEU_CALCUL=SIMP(statut="f", typ=no),
        NOEU_MESURE=SIMP(statut="f", typ=no),
    ),
    NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
    RESOLUTION=FACT(
        statut="f",
        METHODE=SIMP(statut="f", typ="TXM", defaut="LU", into=("LU", "SVD")),
        b_svd=BLOC(
            condition="""equal_to("METHODE", 'SVD')""", EPS=SIMP(statut="f", typ="R", defaut=0.0)
        ),
        REGUL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "NORM_MIN", "TIK_RELA")),
        b_regul=BLOC(
            condition="""not equal_to("REGUL", 'NON')""",
            regles=(PRESENT_ABSENT("COEF_PONDER", "COEF_PONDER_F"),),
            COEF_PONDER=SIMP(statut="f", typ="R", max="**"),
            COEF_PONDER_F=SIMP(
                statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"
            ),
        ),
    ),
)
