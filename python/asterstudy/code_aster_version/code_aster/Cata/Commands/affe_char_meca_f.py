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

# person_in_charge: mickael.abbas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

from .affe_char_meca import compat_syntax

AFFE_CHAR_MECA_F = OPER(
    nom="AFFE_CHAR_MECA_F",
    op=7,
    sd_prod=char_meca,
    fr=tr(
        "Affectation de charges et conditions aux limites mécaniques fonction d'un (ou plusieurs) paramètres"
    ),
    reentrant="n",
    compat_syntax=compat_syntax,
    regles=(
        AU_MOINS_UN(
            "DDL_IMPO",
            "FACE_IMPO",
            "LIAISON_DDL",
            "FORCE_NODALE",
            "FORCE_FACE",
            "FORCE_ARETE",
            "FORCE_CONTOUR",
            "FORCE_INTERNE",
            "PRES_REP",
            "FORCE_POUTRE",
            "VITE_FACE",
            "ONDE_PLANE",
            "LIAISON_OBLIQUE",
            "PRE_EPSI",
            "LIAISON_GROUP",
            "LIAISON_UNIF",
            "FORCE_COQUE",
            "LIAISON_COQUE",
            "FORCE_TUYAU",
            "EFFE_FOND",
            "FLUX_THM_REP",
            "ECHANGE_THM",
        ),
    ),
    VERI_NORM=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    DOUBLE_LAGRANGE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
    DDL_IMPO=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Impose à des noeuds une ou plusieurs valeurs de déplacement (ou de certaines grandeurs asscociées) fournies"
            " par l'intermédiaire d'un concept fonction "
        ),
        regles=(
            AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO", "NOEUD"),
            AU_MOINS_UN(
                "DX",
                "DY",
                "DZ",
                "DRX",
                "DRY",
                "DRZ",
                "DRGX",
                "DRGY",
                "DRGZ",
                "GRX",
                "PRES",
                "PHI",
                "TEMP",
                "PRE1",
                "PRE2",
                "GONF",
                "BLOCAGE",
                "H1X",
                "H1Y",
                "H1Z",
                "H1PRE1",
                "K1",
                "K2",
                "K3",
                "LAGS_C",
                "GLIS",
            ),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        BLOCAGE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("DEPLACEMENT", "ROTATION"),
            min=1,
            max=2,
        ),
        DX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRGX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRGY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRGZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        GRX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRES=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PHI=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        GONF=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        H1X=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        H1Y=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        H1Z=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        H1PRE1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        K1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        K2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        K3=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        LAGS_C=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        GLIS=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FACE_IMPO=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Impose à tous les noeuds d'une face une ou plusieurs valeurs de déplacement (ou de certaines grandeurs associées)"
            " fournies par l'intérmédiaire d'un concept fonction"
        ),
        regles=(
            AU_MOINS_UN(
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
                "DNOR",
                "DTAN",
            ),
            EXCLUS("DNOR", "DX"),
            EXCLUS("DNOR", "DY"),
            EXCLUS("DNOR", "DZ"),
            EXCLUS("DNOR", "DRX"),
            EXCLUS("DNOR", "DRY"),
            EXCLUS("DNOR", "DRZ"),
            EXCLUS("DTAN", "DX"),
            EXCLUS("DTAN", "DY"),
            EXCLUS("DTAN", "DZ"),
            EXCLUS("DTAN", "DRX"),
            EXCLUS("DTAN", "DRY"),
            EXCLUS("DTAN", "DRZ"),
        ),
        #  rajout d un mot cle REPERE : / GLOBAL / LOCAL
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        DX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        GRX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRES=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PHI=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DNOR=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DTAN=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    LIAISON_DDL=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Définit une relation linéaire entre des DDLs de deux ou plusieurs noeuds, les valeurs sont fournies par"
            " l'intermediaire d'un concept de type fonction"
        ),
        regles=(UN_PARMI("GROUP_NO", "NOEUD"), UN_PARMI("COEF_MULT", "COEF_MULT_FONC")),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        DDL=SIMP(statut="o", typ="TXM", into=C_NOM_DDL_INTO("MECANIQUE"), max="**"),
        COEF_MULT=SIMP(statut="f", typ="R", max="**"),
        COEF_MULT_FONC=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"),
        COEF_IMPO=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    LIAISON_OBLIQUE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique à des noeuds la meme valeur de déplacement définie composante par composante dans un repère oblique"
            " quelconque, les valeurs sont fournis par l'intermédiaire d'un concept fonction"
        ),
        regles=(
            AU_MOINS_UN("GROUP_MA", "GROUP_NO"),
            AU_MOINS_UN("DX", "DY", "DZ", "DRX", "DRY", "DRZ"),
        ),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        ANGL_NAUT=SIMP(statut="o", typ="R", max=3),
        DX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DRZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    LIAISON_GROUP=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Définit la meme relation linéaire entre certains DDLs de couples de noeuds, les valeurs sont fournies par"
            " l'intermédiaire de concept fonction"
        ),
        regles=(
            UN_PARMI("GROUP_MA_1", "GROUP_NO_1"),
            UN_PARMI("GROUP_MA_2", "GROUP_NO_2"),
            EXCLUS("GROUP_MA_1", "GROUP_NO_2"),
            EXCLUS("GROUP_NO_1", "GROUP_MA_2"),
        ),
        GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        DDL_1=SIMP(
            statut="o", typ="TXM", into=C_NOM_DDL_INTO("MECANIQUE", with_dnor=True), max="**"
        ),
        COEF_MULT_1=SIMP(statut="o", typ="R", max="**"),
        DDL_2=SIMP(
            statut="o", typ="TXM", into=C_NOM_DDL_INTO("MECANIQUE", with_dnor=True), max="**"
        ),
        COEF_MULT_2=SIMP(statut="o", typ="R", max="**"),
        COEF_IMPO=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TRAN=SIMP(statut="f", typ="R", max=3),
        ANGL_NAUT=SIMP(statut="f", typ="R", max=3),
        CENTRE=SIMP(statut="f", typ="R", max=3),
    ),
    LIAISON_UNIF=FACT(
        statut="f",
        max="**",
        fr=tr("Impose une meme valeur (inconnue) à des DDLs d'un ensemble de noeuds"),
        regles=(UN_PARMI("GROUP_NO", "GROUP_MA"),),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        DDL=SIMP(
            statut="o", typ="TXM", into=C_NOM_DDL_INTO("MECANIQUE"), max="**", validators=NoRepeat()
        ),
    ),
    FORCE_NODALE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique à des noeuds des forces nodales dont les valeurs des composantes sont fournies par l'intermédiaire"
            " d'un concept fonction"
        ),
        regles=(UN_PARMI("GROUP_NO", "NOEUD"), AU_MOINS_UN("FX", "FY", "FZ", "MX", "MY", "MZ")),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ANGL_NAUT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max=3),
    ),
    FORCE_FACE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces surfaciques sur une face d'élément volumique dont les valeurs des composantes sont fournies"
            " par l'intermédiaire d'un concept fonction"
        ),
        regles=(AU_MOINS_UN("FX", "FY", "FZ"),),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FORCE_ARETE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces linéiques à une arete d'élément volumique ou de coque dont les valeurs des composantes sont"
            " fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(AU_MOINS_UN("FX", "FY", "FZ", "MX", "MY", "MZ"),),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FORCE_CONTOUR=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces linéiques au bord d'un domaine 2D ou AXIS ou AXIS_FOURIER, dont les valeurs des composantes"
            " sont fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(AU_MOINS_UN("FX", "FY", "FZ"),),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FORCE_INTERNE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces volumiques (2D ou 3D) à un domaine volumique, dont les valeurs des composantes sont fournies"
            " par l'intermédiaire d'un concept fonction"
        ),
        regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"), AU_MOINS_UN("FX", "FY", "FZ")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    PRES_REP=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique une pression à un domaine de milieu continu 2D ou 3D ou à un domaine de coques et tuyaux, dont les"
            " valeurs imposées (pression et/ou cisaillement) sont fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(
            AU_MOINS_UN("TOUT", "GROUP_MA", "FISSURE"),
            PRESENT_ABSENT("TOUT", "GROUP_MA", "FISSURE"),
            AU_MOINS_UN("PRES", "CISA_2D"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FISSURE=SIMP(statut="f", typ=fiss_xfem, min=1, max=100),
        PRES=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        CISA_2D=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    EFFE_FOND=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Calcul l'effet de fond sur une branche de tuyauterie (modélisation 3D) soumise"
            " à une pression dont la valeur est fournie par l'intermédiaire d'un concept fonction"
        ),
        GROUP_MA_INT=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        PRES=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    PRE_EPSI=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique un chargement de déformation initiale à un élément 2D, 3D ou de structure dont les composantes"
            " du tenseur de déformation sont fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(
            UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),
            AU_MOINS_UN(
                "EPXX",
                "EPYY",
                "EPZZ",
                "EPXY",
                "EPXZ",
                "EPYZ",
                "EPX",
                "KY",
                "KZ",
                "EXX",
                "EYY",
                "EXY",
                "KXX",
                "KYY",
                "KXY",
            ),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        EPXX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPYY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPZZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPXY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPXZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPYZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        KY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        KZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EXX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EYY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EXY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        KXX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        KYY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        KXY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FORCE_POUTRE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces linéiques sur des éléments de type poutre dont les valeurs sont fournies par"
            " l'intermédiaire d'un concept fonction"
        ),
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        #  rajout d un mot cle REPERE : / GLOBAL / LOCAL
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FORCE", into=("VENT", "FORCE")),
        # moment interdit avec VENT
        b_force=BLOC(
            condition="""equal_to("TYPE_CHARGE", 'FORCE')""",
            regles=(
                AU_MOINS_UN(
                    "FX",
                    "FY",
                    "FZ",
                    "MX",
                    "MY",
                    "MZ",
                    "MGX",
                    "MGY",
                    "MGZ",
                    "N",
                    "VY",
                    "VZ",
                    "MT",
                    "MFY",
                    "MFZ",
                ),
                PRESENT_ABSENT("FX", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("FY", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("FZ", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("MX", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("MY", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("MZ", "N", "VY", "VZ", "MT", "MFY", "MFZ"),
                PRESENT_ABSENT("N", "FX", "FY", "FZ", "MX", "MY", "MZ"),
                PRESENT_ABSENT("VY", "FX", "FY", "FZ", "MX", "MY", "MZ"),
                PRESENT_ABSENT("VZ", "FX", "FY", "FZ", "MX", "MY", "MZ"),
                PRESENT_ABSENT("MT", "FX", "FY", "FZ", "MX", "MY", "MZ"),
                PRESENT_ABSENT("MFY", "FX", "FY", "FZ", "MX", "MY", "MZ"),
                PRESENT_ABSENT("MFZ", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            ),
            FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            N=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MFY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MFZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MGX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MGY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MGZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
        b_vent=BLOC(
            condition="""equal_to("TYPE_CHARGE", 'VENT')""",
            regles=(
                AU_MOINS_UN("FX", "FY", "FZ", "N", "VY", "VZ"),
                PRESENT_ABSENT("FX", "N", "VY", "VZ"),
                PRESENT_ABSENT("FY", "N", "VY", "VZ"),
                PRESENT_ABSENT("FZ", "N", "VY", "VZ"),
                PRESENT_ABSENT("N", "FX", "FY", "FZ"),
                PRESENT_ABSENT("VY", "FX", "FY", "FZ"),
                PRESENT_ABSENT("VZ", "FX", "FY", "FZ"),
            ),
            FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            N=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
    ),
    FORCE_TUYAU=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique une pression sur des éléments TUYAU, la valeur est fournie par l'intermédiaire d'un concept fonction"
        ),
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        PRES=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FORCE_COQUE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique des forces surfaciques sur des éléments de types coques dont les valeurs sont fournies par"
            " l'intermédiaires d'un concept fonction"
        ),
        regles=(
            UN_PARMI("TOUT", "GROUP_MA"),
            AU_MOINS_UN("FX", "FY", "FZ", "MX", "MY", "MZ", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("FX", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("FY", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("FZ", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("MX", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("MY", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("MZ", "PRES", "F1", "F2", "F3", "MF1", "MF2"),
            PRESENT_ABSENT("F1", "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            PRESENT_ABSENT("F2", "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            PRESENT_ABSENT("F3", "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            PRESENT_ABSENT("MF1", "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            PRESENT_ABSENT("MF2", "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ"),
            PRESENT_ABSENT(
                "PRES", "FX", "FY", "FZ", "MX", "MY", "MZ", "F1", "F2", "F3", "MF1", "MF2"
            ),
        ),
        #  rajout d un mot cle REPERE : / GLOBAL / LOCAL
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MX=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MY=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MZ=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        F1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        F2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        F3=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MF1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        MF2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRES=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PLAN=SIMP(statut="f", typ="TXM", defaut="MAIL", into=("SUP", "INF", "MOY", "MAIL")),
    ),
    LIAISON_COQUE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Permet de représenter le raccord entre des éléments de coques au moyen des relations linéaires"
        ),
        regles=(AU_MOINS_UN("GROUP_MA_1", "GROUP_MA_2", "GROUP_NO_1", "GROUP_NO_2"),),
        GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    ),
    VITE_FACE=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Impose des vitesses à une face dont les valeurs sont fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(UN_PARMI("VNOR", "DIRECTION"),),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        VNOR=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DIRECTION=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), min=2, max=3),
        b_nonNormal=BLOC(
            condition="""exists("DIRECTION")""",
            VITE=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
    ),
    ONDE_PLANE=FACT(
        statut="f",
        max=1,
        fr=tr(
            "Impose un chargement sismique par onde plane dont la valeur est fournie par l'intermédiaire"
            " d'un concept fonction"
        ),
        DIRECTION=SIMP(statut="o", typ="R", min=3, max=3),
        COOR_SOURCE=SIMP(statut="f", typ="R", min=2, max=3),
        c_reflection=BLOC(
            condition="""exists("COOR_SOURCE")""",
            COOR_REFLECHI=SIMP(statut="f", typ="R", min=2, max=3),
        ),
        TYPE_ONDE=SIMP(statut="o", typ="TXM", into=("S", "P", "SV", "SH")),
        FONC_SIGNAL=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DEPL_IMPO=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    FLUX_THM_REP=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique à un domaine continue 2D ou 3D un flux de chaleur et/ou un apport de masse fluide (flux hydraulique)"
            " dont les valeurs des flux sont fournies par l'intermédiaire d'un concept fonction"
        ),
        regles=(
            UN_PARMI("TOUT", "GROUP_MA"),
            AU_MOINS_UN("FLUN", "FLUN_HYDR1", "FLUN_HYDR2", "FLUN_FRAC"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FLUN=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUN_FRAC=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUN_HYDR1=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUN_HYDR2=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    ECHANGE_THM=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Applique à un domaine de milieu continu 2D ou 3D une condition echange dont les valeurs des coef sont des fonctions"
            "(flux hydraulique)"
        ),
        regles=(
            UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),
            AU_MOINS_UN("COEF_11", "COEF_12", "COEF_21", "COEF_22"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        COEF_11=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_12=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_21=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_22=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE1_EXT=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        PRE2_EXT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
