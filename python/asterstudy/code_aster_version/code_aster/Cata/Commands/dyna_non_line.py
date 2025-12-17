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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DYNA_NON_LINE = OPER(
    nom="DYNA_NON_LINE",
    op=70,
    sd_prod=evol_noli,
    reentrant="f:RESULTAT",
    fr=tr(
        "Calcul de l'évolution dynamique d'une structure dont le matériau ou la géométrie ont un comportement non linéaire"
    ),
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(
        statut="f", typ=evol_noli, fr=tr("Objet qui sera enrichi des nouveaux instants calculés")
    ),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    MODE_STAT=SIMP(statut="f", typ=mode_meca),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    MASS_DIAG=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
    MATR_ELEM_AMOR=SIMP(statut="f", typ=(matr_elem_depl_r,), max=1),
    EXCIT=FACT(
        statut="f",
        max="**",
        regles=(PRESENT_ABSENT("FONC_MULT", "ACCE"), PRESENT_PRESENT("ACCE", "VITE", "DEPL")),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE", "SUIV", "DIDI")
        ),
        CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MULT_APPUI=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        DIRECTION=SIMP(statut="f", typ="R", max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    ),
    EXCIT_GENE=FACT(
        statut="f",
        max="**",
        FONC_MULT=SIMP(statut="f", typ=fonction_sdaster, max="**"),
        VECT_GENE=SIMP(statut="f", typ=vect_asse_gene, max="**"),
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
    AMOR_RAYL_RIGI=SIMP(statut="f", typ="TXM", defaut="ELASTIQUE", into=("TANGENTE", "ELASTIQUE")),
    VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
    AMOR_MODAL=FACT(
        statut="f",
        regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR"),),
        MODE_MECA=SIMP(statut="f", typ=mode_meca),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
        LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        NB_MODE=SIMP(statut="f", typ="I"),
        REAC_VITE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
    PROJ_MODAL=FACT(
        statut="f",
        MODE_MECA=SIMP(statut="o", typ=mode_meca),
        NB_MODE=SIMP(statut="f", typ="I"),
        regles=(PRESENT_PRESENT("MASS_GENE", "RIGI_GENE"),),
        MASS_GENE=SIMP(statut="f", typ=matr_asse_gene_r),
        RIGI_GENE=SIMP(statut="f", typ=matr_asse_gene_r),
        AMOR_GENE=SIMP(statut="f", typ=matr_asse_gene_r),
        DEPL_INIT_GENE=SIMP(statut="f", typ=vect_asse_gene),
        VITE_INIT_GENE=SIMP(statut="f", typ=vect_asse_gene),
        ACCE_INIT_GENE=SIMP(statut="f", typ=vect_asse_gene),
    ),
    # -------------------------------------------------------------------
    SCHEMA_THM=C_SCHEMA_THM(),
    # -------------------------------------------------------------------
    COMPORTEMENT=C_COMPORTEMENT("DYNA_NON_LINE"),
    # -------------------------------------------------------------------
    ETAT_INIT=C_ETAT_INIT("DYNA_NON_LINE", "f"),
    # -------------------------------------------------------------------
    INCREMENT=C_INCREMENT(),
    # -------------------------------------------------------------------
    SCHEMA_TEMPS=FACT(
        statut="o",
        SCHEMA=SIMP(
            statut="o", min=1, max=1, typ="TXM", into=("DIFF_CENT", "TCHAMWA", "NEWMARK", "HHT")
        ),
        COEF_MASS_SHIFT=SIMP(statut="f", typ="R", defaut=0.0e0),
        b_tchamwa=BLOC(
            condition="""equal_to("SCHEMA", 'TCHAMWA')""",
            PHI=SIMP(statut="f", typ="R", defaut=1.05),
        ),
        b_newmark=BLOC(
            condition="""equal_to("SCHEMA", 'NEWMARK')""",
            BETA=SIMP(statut="f", typ="R", defaut=0.25),
            GAMMA=SIMP(statut="f", typ="R", defaut=0.5),
        ),
        b_hht=BLOC(
            condition="""equal_to("SCHEMA", 'HHT')""",
            ALPHA=SIMP(statut="f", typ="R", defaut=-0.1),
            MODI_EQUI=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        ),
        b_explicit=BLOC(
            condition="""equal_to("SCHEMA", 'TCHAMWA') or equal_to("SCHEMA", 'DIFF_CENT')""",
            STOP_CFL=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
            FORMULATION=SIMP(statut="o", typ="TXM", into=("ACCELERATION",)),
        ),
        b_implicit=BLOC(
            condition="""not equal_to("SCHEMA", 'TCHAMWA') and not equal_to("SCHEMA", 'DIFF_CENT')""",
            FORMULATION=SIMP(
                statut="o", max=1, typ="TXM", into=("DEPLACEMENT", "VITESSE", "ACCELERATION")
            ),
        ),
    ),
    # -------------------------------------------------------------------
    METHODE=SIMP(statut="f", typ="TXM", defaut="NEWTON", into=("NEWTON", "NEWTON_KRYLOV")),
    NEWTON=C_NEWTON(),
    # -------------------------------------------------------------------
    RECH_LINEAIRE=C_RECH_LINEAIRE(),
    # -------------------------------------------------------------------
    CONVERGENCE=C_CONVERGENCE("MECA_NON_LINE"),
    # -------------------------------------------------------------------
    SOLVEUR=C_SOLVEUR("DYNA_NON_LINE"),
    # -------------------------------------------------------------------
    OBSERVATION=C_OBSERVATION("MECANIQUE"),
    # -------------------------------------------------------------------
    MESURE=C_MESURE(),
    # -------------------------------------------------------------------
    SUIVI_DDL=C_SUIVI_DDL(),
    # -------------------------------------------------------------------
    ENERGIE=FACT(
        statut="f", max=1, CALCUL=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI")
    ),
    # -------------------------------------------------------------------
    AFFICHAGE=C_AFFICHAGE(),
    # -------------------------------------------------------------------
    ARCHIVAGE=C_ARCHIVAGE(),
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
        bloc_rigi_geom=BLOC(
            condition="""(equal_to("RIGI_GEOM", 'NON') or equal_to("MODI_RIGI", 'OUI'))""",
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
                    "DH",
                ),
            ),
            bloc_type_stab=BLOC(
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
                        "DH",
                    ),
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
    MODE_VIBR=FACT(
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
            FREQ=SIMP(statut="f", typ="R", min=2, max=2),
        ),
        b_petite=BLOC(
            condition="""(equal_to("OPTION", 'PLUS_PETITE'))""",
            NMAX_FREQ=SIMP(statut="f", typ="I", max=1, val_min=1, defaut=3),
        ),
        b_calibre=BLOC(
            condition="""(equal_to("OPTION", 'CALIBRATION'))""",
            FREQ=SIMP(statut="f", typ="R", min=2, max=2),
        ),
        MATR_RIGI=SIMP(
            statut="f", typ="TXM", defaut="ELASTIQUE", into=("ELASTIQUE", "TANGENTE", "SECANTE")
        ),
        COEF_DIM_ESPACE=SIMP(statut="f", typ="I", max=1, val_min=2, defaut=5),
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
    # -------------------------------------------------------------------
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    b_info=BLOC(
        condition="""(equal_to("INFO", 2))""",
        fr=tr("filtre les messages émis dans le .mess selon le type de message demandé"),
        INFO_DBG=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            into=("CONTACT", "MECA_NON_LINE", "PILOTAGE", "FACTORISATION", "APPARIEMENT"),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
