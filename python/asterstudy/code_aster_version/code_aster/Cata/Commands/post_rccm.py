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

# person_in_charge: sarah.plessis at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_RCCM = OPER(
    nom="POST_RCCM",
    op=165,
    sd_prod=table_sdaster,
    fr=tr("Vérification des critères de niveau 0 et certains critères de niveau A du RCC-M"),
    reentrant="n",
    TYPE_RESU=SIMP(
        statut="f", typ="TXM", defaut="VALE_MAX", into=("VALE_MAX", "DETAILS", "SYSTUS")
    ),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
    TYPE_RESU_MECA=SIMP(
        statut="o", typ="TXM", into=("EVOLUTION", "ZE200a", "ZE200b", "B3200", "B3600")
    ),
    AXIS=SIMP(
        statut="f",
        typ="TXM",
        defaut="NON",
        into=("NON", "OUI"),
        fr=tr("Indiquer si le modèle est axisymétrique"),
    ),
    # ======================================================================
    b_evolution=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'EVOLUTION') and not equal_to("TYPE_RESU","SYSTUS")""",
        OPTION=SIMP(
            statut="o",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            into=("PM_PB", "SN", "FATIGUE_ZH210", "AMORCAGE"),
        ),
        MATER=SIMP(statut="o", typ=mater_sdaster),
        SY_MAX=SIMP(
            statut="f",
            typ="R",
            fr=tr("limite élastique utilisée pour le calcul du rochet thermique"),
        ),
        TYPE_KE=SIMP(
            statut="f",
            typ="TXM",
            defaut="KE_MECA",
            into=("KE_MECA", "KE_MIXTE"),
            fr=tr("Ke meca seul ou partition mecanique + thermique"),
        ),
        RAYON_MOYEN=SIMP(
            statut="f", typ="R", defaut=-1.0, fr=tr("La courbure attribuées à la ligne coupe")
        ),
        TRANSITOIRE=FACT(
            statut="o",
            max="**",
            fr=tr("transitoire à dépouiller"),
            regles=(
                UN_PARMI("TOUT_ORDRE", "INST", "LIST_INST", "TOUT_INST"),
                UN_PARMI("TABL_RESU_MECA", "TABL_SIGM_THETA"),
            ),
            NB_OCCUR=SIMP(
                statut="f",
                typ="I",
                defaut=1,
                fr=tr("nombre d occurences réelles de ce transitoire"),
            ),
            TABL_RESU_MECA=SIMP(
                statut="f", typ=table_sdaster, fr=tr("relevé des contraintes sur le chemin")
            ),
            TABL_SIGM_THER=SIMP(
                statut="f", typ=table_sdaster, fr=tr("résultat sous chargement thermique seul")
            ),
            TABL_RESU_PRES=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes sous chargement de pression"),
            ),
            TABL_SIGM_THETA=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr(
                    "table relevé des contraintes a la distance d de la singularité pour chacun des angles THETA"
                ),
            ),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            TOUT_INST=SIMP(statut="f", typ="TXM", into=("OUI",)),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            b_inst=BLOC(
                condition="""(exists("INST")) or (exists("LIST_INST"))""",
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
    ),
    # ======================================================================
    b_ze200=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'ZE200a') or equal_to("TYPE_RESU_MECA", 'ZE200b')""",
        OPTION=SIMP(statut="o", typ="TXM", max=1, into=("SN", "FATIGUE", "EFAT")),
        SOUS_CYCL=SIMP(
            statut="f",
            typ="TXM",
            defaut="NON",
            into=("OUI", "NON"),
            fr=tr("Prise en compte des sous cycles"),
        ),
        METHODE=SIMP(
            statut="f",
            typ="TXM",
            defaut="TRESCA",
            into=("TRESCA", "TOUT_INST"),
            fr=tr("Méthode de sélection des instants"),
        ),
        MATER=SIMP(statut="o", typ=mater_sdaster),
        SY_MAX=SIMP(
            statut="f",
            typ="R",
            fr=tr("limite élastique utilisée pourle calcul du rochet thermique"),
        ),
        TYPE_KE=SIMP(
            statut="f",
            typ="TXM",
            defaut="KE_MECA",
            into=("KE_MECA", "KE_MIXTE"),
            fr=tr("Ke meca seul ou partition mecanique + thermique"),
        ),
        CHAR_MECA=FACT(
            statut="o",
            max="**",
            fr=tr("Chargements mécaniques"),
            regles=(UN_PARMI("MX", "MX_TUBU"),),
            NUME_CHAR=SIMP(statut="o", typ="I", fr=tr("numéro du chargement")),
            NOM_CHAR=SIMP(statut="f", typ="TXM", fr=tr("nom du chargement")),
            MX=SIMP(statut="f", typ="R", fr=tr("moment suivant x")),
            MX_TUBU=SIMP(statut="f", typ="R", fr=tr("moment suivant x, tubulure")),
            b_1_tenseur=BLOC(
                condition="""exists("MX")""",
                MY=SIMP(statut="o", typ="R", fr=tr("moment suivant y")),
                MZ=SIMP(statut="o", typ="R", fr=tr("moment suivant z")),
            ),
            b_2_tenseurs=BLOC(
                condition="""exists("MX_TUBU")""",
                MY_TUBU=SIMP(statut="o", typ="R", fr=tr("moment suivant y, tubulure")),
                MZ_TUBU=SIMP(statut="o", typ="R", fr=tr("moment suivant z, tubulure")),
                MX_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant x, corps du piquage")),
                MY_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant y, corps du piquage")),
                MZ_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant z, corps du piquage")),
            ),
        ),
        INDI_SIGM=FACT(
            statut="o",
            max=1,
            fr=tr("indices de contraintes"),
            regles=(UN_PARMI("C2", "C2_TUBU"),),
            C1=SIMP(statut="o", typ="R", fr=tr("indice de contraintes C1 du RCCM")),
            K1=SIMP(statut="o", typ="R", fr=tr("indice de contraintes K1 du RCCM")),
            C3=SIMP(statut="o", typ="R", fr=tr("indice de contraintes C3 du RCCM")),
            K3=SIMP(statut="o", typ="R", fr=tr("indice de contraintes K3 du RCCM")),
            C2=SIMP(statut="f", typ="R", fr=tr("indice de contraintes C2 du RCCM")),
            C2_TUBU=SIMP(statut="f", typ="R", fr=tr("indice C2 du RCCM (tubulure)")),
            K2=SIMP(statut="f", typ="R", fr=tr("indice de contraintes K2 du RCCM")),
            K2_TUBU=SIMP(statut="f", typ="R", fr=tr("indice K2 du RCCM (tubulure)")),
            C2_CORP=SIMP(statut="f", typ="R", fr=tr("indice C2 du RCCM (corps)")),
            K2_CORP=SIMP(statut="f", typ="R", fr=tr("indice K2 du RCCM (corps)")),
        ),
        TUYAU=FACT(
            statut="o",
            max=1,
            fr=tr("caracteristiques geometriques de la tuyauterie"),
            regles=(UN_PARMI("I", "I_TUBU"),),
            R=SIMP(statut="o", typ="R", fr=tr("rayon de la tuyauterie")),
            R_TUBU=SIMP(statut="f", typ="R", fr=tr("rayon de la tubulure")),
            R_CORP=SIMP(statut="f", typ="R", fr=tr("rayon du corps")),
            EP=SIMP(statut="o", typ="R", fr=tr("epaisseur de la tuyauterie")),
            I=SIMP(statut="f", typ="R", fr=tr("inertie de la tuyauterie")),
            I_TUBU=SIMP(statut="f", typ="R", fr=tr("inertie de la tubulure")),
            I_CORP=SIMP(statut="f", typ="R", fr=tr("inertie du corps")),
        ),
        RESU_THER=FACT(
            statut="f",
            max="**",
            fr=tr("resultats thermiques"),
            NUME_RESU_THER=SIMP(
                statut="o", typ="I", fr=tr("numéro de la table de résultat thermique")
            ),
            TABL_RESU_THER=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes sous chargement thermique seul"),
            ),
        ),
        ENVIRONNEMENT=FACT(
            statut="f",
            max=1,
            fr=tr("Donnees pour le calcul du fen"),
            TABL_YOUNG=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé du module d'young en fonction de la température"),
            ),
            FEN_INTEGRE=SIMP(statut="o", typ="R"),
            S_ETOILE=SIMP(statut="o", typ="R"),
            SEUIL_EPSI_INF=SIMP(statut="o", typ="R", fr=tr("seuil en %/s")),
            SEUIL_EPSI_SUP=SIMP(statut="o", typ="R", fr=tr("seuil en %/s")),
            CRIT_EPSI=SIMP(statut="o", typ="R", fr=tr("seuil en %")),
            A_ENV=SIMP(statut="o", typ="R"),
            B_ENV=SIMP(statut="o", typ="R"),
            C_ENV=SIMP(statut="o", typ="R"),
            SEUIL_T_INF=SIMP(statut="o", typ="R", fr=tr("seuil en degré")),
            SEUIL_T_SUP=SIMP(statut="o", typ="R", fr=tr("seuil en degré")),
            VALE_T_INF=SIMP(
                statut="o", typ="R", fr=tr("valeur inférieure de la température en degré")
            ),
            VALE_T_SUP=SIMP(
                statut="o", typ="R", fr=tr("valeur supérieure de la température en degré")
            ),
            VALE_T_MOY_NUM=SIMP(
                statut="o",
                typ="R",
                fr=tr("valeur moyenne au numérateur de la température en degré"),
            ),
            VALE_T_MOY_DEN=SIMP(
                statut="o",
                typ="R",
                fr=tr("valeur moyenne au dénominateur de la température en degré"),
            ),
        ),
        SEISME=FACT(
            statut="f",
            max=1,
            fr=tr("Situation séisme"),
            NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
            NB_CYCL_SEISME=SIMP(statut="o", typ="I", fr=tr("nombre de cycles associé au séisme")),
            NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
            NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
            CHAR_ETAT=SIMP(statut="o", typ="I", max=1, fr=tr("numero du chargement etat S")),
        ),
    ),
    b_ze200a=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'ZE200a')""",
        SITUATION=FACT(
            statut="o",
            max="**",
            fr=tr("Situation"),
            NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
            NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
            NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
            COMBINABLE=SIMP(
                statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON"), fr=tr("non = sous-cycle")
            ),
            NUME_GROUPE=SIMP(
                statut="o",
                typ="I",
                min=1,
                max=20,
                fr=tr("numéro du ou des groupes de la situation"),
            ),
            NUME_PASSAGE=SIMP(
                statut="f",
                typ="I",
                min=2,
                max=20,
                fr=tr("numéros des groupes de la situation de passage"),
            ),
            NUME_PARTAGE=SIMP(
                statut="f", typ="I", min=1, max=1, fr=tr("numéro du groupe de partage")
            ),
            NUME_RESU_THER=SIMP(
                statut="f", typ="I", max=1, fr=tr("numéro du transitoire thermique")
            ),
            CHAR_ETAT_A=SIMP(statut="o", typ="I", max=1, fr=tr("numero du chargement etat A")),
            CHAR_ETAT_B=SIMP(statut="o", typ="I", max=1, fr=tr("numero du chargement etat B")),
            PRES_A=SIMP(statut="o", typ="R", fr=tr("pression etat A")),
            PRES_B=SIMP(statut="o", typ="R", fr=tr("pression etat B")),
            O_ETOILE=SIMP(statut="f", typ="R"),
            TABL_TEMP=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des températures pendant le transitoire"),
            ),
        ),
    ),
    b_ze200b=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'ZE200b')""",
        RESU_PRES=FACT(
            statut="f",
            max="**",
            fr=tr("resultats dus à la pression"),
            NUME_RESU_PRES=SIMP(
                statut="o", typ="I", fr=tr("numéro de la table de transitoire de pression")
            ),
            TABL_RESU_PRES=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes dues à la pression"),
            ),
        ),
        SITUATION=FACT(
            statut="o",
            max="**",
            fr=tr("Situation"),
            NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
            NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
            NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
            COMBINABLE=SIMP(
                statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON"), fr=tr("non = sous-cycle")
            ),
            NUME_GROUPE=SIMP(
                statut="o",
                typ="I",
                min=1,
                max=20,
                fr=tr("numéro du ou des groupes de la situation"),
            ),
            NUME_PASSAGE=SIMP(
                statut="f",
                typ="I",
                min=2,
                max=20,
                fr=tr("numéros des groupes de la situation de passage"),
            ),
            NUME_PARTAGE=SIMP(
                statut="f", typ="I", min=1, max=1, fr=tr("numéro du groupe de partage")
            ),
            NUME_RESU_THER=SIMP(
                statut="f", typ="I", max=1, fr=tr("numero du transitoire thermique")
            ),
            NUME_RESU_PRES=SIMP(
                statut="f", typ="I", max=1, fr=tr("numero du transitoire de pression")
            ),
            CHAR_ETAT_A=SIMP(statut="o", typ="I", max=1, fr=tr("numero du chargement etat A")),
            CHAR_ETAT_B=SIMP(statut="o", typ="I", max=1, fr=tr("numero du chargement etat B")),
            O_ETOILE=SIMP(statut="f", typ="R"),
            TABL_TEMP=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des températures pendant le transitoire"),
            ),
        ),
    ),
    # ======================================================================
    b_b3200=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'B3200')""",
        OPTION=SIMP(statut="o", typ="TXM", max=1, into=("PM_PB", "SN", "FATIGUE", "EFAT")),
        METHODE=SIMP(
            statut="f",
            typ="TXM",
            defaut="TRESCA",
            into=("TRESCA", "TOUT_INST"),
            fr=tr("Méthode de sélection des instants"),
        ),
        SOUS_CYCL=SIMP(
            statut="f",
            typ="TXM",
            defaut="NON",
            into=("OUI", "NON"),
            fr=tr("Prise en compte des sous cycles"),
        ),
        MATER=SIMP(statut="o", typ=mater_sdaster),
        SY_MAX=SIMP(
            statut="f",
            typ="R",
            fr=tr("limite élastique utilisée pourle calcul du rochet thermique"),
        ),
        TYPE_KE=SIMP(
            statut="f",
            typ="TXM",
            defaut="KE_MECA",
            into=("KE_MECA", "KE_MIXTE"),
            fr=tr("Ke meca seul ou partition mecanique + thermique"),
        ),
        FACT_SIGM=FACT(
            statut="f",
            max=1,
            fr=tr("facteurs d'intensité de contraintes (soudure)"),
            KT_SN=SIMP(statut="f", typ="R", fr=tr("Kt appliqué à Sn")),
            KT_SP=SIMP(statut="f", typ="R", fr=tr("Kt appliqué à Sp")),
        ),
        INDI_SIGM=FACT(
            statut="f",
            max=1,
            fr=tr("indices de contraintes"),
            C1=SIMP(statut="o", typ="R", fr=tr("indice de contraintes C1 du RCCM")),
            K1=SIMP(statut="o", typ="R", fr=tr("indice de contraintes K1 du RCCM")),
            C2=SIMP(statut="o", typ="R", fr=tr("indice de contraintes C2 du RCCM")),
            K2=SIMP(statut="o", typ="R", fr=tr("indice de contraintes K2 du RCCM")),
            C3=SIMP(statut="o", typ="R", fr=tr("indice de contraintes C3 du RCCM")),
            K3=SIMP(statut="o", typ="R", fr=tr("indice de contraintes K3 du RCCM")),
        ),
        regles=(ENSEMBLE("CHAR_MECA", "RESU_MECA_UNIT"),),
        CHAR_MECA=FACT(
            statut="f",
            max="**",
            fr=tr("Chargements mécaniques"),
            regles=(UN_PARMI("MX", "MX_TUBU"),),
            NUME_CHAR=SIMP(statut="o", typ="I", fr=tr("numéro du chargement")),
            NOM_CHAR=SIMP(statut="f", typ="TXM", fr=tr("nom du chargement")),
            MX=SIMP(statut="f", typ="R", fr=tr("moment suivant x")),
            MX_TUBU=SIMP(statut="f", typ="R", fr=tr("moment suivant x, tubulure")),
            b_1_tenseur=BLOC(
                condition="""exists("MX")""",
                FX=SIMP(statut="f", typ="R", fr=tr("effort suivant x")),
                FY=SIMP(statut="f", typ="R", fr=tr("effort suivant y")),
                FZ=SIMP(statut="f", typ="R", fr=tr("effort suivant z")),
                MY=SIMP(statut="o", typ="R", fr=tr("moment suivant y")),
                MZ=SIMP(statut="o", typ="R", fr=tr("moment suivant z")),
            ),
            b_2_tenseurs=BLOC(
                condition="""exists("MX_TUBU")""",
                FX_TUBU=SIMP(statut="f", typ="R", fr=tr("effort suivant x, tubulure")),
                FY_TUBU=SIMP(statut="f", typ="R", fr=tr("effort suivant y, tubulure")),
                FZ_TUBU=SIMP(statut="f", typ="R", fr=tr("effort suivant z, tubulure")),
                MY_TUBU=SIMP(statut="o", typ="R", fr=tr("moment suivant y, tubulure")),
                MZ_TUBU=SIMP(statut="o", typ="R", fr=tr("moment suivant z, tubulure")),
                FX_CORP=SIMP(statut="f", typ="R", fr=tr("effort suivant x, corps du piquage")),
                FY_CORP=SIMP(statut="f", typ="R", fr=tr("effort suivant y, corps du piquage")),
                FZ_CORP=SIMP(statut="f", typ="R", fr=tr("effort suivant z, corps du piquage")),
                MX_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant x, corps du piquage")),
                MY_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant y, corps du piquage")),
                MZ_CORP=SIMP(statut="o", typ="R", fr=tr("moment suivant z, corps du piquage")),
            ),
        ),
        RESU_MECA_UNIT=FACT(
            statut="f",
            fr=tr("resultats mécaniques unitaires"),
            regles=(UN_PARMI("TABL_MX", "TABL_MX_TUBU"),),
            TABL_MX=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes pour chargement unitaire MX"),
            ),
            TABL_MX_TUBU=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes pour chargement unitaire MX_TUBU"),
            ),
            b_1_tenseur=BLOC(
                condition="""exists("TABL_MX")""",
                TABL_FX=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FX"),
                ),
                TABL_FY=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FY"),
                ),
                TABL_FZ=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FZ"),
                ),
                TABL_MY=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MY"),
                ),
                TABL_MZ=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MZ"),
                ),
            ),
            b_2_tenseurs=BLOC(
                condition="""exists("TABL_MX_TUBU")""",
                TABL_FX_TUBU=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FX_TUBU"),
                ),
                TABL_FY_TUBU=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FY_TUBU"),
                ),
                TABL_FZ_TUBU=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FZ_TUBU"),
                ),
                TABL_MY_TUBU=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MY_TUBU"),
                ),
                TABL_MZ_TUBU=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MZ_TUBU"),
                ),
                TABL_FX_CORP=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FX_CORP"),
                ),
                TABL_FY_CORP=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FY_CORP"),
                ),
                TABL_FZ_CORP=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire FZ_CORP"),
                ),
                TABL_MX_CORP=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MX_CORP"),
                ),
                TABL_MY_CORP=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MY_CORP"),
                ),
                TABL_MZ_CORP=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des contraintes pour chargement unitaire MZ_CORP"),
                ),
            ),
            TABL_PRES=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes pour chargement unitaire de pression"),
            ),
        ),
        RESU_THER=FACT(
            statut="f",
            max="**",
            fr=tr("resultats thermiques"),
            NUME_RESU_THER=SIMP(
                statut="o", typ="I", fr=tr("numéro de la table de résultat thermique")
            ),
            TABL_RESU_THER=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes sous chargement thermique seul"),
            ),
        ),
        RESU_PRES=FACT(
            statut="f",
            max="**",
            fr=tr("resultats dus à la pression"),
            NUME_RESU_PRES=SIMP(
                statut="o", typ="I", fr=tr("numéro de la table de transitoire de pression")
            ),
            TABL_RESU_PRES=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé des contraintes dues à la pression"),
            ),
        ),
        RESU_MECA=FACT(
            statut="f",
            max="**",
            fr=tr("resultats dus aux efforts externes"),
            NUME_RESU_MECA=SIMP(
                statut="o", typ="I", fr=tr("numéro de la table de transitoire dus aux efforts")
            ),
            TABL_RESU_MECA=SIMP(statut="o", typ=table_sdaster),
        ),
        SITUATION=FACT(
            statut="o",
            max="**",
            fr=tr("Situation"),
            NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
            NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
            NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
            COMBINABLE=SIMP(
                statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON"), fr=tr("non = sous-cycle")
            ),
            NUME_GROUPE=SIMP(
                statut="o",
                typ="I",
                min=1,
                max=20,
                fr=tr("numéro du ou des groupes de la situation"),
            ),
            NUME_PASSAGE=SIMP(
                statut="f",
                typ="I",
                min=2,
                max=20,
                fr=tr("numéros des groupes de la situation de passage"),
            ),
            NUME_PARTAGE=SIMP(
                statut="f", typ="I", min=1, max=1, fr=tr("numéro du groupe de partage")
            ),
            NUME_RESU_THER=SIMP(
                statut="f", typ="I", max=1, fr=tr("numero du transitoire thermique")
            ),
            regles=(
                UN_PARMI("CHAR_ETAT_A", "NUME_RESU_MECA"),
                PRESENT_ABSENT("PRES_A", "NUME_RESU_PRES"),
                ENSEMBLE("PRES_A", "PRES_B"),
                ENSEMBLE("CHAR_ETAT_A", "CHAR_ETAT_B"),
                PRESENT_PRESENT("TEMP_A", "TABL_TEMP"),
                PRESENT_PRESENT("O_ETOILE", "TABL_TEMP"),
                ENSEMBLE("TEMP_A", "TEMP_B"),
            ),
            NUME_RESU_PRES=SIMP(
                statut="f", typ="I", max=1, fr=tr("numero du transitoire de pression")
            ),
            NUME_RESU_MECA=SIMP(
                statut="f", typ="I", max=1, fr=tr("numero du transitoire dus aux efforts")
            ),
            CHAR_ETAT_A=SIMP(statut="f", typ="I", max=1, fr=tr("numero du chargement etat A")),
            CHAR_ETAT_B=SIMP(statut="f", typ="I", max=1, fr=tr("numero du chargement etat B")),
            PRES_A=SIMP(statut="f", typ="R", fr=tr("pression etat A")),
            PRES_B=SIMP(statut="f", typ="R", fr=tr("pression etat B")),
            O_ETOILE=SIMP(statut="f", typ="R"),
            TABL_TEMP=SIMP(
                statut="f",
                typ=table_sdaster,
                fr=tr("table relevé des températures pendant le transitoire"),
            ),
            TEMP_A=SIMP(statut="f", typ="R", fr=tr("temperature de CHAR ETAT A")),
            TEMP_B=SIMP(statut="f", typ="R", fr=tr("temperature de CHAR ETAT B")),
        ),
        ENVIRONNEMENT=FACT(
            statut="f",
            max=1,
            fr=tr("Donnees pour le calcul du fen"),
            TABL_YOUNG=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("table relevé du module d'young en fonction de la température"),
            ),
            FEN_INTEGRE=SIMP(statut="o", typ="R"),
            S_ETOILE=SIMP(statut="o", typ="R"),
            SEUIL_EPSI_INF=SIMP(statut="o", typ="R", fr=tr("seuil en %/s")),
            SEUIL_EPSI_SUP=SIMP(statut="o", typ="R", fr=tr("seuil en %/s")),
            CRIT_EPSI=SIMP(statut="o", typ="R", fr=tr("seuil en %")),
            A_ENV=SIMP(statut="o", typ="R"),
            B_ENV=SIMP(statut="o", typ="R"),
            C_ENV=SIMP(statut="o", typ="R"),
            SEUIL_T_INF=SIMP(statut="o", typ="R", fr=tr("seuil en degré")),
            SEUIL_T_SUP=SIMP(statut="o", typ="R", fr=tr("seuil en degré")),
            VALE_T_INF=SIMP(
                statut="o", typ="R", fr=tr("valeur inférieure de la température en degré")
            ),
            VALE_T_SUP=SIMP(
                statut="o", typ="R", fr=tr("valeur supérieure de la température en degré")
            ),
            VALE_T_MOY_NUM=SIMP(
                statut="o",
                typ="R",
                fr=tr("valeur moyenne au numérateur de la température en degré"),
            ),
            VALE_T_MOY_DEN=SIMP(
                statut="o",
                typ="R",
                fr=tr("valeur moyenne au dénominateur de la température en degré"),
            ),
        ),
        SEISME=FACT(
            statut="f",
            max=1,
            fr=tr("Situation séisme"),
            NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
            NB_CYCL_SEISME=SIMP(statut="o", typ="I", fr=tr("nombre de cycles associé au séisme")),
            NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
            NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
            regles=(
                UN_PARMI("CHAR_ETAT", "TABL_MX"),
                ENSEMBLE("TABL_MX", "TABL_MY", "TABL_MZ", "TABL_FX", "TABL_FY", "TABL_FZ"),
            ),
            CHAR_ETAT=SIMP(statut="f", typ="I", max=1, fr=tr("numero de chargement etat S")),
            TABL_FX=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme FX")
            ),
            TABL_FY=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme FY")
            ),
            TABL_FZ=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme FZ")
            ),
            TABL_MX=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme MX")
            ),
            TABL_MY=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme MY")
            ),
            TABL_MZ=SIMP(
                statut="f", typ=table_sdaster, fr=tr("table relevé des contraintes pour séisme MZ")
            ),
        ),
    ),
    # ======================================================================
    b_tuyauterie=BLOC(
        condition="""equal_to("TYPE_RESU_MECA", 'B3600') and not equal_to("TYPE_RESU","SYSTUS")""",
        OPTION=SIMP(statut="o", typ="TXM", into=("FATIGUE", "MOMENT_EQUIVALENT")),
        ZONE_ANALYSE=FACT(
            statut="o",
            fr=tr("liste des mailles ou des noeuds analysés"),
            regles=(UN_PARMI("TOUT", "GROUP_MA"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        ),
        b_momeq=BLOC(
            condition="""equal_to("OPTION", 'MOMENT_EQUIVALENT')""",
            RESU_MECA=FACT(
                statut="o",
                max=1,
                fr=tr("Chargements mécaniques"),
                regles=(UN_PARMI("CHAM_GD", "RESULTAT"),),
                CHAM_GD=SIMP(statut="f", typ=cham_elem),
                RESULTAT=SIMP(statut="f", typ=(resultat_sdaster)),
                b_extrac=BLOC(
                    condition="""exists("RESULTAT")""",
                    fr=tr("extraction d un champ de grandeur"),
                    regles=(UN_PARMI("TOUT_ORDRE", "NUME_ORDRE", "INST"),),
                    NOM_CHAM=SIMP(statut="f", typ="TXM", defaut="EFGE_ELNO", into=("EFGE_ELNO",)),
                    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                    NUME_ORDRE=SIMP(statut="f", typ="I", max="**"),
                    INST=SIMP(statut="f", typ="R", max="**"),
                    b_acce_reel=BLOC(
                        condition="""(exists("INST"))""",
                        CRITERE=SIMP(
                            statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                        ),
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
            ),
        ),
        b_fatigue=BLOC(
            condition="""equal_to("OPTION", 'FATIGUE')""",
            CHAM_MATER=SIMP(statut="o", typ=cham_mater),
            TYPE_KE=SIMP(
                statut="f",
                typ="TXM",
                defaut="KE_MECA",
                into=("KE_MECA", "KE_MIXTE"),
                fr=tr("Ke meca seul ou partition mecanique + thermique"),
            ),
            MODELE=SIMP(statut="o", typ=modele_sdaster),
            CARA_ELEM=SIMP(statut="o", typ=cara_elem),
            RESU_MECA=FACT(
                statut="o",
                max="**",
                fr=tr("Chargements mécaniques"),
                regles=(UN_PARMI("CHAM_GD", "RESULTAT"),),
                NUME_CHAR=SIMP(statut="o", typ="I", fr=tr("numéro du chargement")),
                NOM_CHAR=SIMP(statut="f", typ="TXM", fr=tr("nom du chargement")),
                CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
                RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
                b_extrac=BLOC(
                    condition="""exists("RESULTAT")""",
                    fr=tr("extraction d un champ de grandeur"),
                    regles=(UN_PARMI("TOUT_ORDRE", "NUME_ORDRE", "INST", "NOEUD_CMP", "NOM_CAS"),),
                    NOM_CHAM=SIMP(statut="o", typ="TXM", into=("EFGE_ELNO", "SIEF_ELNO")),
                    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                    NUME_ORDRE=SIMP(statut="f", typ="I"),
                    INST=SIMP(statut="f", typ="R"),
                    NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                    NOM_CAS=SIMP(statut="f", typ="TXM"),
                    b_acce_reel=BLOC(
                        condition="""(exists("INST"))""",
                        CRITERE=SIMP(
                            statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                        ),
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
            ),
            INDI_SIGM=FACT(
                statut="o",
                max="**",
                fr=tr("indices de contraintes"),
                regles=(UN_PARMI("TOUT", "GROUP_MA"),),
                C1=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("indice de contraintes C1 du RCCM")),
                K1=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("indice de contraintes K1 du RCCM")),
                C2=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("indice de contraintes C2 du RCCM")),
                K2=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("indice de contraintes K2 du RCCM")),
                C3=SIMP(statut="f", typ="R", defaut=0.5, fr=tr("indice de contraintes C3 du RCCM")),
                K3=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("indice de contraintes K3 du RCCM")),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_MA=SIMP(
                    statut="f",
                    typ=grma,
                    validators=NoRepeat(),
                    max="**",
                    fr=tr("groupe(s) de mailles ou sont affectés les indices de contraintes"),
                ),
                MAILLE=SIMP(
                    statut="c",
                    typ=ma,
                    validators=NoRepeat(),
                    max="**",
                    fr=tr("liste des mailles ou sont affectés les indices de contraintes"),
                ),
                b_grma=BLOC(
                    condition="""(exists("GROUP_MA"))or(exists("MAILLE"))""",
                    GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
                ),
                TYPE_ELEM_STANDARD=SIMP(
                    statut="f",
                    typ="TXM",
                    into=("DRO", "COU", "TRN", "TEE"),
                    fr=tr(
                        "type d'élément de tuyauterie ou sont affectés les indices de contraintes"
                    ),
                ),
            ),
            RESU_THER=FACT(
                statut="f",
                max="**",
                fr=tr("resultats thermiques"),
                regles=(UN_PARMI("TOUT", "GROUP_MA"),),
                NUME_RESU_THER=SIMP(
                    statut="o", typ="I", fr=tr("numéro de la table de résultat thermique")
                ),
                TABL_RESU_THER=SIMP(
                    statut="o",
                    typ=table_sdaster,
                    fr=tr("table relevé des températures sur la section"),
                ),
                TABL_MOYE_THER=SIMP(
                    statut="o", typ=table_sdaster, fr=tr("table relevé des moyennes sur la section")
                ),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
                b_grma=BLOC(
                    condition="""(exists("GROUP_MA"))""",
                    GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
                ),
            ),
            SEISME=FACT(
                statut="f",
                max="**",
                fr=tr("Situation séisme"),
                NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
                NB_CYCL_SEISME=SIMP(
                    statut="o", typ="I", fr=tr("nombre de cycles associé au séisme")
                ),
                NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
                NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
                NUME_GROUPE=SIMP(statut="o", typ="I", fr=tr("numéro du groupe de la situation")),
                CHAR_ETAT=SIMP(
                    statut="o", typ="I", max="**", fr=tr("numeros de chargements etat A")
                ),
                TEMP_REF=SIMP(statut="f", typ="R", fr=tr("temperature référence")),
            ),
            SITUATION=FACT(
                statut="o",
                max="**",
                fr=tr("Situation"),
                NB_OCCUR=SIMP(statut="o", typ="I", fr=tr("nombre d'occurences de la situation")),
                NUME_SITU=SIMP(statut="o", typ="I", fr=tr("numéro de la situation")),
                NOM_SITU=SIMP(statut="f", typ="TXM", fr=tr("nom de la situation")),
                COMBINABLE=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="OUI",
                    into=("OUI", "NON"),
                    fr=tr("non = sous-cycle"),
                ),
                NUME_GROUPE=SIMP(statut="o", typ="I", fr=tr("numéro des groupes de la situation")),
                NUME_PASSAGE=SIMP(
                    statut="f", typ="I", min=2, max=2, fr=tr("numéro des situations de passage")
                ),
                NUME_RESU_THER=SIMP(
                    statut="f", typ="I", max="**", fr=tr("numeros de transitoires thermiques")
                ),
                CHAR_ETAT_A=SIMP(
                    statut="o", typ="I", max="**", fr=tr("numeros de chargements etat A")
                ),
                CHAR_ETAT_B=SIMP(
                    statut="o", typ="I", max="**", fr=tr("numeros de chargements etat B")
                ),
                PRES_A=SIMP(statut="o", typ="R", fr=tr("pression etat A")),
                PRES_B=SIMP(statut="o", typ="R", fr=tr("pression etat B")),
                TEMP_REF_A=SIMP(statut="f", typ="R", fr=tr("temperature référence etat A")),
                TEMP_REF_B=SIMP(statut="f", typ="R", fr=tr("temperature référence etat B")),
            ),
        ),
    ),
)
