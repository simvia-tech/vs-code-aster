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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

STAT_NON_LINE = OPER(
    nom="STAT_NON_LINE",
    op=70,
    sd_prod=evol_noli,
    fr=tr(
        "Calcul de l'évolution mécanique ou thermo-hydro-mécanique couplée, en quasi-statique,"
        " d'une structure en non linéaire"
    ),
    reentrant="f:RESULTAT",
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(
        statut="f", typ=evol_noli, fr=tr("Objet qui sera enrichi des nouveaux instants calculés")
    ),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    EXCIT=FACT(
        statut="f",
        max="**",
        CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TYPE_CHARGE=SIMP(
            statut="f",
            typ="TXM",
            defaut="FIXE_CSTE",
            into=("FIXE_CSTE", "FIXE_PILO", "SUIV", "SUIV_PILO", "DIDI"),
        ),
    ),
    CONTACT=SIMP(statut="f", typ=char_contact),
    SOUS_STRUC=FACT(
        statut="f",
        min=0o1,
        max="**",
        regles=(UN_PARMI("TOUT", "SUPER_MAILLE"),),
        CAS_CHARGE=SIMP(statut="o", typ="TXM"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        SUPER_MAILLE=SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**"),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    # -------------------------------------------------------------------
    SCHEMA_THM=C_SCHEMA_THM(),
    # -------------------------------------------------------------------
    COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
    # -------------------------------------------------------------------
    ETAT_INIT=C_ETAT_INIT("MECA_NON_LINE", "f"),
    # -------------------------------------------------------------------
    INCREMENT=C_INCREMENT(),
    # -------------------------------------------------------------------
    METHODE=SIMP(
        statut="f",
        typ="TXM",
        defaut="NEWTON",
        into=("NEWTON", "IMPLEX", "NEWTON_KRYLOV", "MODELE_REDUIT"),
    ),
    b_meth_newton=BLOC(
        condition="""equal_to("METHODE", 'NEWTON') or equal_to("METHODE", 'NEWTON_KRYLOV')""",
        NEWTON=C_NEWTON(),
    ),
    b_meth_rom=BLOC(
        condition="""equal_to("METHODE", 'MODELE_REDUIT')""",
        MODELE_REDUIT=FACT(
            statut="o",
            REAC_INCR=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            PREDICTION=SIMP(
                statut="f",
                typ="TXM",
                defaut="TANGENTE",
                into=("DEPL_CALCULE", "TANGENTE", "ELASTIQUE", "EXTRAPOLE"),
            ),
            MATRICE=SIMP(statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE", "ELASTIQUE")),
            REAC_ITER=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            BASE_PRIMAL=SIMP(statut="o", typ=mode_empi, max=1),
            DOMAINE_REDUIT=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            EVOL_NOLI=SIMP(statut="f", typ=evol_noli),
            b_hr_cond=BLOC(
                condition="""(equal_to("DOMAINE_REDUIT", 'OUI'))""",
                GROUP_NO_INTERF=SIMP(statut="o", typ=grno, max=1),
                CORR_COMPLET=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
                b_hrcoor_cond=BLOC(
                    condition="""(equal_to("CORR_COMPLET", 'OUI'))""",
                    COEF_PENA=SIMP(statut="f", typ="R", defaut=1.0e6),
                    GROUP_NO_ENCASTRE=SIMP(statut="o", typ=grno, max=1),
                ),
            ),
        ),
    ),
    # -------------------------------------------------------------------
    RECH_LINEAIRE=C_RECH_LINEAIRE(),
    # -------------------------------------------------------------------
    PILOTAGE=C_PILOTAGE(),
    # -------------------------------------------------------------------
    CONVERGENCE=C_CONVERGENCE("MECA_NON_LINE"),
    # -------------------------------------------------------------------
    SOLVEUR=C_SOLVEUR("STAT_NON_LINE"),
    # -------------------------------------------------------------------
    OBSERVATION=C_OBSERVATION("MECANIQUE"),
    # -------------------------------------------------------------------
    MESURE=C_MESURE(),
    # -------------------------------------------------------------------
    SUIVI_DDL=C_SUIVI_DDL(),
    # -------------------------------------------------------------------
    ARCHIVAGE=C_ARCHIVAGE(),
    # -------------------------------------------------------------------
    CRIT_QUALITE=FACT(
        statut="f",
        max=1,
        ERRE_TEMPS_THM=SIMP(
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
            fr=tr("Adaptation temporelle pour les modélisations HM instationnaires"),
        ),
    ),
    # -------------------------------------------------------------------
    ENERGIE=FACT(
        statut="f", max=1, CALCUL=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI")
    ),
    # -------------------------------------------------------------------
    AFFICHAGE=C_AFFICHAGE(),
    # -------------------------------------------------------------------
    CRIT_STAB=FACT(
        statut="f",
        min=1,
        max=1,
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            defaut="PLUS_PETITE",
            into=("PLUS_PETITE", "BANDE", "CALIBRATION"),
        ),
        b_bande=BLOC(
            condition="""(equal_to("OPTION", 'BANDE'))""",
            CHAR_CRIT=SIMP(statut="f", typ="R", min=2, max=2),
        ),
        b_petite=BLOC(
            condition="""(equal_to("OPTION", 'PLUS_PETITE'))""",
            NMAX_CHAR_CRIT=SIMP(statut="f", typ="I", max=1, val_min=1, defaut=3),
        ),
        b_calibre=BLOC(
            condition="""(equal_to("OPTION", 'CALIBRATION'))""",
            CHAR_CRIT=SIMP(statut="f", typ="R", min=2, max=2),
        ),
        COEF_DIM_ESPACE=SIMP(statut="f", typ="I", max=1, val_min=2, defaut=5),
        RIGI_GEOM=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        MODI_RIGI=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        TYPE=SIMP(statut="f", typ="TXM", defaut="FLAMBEMENT", into=("FLAMBEMENT", "STABILITE")),
        PREC_INSTAB=SIMP(statut="f", typ="R", defaut=1.0e-6, max=1),
        SIGNE=SIMP(
            statut="f",
            typ="TXM",
            defaut=("POSITIF_NEGATIF"),
            into=("NEGATIF", "POSITIF", "POSITIF_NEGATIF"),
            max=1,
        ),
        b_rigi_geom=BLOC(
            condition="""(equal_to("RIGI_GEOM", 'NON'))""",
            DDL_EXCLUS=SIMP(
                statut="f",
                typ="TXM",
                validators=NoRepeat(),
                max=40,
                into=(
                    "DX",
                    "DY",
                    "DZ",
                    "DRX",
                    "DRY",
                    "DRZ",
                    "GRX",
                    "PRES",
                    "PHI",
                    "TEMP",
                    "PRE1",
                    "PRE2",
                    "UI2",
                    "UI3",
                    "VI2",
                    "VI3",
                    "WI2",
                    "WI3",
                    "UO2",
                    "UO3",
                    "VO2",
                    "VO3",
                    "WO2",
                    "WO3",
                    "UI4",
                    "UI5",
                    "VI4",
                    "VI5",
                    "WI4",
                    "WI5",
                    "UO4",
                    "UO5",
                    "VO4",
                    "VO5",
                    "WO4",
                    "WO5",
                    "UI6",
                    "UO6",
                    "VI6",
                    "VO6",
                    "WI6",
                    "WO6",
                    "WO",
                    "WI1",
                    "WO1",
                    "GONF",
                    "LIAISON",
                    "DCX",
                    "DCY",
                    "DCZ",
                    "H1X",
                    "H1Y",
                    "H1Z",
                    "K1",
                    "K2",
                    "K3",
                    "LAGS_C",
                    "V11",
                    "V12",
                    "V13",
                    "V21",
                    "V22",
                    "V23",
                    "V31",
                    "V32",
                    "V33",
                    "PRES11",
                    "PRES12",
                    "PRES13",
                    "PRES21",
                    "PRES22",
                    "PRES23",
                    "PRES31",
                    "PRES32",
                    "PRES33",
                    "VARI",
                    "LAG_GV",
                    "DAMG",
                ),
            ),
        ),
        b_type_stab=BLOC(
            condition="""equal_to("TYPE", 'STABILITE') and equal_to("RIGI_GEOM", 'NON')""",
            DDL_STAB=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                min=1,
                max=40,
                into=(
                    "DX",
                    "DY",
                    "DZ",
                    "DRX",
                    "DRY",
                    "DRZ",
                    "GRX",
                    "PRES",
                    "PHI",
                    "TEMP",
                    "PRE1",
                    "PRE2",
                    "UI2",
                    "UI3",
                    "VI2",
                    "VI3",
                    "WI2",
                    "WI3",
                    "UO2",
                    "UO3",
                    "VO2",
                    "VO3",
                    "WO2",
                    "WO3",
                    "UI4",
                    "UI5",
                    "VI4",
                    "VI5",
                    "WI4",
                    "WI5",
                    "UO4",
                    "UO5",
                    "VO4",
                    "VO5",
                    "WO4",
                    "WO5",
                    "UI6",
                    "UO6",
                    "VI6",
                    "VO6",
                    "WI6",
                    "WO6",
                    "WO",
                    "WI1",
                    "WO1",
                    "GONF",
                    "LIAISON",
                    "DCX",
                    "DCY",
                    "DCZ",
                    "H1X",
                    "H1Y",
                    "H1Z",
                    "K1",
                    "K2",
                    "K3",
                    "LAGS_C",
                    "V11",
                    "V12",
                    "V13",
                    "V21",
                    "V22",
                    "V23",
                    "V31",
                    "V32",
                    "V33",
                    "PRES11",
                    "PRES12",
                    "PRES13",
                    "PRES21",
                    "PRES22",
                    "PRES23",
                    "PRES31",
                    "PRES32",
                    "PRES33",
                    "VARI",
                    "LAG_GV",
                    "DAMG",
                ),
            ),
        ),
        regles=(EXCLUS("PAS_CALC", "LIST_INST", "INST"),),
        LIST_INST=SIMP(statut="f", typ=(listr8_sdaster)),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        PAS_CALC=SIMP(statut="f", typ="I"),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
    b_info=BLOC(
        condition="""equal_to("INFO", 2)""",
        fr=tr("filtre les messages émis dans le .mess selon le type de message demandé"),
        INFO_DBG=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            into=("CONTACT", "MECANONLINE", "PILOTAGE", "FACTOR", "SOLVEUR", "APPARIEMENT"),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
