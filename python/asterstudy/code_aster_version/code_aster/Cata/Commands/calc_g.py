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

# person_in_charge: tanguy.mathieu at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calcg_prod(self, THETA, **args):
    if args.get("__all__"):
        return ([table_container], [table_container, cham_no_sdaster])

    if "CHAM_THETA" in THETA and THETA["CHAM_THETA"].is_typco():
        return [table_container, cham_no_sdaster]

    return table_container


CALC_G = OPER(
    nom="CALC_G",
    op=27,
    sd_prod=calcg_prod,
    fr=tr(
        "Nouvel opérateur de calcul du taux de restitution d'énergie par la méthode theta en thermo-élasticité"
        " et des facteurs d'intensité de contraintes."
    ),
    reentrant="n",
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli, dyna_trans, mode_meca)),
    b_ordre=BLOC(
        condition="""is_type("RESULTAT") in (evol_elas,evol_noli,dyna_trans,)""",
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        b_acce_reel=BLOC(
            condition="""(exists("INST"))or(exists("LIST_INST"))""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
    ),
    b_mode=BLOC(
        condition="""is_type("RESULTAT") in (mode_meca,)""",
        TOUT_MODE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_MODE=SIMP(statut="f", typ=listis_sdaster),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        regles=(EXCLUS("TOUT_MODE", "NUME_MODE", "LIST_MODE", "FREQ", "LIST_FREQ"),),
        b_acce_reel=BLOC(
            condition="""(exists("FREQ"))or(exists("LIST_FREQ"))""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
    ),
    # Create theta-field
    THETA=FACT(
        statut="o",
        FISSURE=SIMP(statut="o", typ=fond_fissure, max=1),
        CHAM_THETA=SIMP(statut="f", typ=(CO, cham_no_sdaster), max=1),
        DISCRETISATION=SIMP(
            statut="f", typ="TXM", into=("LINEAIRE", "LEGENDRE"), defaut="LINEAIRE"
        ),
        b_nb_lin=BLOC(
            condition="""(equal_to("DISCRETISATION", 'LINEAIRE'))""",
            NB_POINT_FOND=SIMP(statut="f", typ="I", min=1),
        ),
        b_nb_leg=BLOC(
            condition="""(equal_to("DISCRETISATION", 'LEGENDRE'))""",
            DEGRE=SIMP(statut="f", typ="I", defaut=5, min=0, max=7),
        ),
        b_theta_cham=BLOC(
            condition="""( (not exists("CHAM_THETA")) or (is_type("CHAM_THETA") != cham_no_sdaster) )""",
            R_INF=SIMP(statut="f", typ="R", min=0),
            R_SUP=SIMP(statut="f", typ="R", min=0),
            R_INF_FO=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            R_SUP_FO=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            NB_COUCHE_INF=SIMP(statut="f", typ="I", min=0),
            NB_COUCHE_SUP=SIMP(statut="f", typ="I", min=1),
            regles=(
                PRESENT_PRESENT("R_INF", "R_SUP"),
                PRESENT_PRESENT("R_INF_FO", "R_SUP_FO"),
                PRESENT_PRESENT("NB_COUCHE_INF", "NB_COUCHE_SUP"),
                EXCLUS("R_INF", "NB_COUCHE_INF"),
                EXCLUS("R_SUP", "NB_COUCHE_INF"),
                EXCLUS("R_SUP", "NB_COUCHE_SUP"),
                EXCLUS("R_INF", "NB_COUCHE_SUP"),
                EXCLUS("R_INF", "R_INF_FO"),
                EXCLUS("R_INF_FO", "NB_COUCHE_INF"),
            ),
        ),
    ),
    # loading
    b_excit=BLOC(
        condition="""is_type("RESULTAT") in (mode_meca, dyna_trans,)""",
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
    ),
    OPTION=SIMP(statut="o", typ="TXM", max="**", into=("G", "G_EPSI", "K", "KJ", "KJ_EPSI")),
    b_option=BLOC(
        condition="""(not equal_to("OPTION", 'G_EPSI') )""",
        ETAT_INIT=FACT(
            statut="f",
            SIGM=SIMP(statut="o", typ=(cham_no_sdaster, cham_elem)),
            #               DEPL            =SIMP(statut='f',typ=cham_no_sdaster),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
