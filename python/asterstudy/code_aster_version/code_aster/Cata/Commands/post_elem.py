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

# person_in_charge: josselin.delmas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def post_elem_prod(CARA_POUTRE, CARA_GEOM, **args):
    if args.get("__all__"):
        return (table_container, table_sdaster)

    if CARA_POUTRE is not None:
        return table_container
    elif CARA_GEOM is not None:
        return table_container
    else:
        return table_sdaster


POST_ELEM = OPER(
    nom="POST_ELEM",
    op=107,
    sd_prod=post_elem_prod,
    reentrant="n",
    fr=tr(
        "Calcul de quantités globales (masse, inerties, énergie, ...) sur tout ou partie du modèle"
    ),
    regles=(
        UN_PARMI(
            "MASS_INER",
            "ENER_POT",
            "ENER_CIN",
            "TRAV_EXT",
            "MINMAX",
            "WEIBULL",
            "RICE_TRACEY",
            "CARA_GEOM",
            "CHAR_LIMITE",
            "NORME",
            "CARA_POUTRE",
            "INDIC_ENER",
            "INDIC_SEUIL",
            "VOLUMOGRAMME",
            "AIRE_INTERNE",
            "ENER_ELAS",
            "ENER_ELTR",
            "ENER_TOTALE",
            "ENER_DISS",
            "INTEGRALE",
        ),
    ),
    MASS_INER=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        ORIG_INER=SIMP(statut="f", typ="R", min=3, max=3),
    ),
    b_mass_iner=BLOC(
        condition="""( exists("MASS_INER") )""",
        fr=tr("calcul de la masse, les inerties et le centre de gravité"),
        regles=(
            EXCLUS("CHAM_GD", "RESULTAT"),
            EXCLUS(
                "CHAM_GD",
                "TOUT_ORDRE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "NOEUD_CMP",
                "LIST_ORDRE",
                "LIST_INST",
                "LIST_FREQ",
                "NOM_CAS",
            ),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        GEOMETRIE=SIMP(statut="f", typ="TXM", defaut="INITIALE", into=("INITIALE", "DEFORMEE")),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(
            statut="f", typ=(mode_meca, evol_elas, evol_noli, mult_elas, fourier_elas, dyna_trans)
        ),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NUME_MODE=SIMP(statut="f", typ="I"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", min=2, validators=NoRepeat(), max=2),
        NOM_CAS=SIMP(statut="f", typ="TXM"),
    ),
    ENER_POT=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_pot=BLOC(
        condition="""( exists("ENER_POT") )""",
        fr=tr("calcul de l'énergie potentielle de déformation"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS(
                "TOUT_ORDRE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "NOEUD_CMP",
                "LIST_ORDRE",
                "LIST_INST",
                "LIST_FREQ",
                "NOM_CAS",
            ),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        ANGLE=SIMP(statut="f", typ="I", defaut=0),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(
            statut="f", typ=(mode_meca, evol_elas, evol_ther, evol_noli, dyna_trans, mult_elas)
        ),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    ),
    ENER_CIN=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("MASS_MECA", "MASS_MECA_DIAG"),
            defaut="MASS_MECA",
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_cin=BLOC(
        condition="""( exists("ENER_CIN") )""",
        fr=tr("calcul de l'énergie cinétique"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS(
                "TOUT_ORDRE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "NOEUD_CMP",
                "LIST_ORDRE",
                "LIST_INST",
                "LIST_FREQ",
                "NOM_CAS",
            ),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        ANGLE=SIMP(statut="f", typ="I", defaut=0),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(statut="f", typ=(mode_meca, evol_elas, evol_ther, evol_noli, dyna_trans)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    ),
    ENER_DISS=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_diss=BLOC(
        condition="""( exists("ENER_DISS") )""",
        fr=tr("calcul de l'énergie dissipée"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    ENER_ELAS=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_elas=BLOC(
        condition="""( exists("ENER_ELAS") )""",
        fr=tr("calcul de l'énergie de déformation élastique"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli, evol_elas)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    ENER_ELTR=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_eltr=BLOC(
        condition="""( exists("ENER_ELTR") )""",
        fr=tr("calcul de l'énergie de déformation élastique modifiée (traction)"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli, evol_elas)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    ENER_TOTALE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_ener_totale=BLOC(
        condition="""( exists("ENER_TOTALE") )""",
        fr=tr("calcul de l'énergie de déformation totale"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    INTEGRALE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"), UN_PARMI("NOM_CMP", "NOM_VARI")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        NOM_CHAM=SIMP(statut="f", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
        NOM_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_VARI=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        DEJA_INTEGRE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        TYPE_MAILLE=SIMP(statut="o", typ="TXM", into=("1D", "2D", "3D")),
    ),
    b_integrale=BLOC(
        condition="""( exists("INTEGRALE") )""",
        fr=tr("calcul de la moyenne d'une composante"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_ORDRE", "LIST_INST"),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        RESULTAT=SIMP(statut="f", typ=(evol_noli, evol_ther, evol_elas, evol_char)),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    VOLUMOGRAMME=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"), UN_PARMI("NB_INTERV", "SEUIL")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, max=1),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        TYPE_MAILLE=SIMP(statut="f", typ="TXM", into=("2D", "3D")),
        NOM_CHAM=SIMP(statut="f", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
        NOM_CMP=SIMP(statut="o", typ="TXM"),
        NB_INTERV=SIMP(statut="f", typ="I"),
        SEUIL=SIMP(statut="f", typ="R"),
        BORNES=SIMP(statut="f", typ="R", validators=NoRepeat(), min=2, max=2),
        NORME=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),
    b_volumogramme=BLOC(
        condition="""( exists("VOLUMOGRAMME") )""",
        fr=tr("calcul de la distribution du volume d'une structure vis-à-vis d'une composante"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_ORDRE", "LIST_INST"),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        RESULTAT=SIMP(statut="f", typ=(evol_noli, evol_ther, evol_elas, evol_char)),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    NORME=FACT(
        statut="f",
        max=1,
        fr=tr(
            "calcul des extrema en espace d'une CMP d'un champ, pour tous les instants spécifiés"
        ),
        regles=(
            UN_PARMI("TOUT", "GROUP_MA"),
            UN_PARMI("CHAM_GD", "RESULTAT"),
            PRESENT_PRESENT("CHAM_GD", "MODELE"),
            PRESENT_PRESENT("RESULTAT", "NOM_CHAM"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TYPE_MAILLE=SIMP(statut="f", typ="TXM", into=("2D", "3D")),
        TYPE_NORM=SIMP(statut="f", typ="TXM", into=("L2", "FROBENIUS")),
        RESULTAT=SIMP(statut="f", typ=(evol_noli, evol_ther, evol_elas)),
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=(
                "DEPL",
                "TEMP",
                "NEUT_R",
                "FLUX_ELGA",
                "FLUX_ELNO",
                "FLUX_NOEU",
                "EPSI_ELGA",
                "EPSI_ELNO",
                "EPSI_NOEU",
                "SIEF_ELGA",
                "SIEF_ELNO",
                "SIEF_NOEU",
            ),
        ),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        b_norme_GD=BLOC(
            condition="""( exists("CHAM_GD") )""", COEF_MULT=SIMP(statut="f", typ="R", max=30)
        ),
        b_norme=BLOC(
            condition="""( exists("RESULTAT") )""",
            regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        ),
    ),
    MINMAX=FACT(
        statut="f",
        max="**",
        fr=tr(
            "calcul des extrema en espace d'une CMP d'un champ, pour tous les instants spécifiés"
        ),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            PRESENT_PRESENT("CHAM_GD", "MODELE"),
            PRESENT_PRESENT("RESULTAT", "NOM_CHAM"),
            UN_PARMI("TOUT", "GROUP_MA"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        RESULTAT=SIMP(statut="f", typ=(evol_noli, evol_ther, evol_elas)),
        NOM_CHAM=SIMP(statut="f", typ="TXM", into=C_NOM_CHAM_INTO()),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        NOM_CMP=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**"),
        b_minmax=BLOC(
            condition="""( exists("RESULTAT") )""",
            regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        ),
    ),
    WEIBULL=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("SIGM_ELGA", "SIGM_ELMOY"),
            defaut="SIGM_ELGA",
        ),
        CORR_PLAST=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        COEF_MULT=SIMP(statut="f", typ="R", defaut=1.0),
    ),
    b_weibull=BLOC(
        condition="""( exists("WEIBULL") )""",
        fr=tr("calcul du champ élémentaire de la puissance m-ième de la contrainte de Weibull"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(statut="f", typ=(evol_noli)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    RICE_TRACEY=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("SIGM_ELGA", "SIGM_ELMOY"),
            defaut="SIGM_ELGA",
        ),
        LOCAL=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
    b_rice_tracey=BLOC(
        condition="""( exists("RICE_TRACEY") )""",
        fr=tr("calcul du taux de croissance d'une cavité sphérique par rapport à un domaine"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),
        ),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        NUME_COUCHE=SIMP(statut="f", typ="I", defaut=1),
        NIVE_COUCHE=SIMP(statut="f", typ="TXM", defaut="MOY", into=("INF", "SUP", "MOY")),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(statut="f", typ=(evol_noli)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    INDIC_ENER=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_indic_ener=BLOC(
        condition="""( exists("INDIC_ENER") )""",
        fr=tr("calcul un indicateur global de perte de proportionnalité du chargement"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    INDIC_SEUIL=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_indic_seuil=BLOC(
        condition="""( exists("INDIC_SEUIL") )""",
        fr=tr("calcul un indicateur global de perte de proportionnalité du chargement"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    CHAR_LIMITE=FACT(
        statut="f", min=0, CHAR_CSTE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON")
    ),
    b_char_limite=BLOC(
        condition="""( exists("CHAR_LIMITE") )""",
        fr=tr("post-traitement du calcul de la charge limite"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        RESULTAT=SIMP(statut="o", typ=(evol_noli)),
        regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST"),),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    CARA_GEOM=FACT(
        statut="f",
        max="**",
        regles=(AU_MOINS_UN("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SYME_X=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        SYME_Y=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        ORIG_INER=SIMP(statut="f", typ="R", min=2, max=2),
    ),
    b_cara_geom=BLOC(
        condition="""( exists("CARA_GEOM") )""",
        fr=tr("calcul des caractéristiques géométriques d'un section de poutre"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
    ),
    CARA_POUTRE=FACT(
        statut="f",
        regles=(UN_PARMI("TOUT", "GROUP_MA"), ENSEMBLE("LONGUEUR", "LIAISON", "MATERIAU")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_MA_INTE=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        CARA_GEOM=SIMP(statut="o", typ=table_sdaster),
        RT=SIMP(statut="f", typ="R"),
        LAPL_PHI=SIMP(statut="f", typ=evol_ther),
        LAPL_PHI_Y=SIMP(statut="f", typ=evol_ther),
        LAPL_PHI_Z=SIMP(statut="f", typ=evol_ther),
        LIAISON=SIMP(statut="f", typ="TXM", into=("ROTULE", "ENCASTREMENT")),
        LONGUEUR=SIMP(statut="f", typ="R"),
        MATERIAU=SIMP(statut="f", typ=mater_sdaster),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("CARA_TORSION", "CARA_CISAILLEMENT", "CARA_GAUCHI"),
        ),
    ),
    b_cara_poutre=BLOC(
        condition="""( exists("CARA_POUTRE") )""",
        fr=tr("calcul des caractéristiques mécaniques d'un section de poutre"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
    ),
    AIRE_INTERNE=FACT(
        statut="f",
        max="**",
        GROUP_MA_BORD=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
    ),
    b_aire_interne=BLOC(
        condition="""( exists("AIRE_INTERNE") )""",
        fr=tr("calcul de l'aire d'un trou dans un maillage 2D"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
    ),
    TRAV_EXT=FACT(statut="f"),
    b_trav_ext=BLOC(
        condition="""( exists("TRAV_EXT") )""",
        fr=tr("calcul du travail des efforts extérieurs"),
        RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli, dyna_trans)),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
