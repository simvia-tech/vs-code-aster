# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2023 - EDF R&D - www.code-aster.org
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


def observation_prod(self, RESULTAT, **args):
    if args.get("__all__"):
        return (None, mode_meca, evol_elas, dyna_harmo, dyna_trans)

    if AsType(RESULTAT) == mode_meca:
        return mode_meca
    elif AsType(RESULTAT) == evol_elas:
        return evol_elas
    elif AsType(RESULTAT) == dyna_harmo:
        return dyna_harmo
    elif AsType(RESULTAT) == dyna_trans:
        return dyna_trans
    else:
        return None


OBSERVATION = MACRO(
    nom="OBSERVATION",
    op=OPS("code_aster.MacroCommands.observation_ops.observation_ops"),
    sd_prod=observation_prod,
    fr=tr("Calcul de l'observabilite d'un champ aux noeuds "),
    #
    MODELE_1=SIMP(statut="o", typ=modele_sdaster),
    MODELE_2=SIMP(statut="o", typ=modele_sdaster),
    RESULTAT=SIMP(statut="o", typ=(mode_meca, evol_elas, dyna_harmo, dyna_trans)),
    NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()),
    #        ------------------------------------------------------------------
    regles=(
        UN_PARMI("TOUT_ORDRE", "NUME_ORDRE", "FREQ", "LIST_FREQ", "NUME_MODE", "INST", "LIST_INST"),
    ),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    #        ------------------------------------------------------------------
    #        OPTIONS DE PROJ_CHAMP (SANS MC FACTEUR PARTICULIER)
    #        ------------------------------------------------------------------
    PROJECTION=SIMP(statut="f", max=1, typ="TXM", into=("OUI", "NON"), defaut="OUI"),
    CAS_FIGURE=SIMP(statut="f", typ="TXM", into=("2D", "3D", "2.5D", "1.5D")),
    DISTANCE_MAX=SIMP(
        statut="f",
        typ="R",
        fr=tr(
            "Distance maximale entre le noeud et l'élément le plus proche, lorsque le noeud n'est dans aucun élément."
        ),
    ),
    DISTANCE_ALARME=SIMP(statut="f", typ="R"),
    ALARME=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    TYPE_CHAM=SIMP(
        statut="f",
        typ="TXM",
        into=("NOEU",),
        fr=tr("Pour forcer le type des champs projetés. NOEU -> cham_no"),
    ),
    #           PROL_ZERO       =SIMP(statut='f',typ='TXM',into=("OUI","NON"),defaut="NON",
    #                fr=tr("Si le résultat est un mode_xxx ou une base_xxx, on peut prolonger")
    #                   +" les champs par zéro la ou la projection ne donne pas de valeurs."),
    MATR_RIGI=SIMP(statut="f", typ=(matr_asse_depl_r)),
    MATR_MASS=SIMP(statut="f", typ=(matr_asse_depl_r)),
    VIS_A_VIS=FACT(
        statut="f",
        max="**",
        regles=(
            AU_MOINS_UN("TOUT_1", "GROUP_MA_1", "GROUP_NO_1"),
            AU_MOINS_UN("TOUT_2", "GROUP_MA_2", "GROUP_NO_2"),
        ),
        TOUT_1=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        TOUT_2=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        CAS_FIGURE=SIMP(statut="f", typ="TXM", into=("2D", "3D", "2.5D", "1.5D")),
    ),
    #        ------------------------------------------------------------------
    #        MODI_REPERE
    #        ------------------------------------------------------------------
    MODI_REPERE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("REPERE"), AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO", "NOEUD")),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        #
        TYPE_CHAM=SIMP(
            statut="f",
            typ="TXM",
            into=("VECT_2D", "VECT_3D", "TENS_2D", "TENS_3D"),
            defaut="VECT_3D",
        ),
        b_vect_2d=BLOC(
            condition="""equal_to("TYPE_CHAM", 'VECT_2D')""",
            NOM_CMP=SIMP(statut="o", typ="TXM", min=2, max=2),
        ),
        b_vect_3d=BLOC(
            condition="""equal_to("TYPE_CHAM", 'VECT_3D')""",
            NOM_CMP=SIMP(statut="f", typ="TXM", min=3, max=3, defaut=("DX", "DY", "DZ")),
        ),
        b_tens_2d=BLOC(
            condition="""equal_to("TYPE_CHAM", 'TENS_2D')""",
            NOM_CMP=SIMP(
                statut="f", typ="TXM", min=4, max=4, defaut=("EPXX", "EPYY", "EPZZ", "EPXY")
            ),
        ),
        b_tens_3d=BLOC(
            condition="""equal_to("TYPE_CHAM", 'TENS_3D')""",
            NOM_CMP=SIMP(
                statut="f",
                typ="TXM",
                min=6,
                max=6,
                defaut=("EPXX", "EPYY", "EPZZ", "EPXY", "EPXZ", "EPYZ"),
            ),
        ),
        REPERE=SIMP(
            statut="o", typ="TXM", into=("UTILISATEUR", "CYLINDRIQUE", "NORMALE", "DIR_JAUGE")
        ),
        b_normale=BLOC(
            condition="""equal_to("REPERE", 'NORMALE')""",
            regles=(UN_PARMI("VECT_X", "VECT_Y")),
            VECT_X=SIMP(statut="f", typ="R", min=3, max=3),
            VECT_Y=SIMP(statut="f", typ="R", min=3, max=3),
        ),
        b_utilisateur=BLOC(
            condition="""equal_to("REPERE", 'UTILISATEUR')""",
            ANGL_NAUT=SIMP(statut="o", typ="R", max=3),
        ),
        b_cylindrique=BLOC(
            condition="""equal_to("REPERE", 'CYLINDRIQUE')""",
            ORIGINE=SIMP(statut="o", typ="R", min=2, max=3),
            AXE_Z=SIMP(statut="o", typ="R", min=3, max=3),
        ),
        b_dir_jauge=BLOC(
            condition="""equal_to("REPERE", 'DIR_JAUGE')""",
            VECT_X=SIMP(statut="f", typ="R", min=3, max=3),
            VECT_Y=SIMP(statut="f", typ="R", min=3, max=3),
        ),
    ),
    #        ------------------------------------------------------------------
    #        EPSI_MOYENNE
    #        ------------------------------------------------------------------
    EPSI_MOYENNE=FACT(
        statut="f",
        max="**",
        regles=(AU_MOINS_UN("GROUP_MA", "GROUP_NO", "NOEUD"),),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SEUIL_VARI=SIMP(statut="f", typ="R", validators=NoRepeat(), defaut=0.1),
        MASQUE=SIMP(statut="f", typ="TXM", max=6),
    ),
    #        ------------------------------------------------------------------
    #        FILTRE DES DDL
    #        ------------------------------------------------------------------
    FILTRE=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("DDL_ACTIF"),
            #                           'MASQUE'),
            AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO", "NOEUD"),
        ),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
        #
        DDL_ACTIF=SIMP(statut="f", typ="TXM", max=6),
        # TODO : mettre en place le systeme de masques
        #           MASQUE          =SIMP(statut='f',typ='TXM',max=6),
    ),
    #        ------------------------------------------------------------------
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
