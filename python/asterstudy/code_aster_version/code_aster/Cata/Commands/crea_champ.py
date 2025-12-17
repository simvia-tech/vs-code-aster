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


def crea_champ_prod(TYPE_CHAM, **args):
    if args.get("__all__"):
        return (carte_sdaster, cham_no_sdaster, cham_elem)
    # Analysis of type of field
    location, quantity, typ = TYPE_CHAM.split("_")

    if location == "CART":
        return carte_sdaster
    elif location == "NOEU":
        return cham_no_sdaster
    elif location[0:2] == "EL":
        return cham_elem
    else:
        raise AsException("type de concept resultat_sdaster non prevu")


CREA_CHAMP = OPER(
    nom="CREA_CHAMP",
    op=195,
    sd_prod=crea_champ_prod,
    fr=tr("Création d'un champ "),
    reentrant="f:CHAM_GD",
    reuse=SIMP(statut="c", typ=CO),
    b_reuse=BLOC(
        condition="""is_in("OPERATION", ("ASSE", "COMB"))""",
        CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
        fr=tr("Objet qui sera réutilisé pour l'opération"),
    ),
    # TYPE_CHAM doit etre de la forme : CART_xx, NOEU_xx, ELEM_xx, ELGA_xx ou ELNO_xx
    # ou xx est le nom d'une grandeur définie dans le catalogue des grandeurs
    TYPE_CHAM=SIMP(statut="o", typ="TXM", into=C_TYPE_CHAM_INTO()),
    #        SI CREATION D'UN CHAM_NO, POUR IMPOSER LA NUMEROTATION DES DDLS :
    #        ------------------------------------------------------------------
    regles=(EXCLUS("NUME_DDL", "CHAM_NO")),
    NUME_DDL=SIMP(statut="f", typ=(nume_ddl_sdaster)),
    CHAM_NO=SIMP(statut="f", typ=(cham_no_sdaster)),
    #        AUTORISE-T-ON LE PROLONGEMENT DU CHAMP PAR ZERO ?
    #        ------------------------------------------------------------------
    #        CE MOT CLE N'A DE SENS QUE DANS 2 CAS DE FIGURE :
    #          - POUR LES CHAM_ELEM (AVEC LE MOT CLE MODELE)
    #          - POUR LES CHAM_NO SI ON IMPOSE LEUR NUMEROTATION
    b_prol_zero=BLOC(
        condition="""exists("NUME_DDL") or exists("CHAM_NO") or (exists("TYPE_CHAM") and TYPE_CHAM[0:2] == 'EL')""",
        PROL_ZERO=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    ),
    #        SI CREATION D'UN CHAM_ELEM, POUR POUVOIR AIDER A L'ALLOCATION DU CHAMP :
    #        (PAR DEFAUT : TOU_INI_ELNO/_ELGA/_ELEM)
    #        ------------------------------------------------------------------
    OPTION=SIMP(statut="f", typ="TXM", validators=NoRepeat()),
    #        Si creation d'un cham_elem avec sous-points, pour que tous les sous-points
    #        soient affectes : on duplique la valeur sur tous les sous-points
    #        ------------------------------------------------------------------
    AFFE_SP=FACT(statut="f", max=1, CARA_ELEM=SIMP(statut="o", typ=cara_elem, min=1, max=1)),
    #        LE MOT-CLE OPERATION EST OBLIGATOIRE. IL PERMET LE BON AIGUILLAGE.
    #        ------------------------------------------------------------------
    OPERATION=SIMP(
        statut="o",
        typ="TXM",
        into=("AFFE", "ASSE", "ASSE_DEPL", "EVAL", "EXTR", "DISC", "NORMALE", "R2C", "C2R", "COMB"),
    ),
    #        ------------------------------------------------------------------
    b_norm=BLOC(
        condition="""equal_to("OPERATION", 'NORMALE')""",
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
    ),
    #        ------------------------------------------------------------------
    b_affe=BLOC(
        condition="""equal_to("OPERATION", 'AFFE')""",
        regles=(UN_PARMI("MAILLAGE", "MODELE"),),
        MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster)),
        MODELE=SIMP(statut="f", typ=(modele_sdaster)),
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(
                AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO", "NOEUD"),
                UN_PARMI("VALE", "VALE_I", "VALE_C", "VALE_F"),
            ),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
            VALE=SIMP(statut="f", typ="R", max="**"),
            VALE_I=SIMP(statut="f", typ="I", max="**"),
            VALE_C=SIMP(statut="f", typ="C", max="**"),
            VALE_F=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"),
        ),
    ),
    #        ------------------------------------------------------------------
    b_asse=BLOC(
        condition="""equal_to("OPERATION", 'ASSE')""",
        regles=(UN_PARMI("MAILLAGE", "MODELE"),),
        MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster)),
        MODELE=SIMP(statut="f", typ=(modele_sdaster)),
        ASSE=FACT(
            statut="o",
            max="**",
            regles=(
                AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO"),
                PRESENT_PRESENT("NOM_CMP_RESU", "NOM_CMP"),
            ),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            CHAM_GD=SIMP(statut="o", typ=cham_gd_sdaster),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            NOM_CMP_RESU=SIMP(statut="f", typ="TXM", max="**"),
            CUMUL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            COEF_R=SIMP(statut="f", typ="R", defaut=1.0),
            COEF_C=SIMP(statut="f", typ="C", max=1),
        ),
    ),
    #        ------------------------------------------------------------------
    b_comb=BLOC(
        condition="""equal_to("OPERATION", 'COMB')""",
        fr=tr("Pour faire une combinaison linéaire de cham_no ayant meme profil"),
        COMB=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=cham_no_sdaster),
            COEF_R=SIMP(statut="o", typ="R"),
        ),
    ),
    #        ------------------------------------------------------------------
    b_eval=BLOC(
        condition="""equal_to("OPERATION", 'EVAL')""",
        CHAM_F=SIMP(statut="o", typ=cham_gd_sdaster),
        CHAM_PARA=SIMP(statut="o", typ=cham_gd_sdaster, max="**"),
    ),
    #        ------------------------------------------------------------------
    b_xfem=BLOC(
        condition="""equal_to("OPERATION", 'ASSE_DEPL')""",
        CHAM_GD=SIMP(statut="o", typ=cham_gd_sdaster),
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    ),
    #        ------------------------------------------------------------------
    b_r2c=BLOC(
        condition="""equal_to("OPERATION", 'R2C')""", CHAM_GD=SIMP(statut="o", typ=cham_gd_sdaster)
    ),
    #        ------------------------------------------------------------------
    b_c2r=BLOC(
        condition="""equal_to("OPERATION", 'C2R')""",
        CHAM_GD=SIMP(statut="o", typ=cham_gd_sdaster),
        PARTIE=SIMP(statut="o", typ="TXM", into=("REEL", "IMAG", "MODULE", "PHASE")),
    ),
    #        ------------------------------------------------------------------
    b_disc=BLOC(
        condition="""equal_to("OPERATION", 'DISC')""",
        MODELE=SIMP(statut="f", typ=(modele_sdaster)),
        CHAM_GD=SIMP(statut="o", typ=cham_gd_sdaster),
    ),
    #        ------------------------------------------------------------------
    b_extr=BLOC(
        condition="""equal_to("OPERATION", 'EXTR')""",
        regles=(
            AU_MOINS_UN("MAILLAGE", "FISSURE", "RESULTAT", "TABLE", "CARA_ELEM", "CHARGE"),
            PRESENT_ABSENT("MAILLAGE", "FISSURE", "RESULTAT", "CARA_ELEM", "CHARGE"),
            PRESENT_ABSENT("FISSURE", "MAILLAGE", "RESULTAT", "TABLE", "CARA_ELEM", "CHARGE"),
            PRESENT_ABSENT("RESULTAT", "FISSURE", "MAILLAGE", "TABLE", "CARA_ELEM", "CHARGE"),
            PRESENT_ABSENT("TABLE", "RESULTAT", "FISSURE", "CARA_ELEM", "CHARGE"),
            PRESENT_ABSENT("CARA_ELEM", "MAILLAGE", "TABLE", "RESULTAT", "FISSURE", "CHARGE"),
            PRESENT_ABSENT("CHARGE", "MAILLAGE", "TABLE", "RESULTAT", "FISSURE", "CARA_ELEM"),
        ),
        MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster)),
        FISSURE=SIMP(statut="f", typ=(fiss_xfem)),
        RESULTAT=SIMP(statut="f", typ=(resultat_sdaster)),
        TABLE=SIMP(statut="f", typ=(table_sdaster), min=1, max=1),
        CARA_ELEM=SIMP(statut="f", typ=(cara_elem), min=1, max=1),
        CHARGE=SIMP(statut="f", typ=(char_meca), min=1, max=1),
        b_extr_maillage=BLOC(
            condition="""exists("MAILLAGE") and not exists("TABLE")""",
            NOM_CHAM=SIMP(
                statut="o", typ="TXM", validators=NoRepeat(), into=("GEOMETRIE", "ABSC_CURV")
            ),
        ),
        b_extr_cara_elem=BLOC(
            condition="""exists("CARA_ELEM")""",
            NOM_CHAM=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                into=(
                    ".CARGENBA",
                    ".CARMASSI",
                    ".CARCABLE",
                    ".CARCOQUE",
                    ".CARGEOBA",
                    ".CARDISCK",
                    ".CARARCPO",
                    ".CARGENPO",
                    ".CARDISCM",
                    ".CARORIEN",
                    ".CARDISCA",
                    ".CVENTCXF",
                    ".CARPOUFL",
                    ".CARGEOPO",
                    ".CARDINFO",
                    ".CAFIBR",
                    ".CANBSP",
                ),
            ),
        ),
        b_extr_charge=BLOC(
            condition="""exists("CHARGE")""",
            NOM_CHAM=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                into=(
                    ".CHME.EPSIN",
                    ".CHME.F1D1D",
                    ".CHME.F1D2D",
                    ".CHME.F1D3D",
                    ".CHME.F2D2D",
                    ".CHME.F2D3D",
                    ".CHME.F3D3D",
                    ".CHME.FCO2D",
                    ".CHME.FCO3D",
                    ".CHME.FELEC",
                    ".CHME.FL101",
                    ".CHME.FL102",
                    ".CHME.FLUX",
                    ".CHME.FORNO",
                    ".CHME.IMPE",
                    ".CHME.ONDE",
                    ".CHME.ONDPL",
                    ".CHME.ONDPR",
                    ".CHME.PESAN",
                    ".CHME.PRESS",
                    ".CHME.ROTAT",
                    ".CHME.SIGIN",
                    ".CHME.SIINT",
                    ".CHME.VFACE",
                ),
            ),
        ),
        b_extr_fissure=BLOC(
            condition="""exists("FISSURE")""",
            NOM_CHAM=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                into=(
                    "LTNO",
                    "LNNO",
                    "GRLTNO",
                    "GRLNNO",
                    "STNO",
                    "BASLOC",
                    "GRI.LNNO",
                    "GRI.LTNO",
                    "GRI.GRLNNO",
                    "GRI.GRLTNO",
                ),
            ),
        ),
        b_extr_table=BLOC(
            condition="""exists("TABLE")""", MODELE=SIMP(statut="f", typ=(modele_sdaster))
        ),
        b_extr_resultat=BLOC(
            condition="""exists("RESULTAT")""",
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            TYPE_MAXI=SIMP(
                statut="f", typ="TXM", into=("MAXI", "MINI", "MAXI_ABS", "MINI_ABS", "NORM_TRAN")
            ),
            # si TYPE_MAXI, on spécifie en général plusieurs numéros d'ordre :
            b_type_abs=BLOC(
                condition="""(equal_to("TYPE_MAXI", 'MAXI_ABS') or equal_to("TYPE_MAXI", 'MINI_ABS'))""",
                TYPE_RESU=SIMP(
                    statut="f", typ="TXM", defaut="VALE", into=("VALE", "INST", "VALE_ABS")
                ),
            ),
            b_type_non_abs=BLOC(
                condition="""(equal_to("TYPE_MAXI", 'MAXI') or equal_to("TYPE_MAXI", 'MINI') or equal_to("TYPE_MAXI", 'NORM_TRAN'))""",
                TYPE_RESU=SIMP(statut="f", typ="TXM", defaut="VALE", into=("VALE", "INST")),
            ),
            b_type_maxi=BLOC(
                condition="""exists("TYPE_MAXI")""",
                regles=(
                    EXCLUS(
                        "TOUT_ORDRE",
                        "LIST_INST",
                        "LIST_FREQ",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                LIST_INST=SIMP(statut="f", typ=(listr8_sdaster)),
                LIST_FREQ=SIMP(statut="f", typ=(listr8_sdaster)),
                NUME_ORDRE=SIMP(statut="f", typ="I", max="**"),
                INST=SIMP(statut="f", typ="R", max="**"),
                FREQ=SIMP(statut="f", typ="R", max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", max="**"),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", max="**"),
                ANGLE=SIMP(statut="f", typ="R", max="**"),
            ),
            # si .not. TYPE_MAXI, on ne doit spécifier qu'un seul numéro d'ordre :
            b_non_type_maxi=BLOC(
                condition="""not exists("TYPE_MAXI")""",
                regles=(
                    UN_PARMI(
                        "NUME_ORDRE", "INST", "FREQ", "NUME_MODE", "NOEUD_CMP", "NOM_CAS", "ANGLE"
                    ),
                ),
                NUME_ORDRE=SIMP(statut="f", typ="I"),
                INST=SIMP(statut="f", typ="R"),
                FREQ=SIMP(statut="f", typ="R"),
                NUME_MODE=SIMP(statut="f", typ="I"),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", max=2),
                NOM_CAS=SIMP(statut="f", typ="TXM"),
                ANGLE=SIMP(statut="f", typ="R"),
                b_inst=BLOC(
                    condition="""exists("INST") """,
                    INTERPOL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "LIN")),
                ),
            ),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),  # fin bloc b_extr
    ),
    # FIN DU CATALOGUE : INFO,TITRE ET TYPAGE DU RESULTAT :
    # -----------------------------------------------------
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
