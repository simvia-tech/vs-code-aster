# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2024 - EDF R&D - www.code-aster.org
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


def proj_champ_prod(RESULTAT=None, CHAM_GD=None, METHODE=None, **args):
    if args.get("__all__"):
        return (corresp_2_mailla, resultat_sdaster, cham_no_sdaster, cham_elem)

    if not RESULTAT and not CHAM_GD:
        return corresp_2_mailla
    if RESULTAT:
        return AsType(RESULTAT)
    if CHAM_GD and METHODE == "SOUS_POINT":
        return cham_elem
    else:
        return AsType(CHAM_GD)


PROJ_CHAMP = OPER(
    nom="PROJ_CHAMP",
    op=166,
    sd_prod=proj_champ_prod,
    reentrant="f:RESULTAT",
    fr=tr("Projeter des champs d'un maillage sur un autre"),
    reuse=SIMP(statut="c", typ=CO),
    # faut-il projeter les champs ?
    PROJECTION=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    # pour projeter avec une sd_corresp_2_mailla deja calculée :
    MATR_PROJECTION=SIMP(statut="f", typ=corresp_2_mailla),
    # -----------------------------------------------------------------------------------------------------------
    # 1er cas : on fait tout d'un coup : creation de la sd_corresp_2_mailla + projection des champs
    # -----------------------------------------------------------------------------------------------
    b_1_et_2=BLOC(
        condition="""equal_to("PROJECTION", 'OUI') and not exists("MATR_PROJECTION")""",
        regles=(
            UN_PARMI("RESULTAT", "CHAM_GD"),
            UN_PARMI("MODELE_1", "MAILLAGE_1"),
            UN_PARMI("MODELE_2", "MAILLAGE_2"),
        ),
        RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        METHODE=SIMP(
            statut="f",
            typ="TXM",
            defaut="AUTO",
            into=("NUAGE_DEG_0", "NUAGE_DEG_1", "AUTO", "COLLOCATION", "ECLA_PG", "SOUS_POINT"),
        ),
        MODELE_1=SIMP(statut="f", typ=modele_sdaster),
        MAILLAGE_1=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
        MODELE_2=SIMP(statut="f", typ=modele_sdaster),
        MAILLAGE_2=SIMP(statut="f", typ=maillage_sdaster),
        # Cas de la projection NUAGE_DEG_0/1 :
        # --------------------------------------------
        b_nuage=BLOC(
            condition="""is_in("METHODE", ('NUAGE_DEG_0','NUAGE_DEG_1'))""",
            CHAM_NO_REFE=SIMP(statut="o", typ=cham_no_sdaster),
        ),
        # Cas de la projection COLLOCATION :
        # --------------------------------------------
        b_elem=BLOC(
            condition="""is_in("METHODE", ('COLLOCATION','ECLA_PG','AUTO'))""",
            CAS_FIGURE=SIMP(
                statut="f",
                typ="TXM",
                into=("2D", "3D", "2.5D", "1.5D"),
                fr=tr("Pour indiquer au programme le type de projection souhaité"),
            ),
            DISTANCE_MAX=SIMP(
                statut="f",
                typ="R",
                fr=tr(
                    "Distance maximale entre le noeud et l'élément le plus proche, lorsque le noeud n'est dans aucun élément."
                ),
            ),
            DISTANCE_ALARME=SIMP(statut="f", typ="R"),
            TRANSF_GEOM_1=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_1 avant la projection."
                ),
            ),
            TRANSF_GEOM_2=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_2 avant la projection."
                ),
            ),
            ALARME=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
            TYPE_CHAM=SIMP(
                statut="f",
                typ="TXM",
                into=("NOEU",),
                fr=tr("Pour forcer le type des champs projetés. NOEU -> cham_no"),
            ),
            PROL_ZERO=SIMP(
                statut="f",
                typ="TXM",
                into=("OUI", "NON"),
                defaut="NON",
                fr=tr(
                    "Pour prolonger les champs par zéro là ou la projection ne donne pas de valeurs."
                ),
            ),
        ),
        # Cas de la projection SOUS_POINT :
        # --------------------------------------------
        b_sous_point=BLOC(
            condition="""equal_to("METHODE", 'SOUS_POINT')""",
            CARA_ELEM=SIMP(statut="o", typ=cara_elem),
            TRANSF_GEOM_1=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_1 avant la projection."
                ),
            ),
            TRANSF_GEOM_2=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_2 avant la projection."
                ),
            ),
        ),
        # Cas de la projection d'une sd_resultat :
        # --------------------------------------------
        b_resultat=BLOC(
            condition="""exists("RESULTAT")""",
            regles=(
                EXCLUS(
                    "TOUT_ORDRE",
                    "NUME_ORDRE",
                    "INST",
                    "FREQ",
                    "LIST_INST",
                    "LIST_FREQ",
                    "LIST_ORDRE",
                ),
                EXCLUS("TOUT_CHAM", "NOM_CHAM"),
            ),
            NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
            TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CHAM=SIMP(
                statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
            ),
            NUME_DDL=SIMP(
                statut="f",
                typ=(nume_ddl_sdaster),
                fr=tr("Utile en dynamique pour pouvoir imposer la numérotation des cham_no."),
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
            b_acce_reel=BLOC(
                condition="""(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                b_prec_rela=BLOC(
                    condition="""(equal_to("CRITERE", 'RELATIF'))""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ),
                b_prec_abso=BLOC(
                    condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                    PRECISION=SIMP(statut="o", typ="R"),
                ),
            ),
        ),
        VIS_A_VIS=FACT(
            statut="f",
            max="**",
            regles=(
                AU_MOINS_UN("TOUT_1", "GROUP_MA_1", "MAILLE_1", "GROUP_NO_1"),
                AU_MOINS_UN("TOUT_2", "GROUP_MA_2", "GROUP_NO_2", "NOEUD_2"),
            ),
            TOUT_1=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE_1=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            TOUT_2=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD_2=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            # les mots clés suivants ne sont actifs que si METHODE='COLLOCATION' mais on ne peut pas le vérifier:
            CAS_FIGURE=SIMP(statut="f", typ="TXM", into=("2D", "3D", "2.5D", "1.5D", "0D")),
            TRANSF_GEOM_1=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_1 avant la projection."
                ),
            ),
            TRANSF_GEOM_2=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_2 avant la projection."
                ),
            ),
            b_0D=BLOC(
                condition="""equal_to("CAS_FIGURE",'0D')""",
                DISTANCE_0D=SIMP(
                    statut="o",
                    typ="R",
                    val_min=0,
                    fr=tr(
                        "Distance maximale entre un noeud et le noeud sur lequel il est projeté."
                    ),
                ),
            ),
        ),
    ),  # fin bloc b_1_et_2
    # -----------------------------------------------------------------------------------------------------------
    # 2eme cas : on s'arrete apres la creation de la sd_corresp_2_mailla
    # -----------------------------------------------------------------------------------------------
    b_1=BLOC(
        condition="""equal_to("PROJECTION", 'NON')""",
        METHODE=SIMP(statut="f", typ="TXM", defaut="COLLOCATION", into=("COLLOCATION", "COUPLAGE")),
        regles=(UN_PARMI("MODELE_1", "MAILLAGE_1"), UN_PARMI("MODELE_2", "MAILLAGE_2")),
        MODELE_1=SIMP(statut="f", typ=modele_sdaster),
        MAILLAGE_1=SIMP(statut="f", typ=maillage_sdaster),
        MODELE_2=SIMP(statut="f", typ=modele_sdaster),
        MAILLAGE_2=SIMP(statut="f", typ=maillage_sdaster),
        # Cas de la projection COLLOCATION :
        # --------------------------------------------
        b_elem=BLOC(
            condition="""is_in("METHODE", ('COLLOCATION',))""",
            CAS_FIGURE=SIMP(
                statut="f",
                typ="TXM",
                into=("2D", "3D", "2.5D", "1.5D"),
                fr=tr("Pour indiquer au programme le type de projection souhaité"),
            ),
            DISTANCE_MAX=SIMP(
                statut="f",
                typ="R",
                fr=tr(
                    "Distance maximale entre le noeud et l'élément le plus proche, lorsque le noeud n'est dans aucun élément."
                ),
            ),
            DISTANCE_ALARME=SIMP(statut="f", typ="R"),
            TRANSF_GEOM_1=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_1 avant la projection."
                ),
            ),
            TRANSF_GEOM_2=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_2 avant la projection."
                ),
            ),
            ALARME=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        ),
        VIS_A_VIS=FACT(
            statut="f",
            max="**",
            regles=(
                AU_MOINS_UN("TOUT_1", "GROUP_MA_1", "MAILLE_1", "GROUP_NO_1", "NOEUD_1"),
                AU_MOINS_UN("TOUT_2", "GROUP_MA_2", "GROUP_NO_2", "NOEUD_2"),
            ),
            TOUT_1=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE_1=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD_1=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            TOUT_2=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD_2=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            # les mots clés suivants ne sont actifs que si METHODE='COLLOCATION' mais on ne peut pas le vérifier:
            CAS_FIGURE=SIMP(statut="f", typ="TXM", into=("2D", "3D", "2.5D", "1.5D", "0D")),
            TRANSF_GEOM_1=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_1 avant la projection."
                ),
            ),
            TRANSF_GEOM_2=SIMP(
                statut="f",
                typ=(fonction_sdaster, nappe_sdaster, formule),
                min=2,
                max=3,
                fr=tr(
                    "2 (ou 3) fonctions fx,fy,fz définissant la transformation géométrique à appliquer"
                    " aux noeuds du MODELE_2 avant la projection."
                ),
            ),
        ),
    ),  # fin bloc b_1
    # -----------------------------------------------------------------------------------------------------------
    # 3eme cas : on projette les champs avec une sd_corresp_2_mailla déjà calculée
    # -----------------------------------------------------------------------------------------------
    b_2=BLOC(
        condition="""exists("MATR_PROJECTION")""",
        regles=(UN_PARMI("RESULTAT", "CHAM_GD"),),
        RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        TYPE_CHAM=SIMP(
            statut="f",
            typ="TXM",
            into=("NOEU",),
            fr=tr("Pour forcer le type des champs projetés. NOEU -> cham_no"),
        ),
        NUME_DDL=SIMP(
            statut="f",
            typ=(nume_ddl_sdaster),
            fr=tr("Parfois utile en dynamique pour pouvoir imposer la numérotation des cham_no."),
        ),
        # nécessaire si l'on projette des cham_elem :
        MODELE_2=SIMP(statut="f", typ=modele_sdaster),
        PROL_ZERO=SIMP(
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
            fr=tr(
                "Pour prolonger les champs par zéro là où la projection ne donne pas de valeurs."
            ),
        ),
        # Cas de la projection d'une sd_resultat :
        # --------------------------------------------
        b_resultat=BLOC(
            condition="""exists("RESULTAT")""",
            regles=(
                EXCLUS(
                    "TOUT_ORDRE",
                    "NUME_ORDRE",
                    "INST",
                    "FREQ",
                    "LIST_INST",
                    "LIST_FREQ",
                    "LIST_ORDRE",
                ),
                EXCLUS("TOUT_CHAM", "NOM_CHAM"),
            ),
            NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
            TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CHAM=SIMP(
                statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
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
            b_acce_reel=BLOC(
                condition="""(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                b_prec_rela=BLOC(
                    condition="""(equal_to("CRITERE", 'RELATIF'))""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ),
                b_prec_abso=BLOC(
                    condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                    PRECISION=SIMP(statut="o", typ="R"),
                ),
            ),
        ),
    ),  # fin bloc b_2
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
