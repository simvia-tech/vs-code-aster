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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

AFFE_MODELE = OPER(
    nom="AFFE_MODELE",
    op=18,
    sd_prod=modele_sdaster,
    fr=tr("Définir le phénomène physique modélisé et le type d'éléments finis sur le maillage"),
    reentrant="n",
    regles=(AU_MOINS_UN("AFFE", "AFFE_SOUS_STRUC"),),
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    #
    # ====
    # Définition des grandeurs caractéristiques
    # ====
    #
    GRANDEUR_CARA=FACT(
        statut="f",
        max=1,
        fr=tr("Grandeurs caractéristiques pour l'adimensionnement des indicateurs d'erreur HM"),
        #
        LONGUEUR=SIMP(statut="f", typ="R", val_min=0, fr=tr("Longueur caractéristique")),
        PRESSION=SIMP(statut="f", typ="R", val_min=0, fr=tr("Pression caractéristique")),
        TEMPERATURE=SIMP(statut="f", typ="R", val_min=0, fr=tr("Température caractéristique")),
    ),
    #
    AFFE_SOUS_STRUC=FACT(
        statut="f",
        regles=(UN_PARMI("TOUT", "SUPER_MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        SUPER_MAILLE=SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**"),
        PHENOMENE=SIMP(statut="f", typ="TXM", defaut="MECANIQUE", into=("MECANIQUE",)),
    ),
    AFFE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        PHENOMENE=SIMP(statut="o", typ="TXM", into=("MECANIQUE", "THERMIQUE", "ACOUSTIQUE")),
        b_mecanique=BLOC(
            condition="""equal_to("PHENOMENE", 'MECANIQUE')""",
            fr=tr("modélisations mécaniques"),
            MODELISATION=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max=1,
                into=(
                    "2D_DIS_T",  # person_in_charge: jean-luc.flejou at edf.fr
                    "2D_DIS_TR",  # person_in_charge: jean-luc.flejou at edf.fr
                    "2D_FLUI_ABSO",  # person_in_charge: georges-cc.devesa at edf.fr
                    "2D_FLUI_PESA",  # person_in_charge: nicolas.greffet at edf.fr
                    "2D_FLUI_STRU",  # person_in_charge: nicolas.greffet at edf.fr
                    "2D_FLUIDE",  # person_in_charge: nicolas.greffet at edf.fr
                    "3D",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_ABSO",  # person_in_charge: georges-cc.devesa at edf.fr
                    "3D_FAISCEAU",  # person_in_charge: francois.voldoire at edf.fr
                    "3D_FLUI_ABSO",  # person_in_charge: georges-cc.devesa at edf.fr
                    "3D_FLUIDE",  # person_in_charge: nicolas.greffet at edf.fr
                    "3D_INCO_UPG",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_INCO_UP",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_INCO_UPO",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_SI",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_GRAD_VARI",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "3D_GRAD_INCO",  # person_in_charge: eric.lorentz at edf.fr
                    "3D_GVNO",  # person_in_charge: jerome.beaurain at edf.fr
                    "3D_JOINT",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "3D_JOINT_HYME",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "3D_INTERFACE",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "3D_INTERFACE_S",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "AXIS",  # person_in_charge: j-pierre.lefebvre at edf.fr
                    "AXIS_FLUI_STRU",  # person_in_charge: nicolas.greffet at edf.fr
                    "AXIS_FLUI_ABSO",  # person_in_charge: stefano.cherubini at edf.fr
                    "AXIS_FLUIDE",  # person_in_charge: nicolas.greffet at edf.fr
                    "AXIS_FOURIER",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "AXIS_INCO_UPG",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_INCO_UP",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_INCO_UPO",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_SI",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_GRAD_VARI",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "AXIS_GRAD_INCO",  # person_in_charge: eric.lorentz at edf.fr
                    "AXIS_GVNO",  # person_in_charge: jerome.beaurain at edf.fr
                    "AXIS_JOINT",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "AXIS_INTERFACE",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "AXIS_INTERFACE_S",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "BARRE",  # person_in_charge: jean-luc.flejou at edf.fr
                    "CABLE_GAINE",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "2D_BARRE",  # person_in_charge: jean-luc.flejou at edf.fr
                    "C_PLAN",  # person_in_charge: j-pierre.lefebvre at edf.fr
                    "C_PLAN_SI",  # person_in_charge: mickael.abbas at edf.fr
                    "CABLE",  # person_in_charge: jean-luc.flejou at edf.fr
                    "CABLE_POULIE",  # person_in_charge: jean-luc.flejou at edf.fr
                    "COQUE_3D",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "COQUE_AXIS",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "D_PLAN",  # person_in_charge: j-pierre.lefebvre at edf.fr
                    "D_PLAN_GRAD_VARI",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "D_PLAN_GRAD_INCO",  # person_in_charge: eric.lorentz at edf.fr
                    "D_PLAN_GVNO",  # person_in_charge: jerome.beaurain at edf.fr
                    "D_PLAN_GRAD_SIGM",  # person_in_charge: sylvie.granet at edf.fr
                    "PLAN_JOINT",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "PLAN_JOINT_HYME",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "PLAN_INTERFACE",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "PLAN_INTERFACE_S",  # person_in_charge: kyrylo.kazymyrenko at edf.fr
                    "D_PLAN_ABSO",  # person_in_charge: georges-cc.devesa at edf.fr
                    "D_PLAN_INCO_UPG",  # person_in_charge: mickael.abbas at edf.fr
                    "D_PLAN_INCO_UP",  # person_in_charge: mickael.abbas at edf.fr
                    "D_PLAN_INCO_UPO",  # person_in_charge: mickael.abbas at edf.fr
                    "D_PLAN_SI",  # person_in_charge: mickael.abbas at edf.fr
                    "DIS_T",  # person_in_charge: jean-luc.flejou at edf.fr
                    "DIS_TR",  # person_in_charge: jean-luc.flejou at edf.fr
                    "DKT",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "DKTG",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "DST",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "FLUI_STRU",  # person_in_charge: nicolas.greffet at edf.fr
                    "POU_FLUI_STRU",  # person_in_charge: nicolas.greffet at edf.fr
                    "GRILLE_EXCENTRE",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "GRILLE_MEMBRANE",  # person_in_charge: sylvie.michel-ponnelle at edf.fr
                    "MEMBRANE",  # person_in_charge: thomas.de-soza at edf.fr
                    "POU_D_E",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_EM",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_T",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_T_GD",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_TG",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_TGM",  # person_in_charge: jean-luc.flejou at edf.fr
                    "POU_D_SQUE",  # person_in_charge: jean-luc.flejou at edf.fr
                    "Q4G",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "Q4GG",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "TUYAU_3M",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "TUYAU_6M",  # person_in_charge: ayaovi-dzifa.kudawoo at edf.fr
                    "COQUE_SOLIDE",  # person_in_charge: mickael.abbas at edf.fr
                    "D_PLAN_HHM",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2M_SI",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HM",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HM_SI",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HM_SI_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THM",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HMD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THHD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THVD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THMD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2MS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HMS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HMS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THHS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THVS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THMS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_THMS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HHD",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HHS",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_2DG",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THM",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HHM",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HM",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HMD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THHD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THVD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THMD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HMS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THHS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THVS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_THMS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HHD",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HHS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_HH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHM",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2M_SI",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HM",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HM_SI",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HM_SI_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THHM",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THM",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HMD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THHD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THVD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THHMD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THMD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HMS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HMS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THHS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THVS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THMS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THMS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2MD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2MS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2MS_DIL",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_THH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHD",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2D",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2S",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HH2SUDA",  # person_in_charge: sylvie.granet at edf.fr
                    "D_PLAN_HH2SUDA",  # person_in_charge: sylvie.granet at edf.fr
                    "PLAN_JHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "AXIS_JHMS",  # person_in_charge: sylvie.granet at edf.fr
                    "3D_HHO",  # person_in_charge: nicolas.pignet at edf.fr
                    "D_PLAN_HHO",  # person_in_charge: nicolas.pignet at edf.fr
                    "3D_GRAD_HHO",  # person_in_charge: nicolas.pignet at edf.fr
                    "D_PLAN_GRAD_HHO",  # person_in_charge: nicolas.pignet at edf.fr
                ),
            ),
            b_formu_hho=BLOC(
                condition="""equal_to('MODELISATION', ('3D_HHO', 'D_PLAN_HHO', "D_PLAN_GRAD_HHO", "3D_GRAD_HHO" ))""",
                fr=tr("HHO formulation"),
                FORMULATION=SIMP(
                    statut="f",
                    typ="TXM",
                    max=1,
                    into=("LINEAIRE", "QUADRATIQUE"),
                    defaut="LINEAIRE",
                ),
            ),
            b_formu_fsi=BLOC(
                condition="""equal_to('MODELISATION', ('2D_FLUIDE', '2D_FLUI_ABSO', '2D_FLUI_PESA', '2D_FLUI_STRU','3D_FLUIDE','3D_FLUI_ABSO', 'AXIS_FLUIDE', 'AXIS_FLUI_STRU', 'AXIS_FLUI_ABSO', 'FLUI_STRU'))""",
                fr=tr("FSI formulation"),
                FORMULATION=SIMP(
                    statut="f", typ="TXM", max=1, into=("U_P_PHI", "U_P", "U_PSI"), defaut="U_P_PHI"
                ),
            ),
            b_formu_dil=BLOC(
                condition="""equal_to('MODELISATION', ('D_PLAN_DIL', '3D_DIL', ))""",
                fr=tr("DIL formulation"),
                FORMULATION=SIMP(
                    statut="f", typ="TXM", max=1, into=("DIL", "DIL_INCO"), defaut="DIL"
                ),
            ),
        ),
        b_thermique=BLOC(
            condition="""equal_to("PHENOMENE", 'THERMIQUE')""",
            fr=tr("modélisations thermiques"),
            MODELISATION=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max=1,
                into=(
                    "3D",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_DIAG",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_DIAG",  # person_in_charge: mickael.abbas at edf.fr
                    "AXIS_FOURIER",  # person_in_charge: mickael.abbas at edf.fr
                    "COQUE",  # person_in_charge: mickael.abbas at edf.fr
                    "COQUE_AXIS",  # person_in_charge: mickael.abbas at edf.fr
                    "COQUE_PLAN",  # person_in_charge: mickael.abbas at edf.fr
                    "PLAN",  # person_in_charge: mickael.abbas at edf.fr
                    "PLAN_DIAG",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_HHO",
                    "PLAN_HHO",
                    "AXIS_HHO",
                ),
            ),
            b_formu_hho=BLOC(
                condition="""equal_to('MODELISATION', ('3D_HHO', 'PLAN_HHO', 'AXIS_HHO'))""",
                fr=tr("HHO formulation"),
                FORMULATION=SIMP(
                    statut="f",
                    typ="TXM",
                    max=1,
                    into=("LINEAIRE", "QUADRATIQUE"),
                    defaut="LINEAIRE",
                ),
            ),
        ),
        b_acoustique=BLOC(
            condition="""equal_to("PHENOMENE", 'ACOUSTIQUE')""",
            fr=tr("modélisations acoustiques"),
            MODELISATION=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max=1,
                into=(
                    "3D",  # person_in_charge: mickael.abbas at edf.fr
                    "PLAN",  # person_in_charge: mickael.abbas at edf.fr
                    "3D_ABSO",  # person_in_charge: mickael.abbas at edf.fr
                    "PLAN_ABSO",  # person_in_charge: mickael.abbas at edf.fr
                ),
            ),
        ),
    ),
    DISTRIBUTION=FACT(
        statut="d",
        METHODE=SIMP(
            statut="f",
            typ="TXM",
            defaut="SOUS_DOMAINE",
            into=("MAIL_CONTIGU", "MAIL_DISPERSE", "CENTRALISE", "GROUP_ELEM", "SOUS_DOMAINE"),
        ),
        b_dist_maille=BLOC(
            condition="""is_in("METHODE", ('MAIL_DISPERSE','MAIL_CONTIGU'))""",
            CHARGE_PROC0_MA=SIMP(statut="f", typ="I", defaut=100, val_min=0, val_max=100),
        ),
        b_partition=BLOC(
            condition="""equal_to("METHODE",'SOUS_DOMAINE' )""",
            NB_SOUS_DOMAINE=SIMP(statut="f", typ="I"),  # par defaut : le nombre de processeurs
            PARTITIONNEUR=SIMP(statut="f", typ="TXM", into=("METIS", "SCOTCH"), defaut="METIS"),
        ),
    ),
    VERI_JACOBIEN=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="OUI",
        fr=tr("Vérification de la forme des mailles (jacobiens tous de meme signe)."),
    ),
    VERI_NORM_IFS=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="OUI",
        fr=tr("Vérification de l'orientation des normales pur l'IFS"),
    ),
    translation={
        "AFFE_MODELE": "Assign finite element",
        "AFFE": "Finite element assignement",
        "AFFE_SOUS_STRUC": "Substructures assignement",
        "VERI_JACOBIEN": "Jacobian check",
        "DISTRIBUTION": "MPI distribution",
        "TOUT": "Everywhere",
    },
)
