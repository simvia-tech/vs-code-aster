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
# person_in_charge: mickael.abbas at edf.fr
#
from ..Language.DataStructure import *
from ..Language.Syntax import *
from .c_relation import C_RELATION


def C_COMPORTEMENT(command):
    assert command in (
        "CALC_ESSAI_GEOMECA",
        "SIMU_POINT_MAT",
        "CALCUL",
        "DYNA_NON_LINE",
        "MECA_NON_LINE",
        "THER_NON_LINE",
    )

    stcom = "d"
    if command == "CALC_ESSAI_GEOMECA":
        mcfact = FACT(
            statut=stcom,
            min=1,
            max="**",  # COMMUN#
            RELATION=SIMP(
                statut="o",
                typ="TXM",
                into=(
                    "HUJEUX",
                    "DRUCK_PRAGER",
                    "DRUCK_PRAG_N_A",
                    "CAM_CLAY",
                    "CJS",
                    "MOHR_COULOMB",
                    "Iwan",
                    "MohrCoulombAS",
                    "GonfElas",
                    "KH_CSSM",
                    "NLH_CSRM",
                    "MFRONT",
                ),
            ),
            b_mfront=BLOC(
                condition="""equal_to('RELATION', 'MFRONT') """,
                fr=tr("Comportement utilisateur de type MFRONT"),
                COMPOR_MFRONT=SIMP(
                    statut="o", typ=compor_mgis, fr=tr("Comportement MFRONT à utiliser")
                ),
                VERI_BORNE=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="ARRET",
                    into=("ARRET", "SANS", "MESSAGE"),
                    fr=tr("Vérification des bornes physiques de la loi de comportement MFRONT"),
                ),
                SYME_MATR_TANG=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            ),
            b_mfront_hidden=BLOC(
                condition="""not equal_to('RELATION', 'MFRONT')""",
                COMPOR_MFRONT=SIMP(
                    statut="c", typ=compor_mgis, fr=tr("objet ajouté automatiquement")
                ),
            ),
            DEFORMATION=SIMP(
                statut="f", typ="TXM", defaut="PETIT", into=("PETIT", "GDEF_LOG", "GREEN_LAGRANGE")
            ),
            # Parametres d'integration
            b_mfront_resi=BLOC(
                condition="""equal_to('RELATION', 'MFRONT')""",
                RESI_INTE_MAXI=SIMP(statut="f", typ="R", defaut=1.0e-8),
                ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=100),
            ),
            b_no_mfront=BLOC(
                condition="""not equal_to('RELATION', 'MFRONT')""",
                RESI_INTE_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=20),
            ),
            b_redec_local=BLOC(
                condition="""is_in('DEFORMATION', ('PETIT','PETIT_REAC','GROT_GDEP'))""",
                fr=tr("Nombre de redécoupages internes du pas de temps"),
                ITER_INTE_PAS=SIMP(statut="f", typ="I", defaut=0),
            ),
            ALGO_INTE=SIMP(
                statut="f",
                typ="TXM",
                into=(
                    "ANALYTIQUE",
                    "SECANTE",
                    "DEKKER",
                    "NEWTON_1D",
                    "BRENT",
                    "NEWTON",
                    "NEWTON_RELI",
                    "NEWTON_PERT",
                    "RUNGE_KUTTA",
                    "SPECIFIQUE",
                    "SEMI_EXPLICITE",
                    "BASCULE_EXPLICITE",
                    "SANS_OBJET",
                ),
            ),
            TYPE_MATR_TANG=SIMP(statut="f", typ="TXM", into=("PERTURBATION", "VERIFICATION")),
            b_perturb=BLOC(
                condition=""" (exists("TYPE_MATR_TANG")) """,
                fr=tr("Calcul de la matrice tangente par perturbation, valeur de la perturbation"),
                VALE_PERT_RELA=SIMP(statut="f", typ="R", defaut=1.0e-5),
            ),
            PARM_THETA=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0, defaut=1.0),
            b_radi=BLOC(
                condition="""not exists("TYPE_MATR_TANG")""",
                RESI_RADI_RELA=SIMP(statut="f", typ="R"),
            ),
        )
    elif command == "THER_NON_LINE":
        mcfact = FACT(
            statut=stcom,
            max="**",
            RELATION=SIMP(
                statut="f",
                typ="TXM",
                defaut="THER_NL",
                into=(
                    "THER_NL",
                    "THER_HYDR",
                    "SECH_GRANGER",
                    "SECH_MENSI",
                    "SECH_BAZANT",
                    "SECH_NAPPE",
                ),
            ),
            regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        )
    else:
        opts = {}
        if command in ("MECA_NON_LINE", "DYNA_NON_LINE"):
            opts["b_crirupt"] = BLOC(
                condition="""is_in("RELATION", ('VMIS_ISOT_LINE','VMIS_ISOT_TRAC','VISCOCHAB','VISC_ISOT_LINE','VISC_ISOT_TRAC',))""",
                fr=tr("Critere de rupture selon une contrainte critique"),
                POST_ITER=SIMP(statut="f", typ="TXM", into=("CRIT_RUPT",)),
            )
        if command == "MECA_NON_LINE":
            opts["b_anneal"] = BLOC(
                condition="""is_in("RELATION", ('VMIS_ISOT_LINE','VMIS_CINE_LINE','VMIS_ECMI_LINE','VMIS_ISOT_TRAC','VMIS_CIN1_CHAB','VMIS_CIN2_CHAB'))""",
                fr=tr("Restauration d'écrouissage"),
                POST_INCR=SIMP(statut="f", typ="TXM", into=("REST_ECRO", "SANS")),
            )

        mcfact = FACT(
            statut=stcom,
            min=1,
            max="**",
            regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            RELATION=SIMP(statut="f", typ="TXM", defaut="ELAS", into=C_RELATION("MECA_NON_LINE")),
            REGU_VISC=SIMP(statut="f", typ="TXM", into=("NON", "OUI"), defaut="NON"),
            b_monox=BLOC(
                condition="""equal_to("RELATION", 'MONOCRISTAL') """,
                fr=tr("SD issue de DEFI_COMPOR"),
                COMPOR=SIMP(statut="o", typ=compor_sdaster, max=1),
            ),
            b_rigi_geom=BLOC(
                condition="""equal_to("RELATION", 'MULTIFIBRE')""",
                fr=tr("Work on deformed geometry"),
                RIGI_GEOM=SIMP(statut="f", typ="TXM", into=("DEFAUT", "OUI"), defaut="DEFAUT"),
            ),
            b_polyx=BLOC(
                condition="""equal_to("RELATION", 'POLYCRISTAL') """,
                fr=tr("SD issue de DEFI_COMPOR"),
                COMPOR=SIMP(statut="o", typ=compor_sdaster, max=1),
            ),
            b_umat=BLOC(
                condition="""equal_to("RELATION", 'UMAT') """,
                fr=tr("Comportement utilisateur de type UMAT"),
                NB_VARI=SIMP(statut="o", typ="I", max=1, fr=tr("Nombre de variables internes")),
                LIBRAIRIE=SIMP(
                    statut="o",
                    typ="TXM",
                    validators=LongStr(1, 128),
                    fr=tr("Chemin vers la bibliothèque dynamique pour UMAT"),
                ),
                NOM_ROUTINE=SIMP(
                    statut="o", typ="TXM", fr=tr("Nom de la routine UMAT dans la bibliothèque")
                ),
            ),
            b_mfront=BLOC(
                condition="""equal_to("RELATION", 'MFRONT') """,
                fr=tr("Comportement utilisateur de type MFRONT"),
                COMPOR_MFRONT=SIMP(
                    statut="o", typ=compor_mgis, fr=tr("Comportement MFRONT à utiliser")
                ),
                VERI_BORNE=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="ARRET",
                    into=("ARRET", "SANS", "MESSAGE"),
                    fr=tr("Vérification des bornes physiques de la loi"),
                ),
                ALGO_CPLAN=SIMP(
                    statut="f", typ="TXM", defaut="DEBORST", into=("DEBORST", "ANALYTIQUE")
                ),
                SYME_MATR_TANG=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            ),
            b_mfront_hidden=BLOC(
                condition="""not equal_to('RELATION', 'MFRONT')""",
                COMPOR_MFRONT=SIMP(
                    statut="c", typ=compor_mgis, fr=tr("objet ajouté automatiquement")
                ),
            ),
            b_kit_ddi=BLOC(
                condition="""equal_to("RELATION", 'KIT_DDI') """,
                fr=tr("relations de couplage fluage-plasticite"),
                RELATION_KIT=SIMP(
                    statut="o",
                    typ="TXM",
                    min=2,
                    max=2,
                    validators=NoRepeat(),
                    into=(
                        "VMIS_CINE_LINE",
                        "VMIS_ISOT_TRAC",
                        "VMIS_ISOT_LINE",
                        "VMIS_ISOT_PUIS",
                        "GLRC_DM",
                        "BETON_GRANGER",
                        "BETON_GRANGER_V",
                        "BETON_UMLV",
                        "ROUSS_PR",
                        "BETON_DOUBLE_DP",
                        "ENDO_ISOT_BETON",
                        "MAZARS",
                    ),
                ),
            ),
            b_kit_cg=BLOC(
                condition="""equal_to("RELATION", 'KIT_CG') """,
                fr=tr("relations pour elements cables gaines"),
                RELATION_KIT=SIMP(
                    statut="o",
                    typ="TXM",
                    min=2,
                    max=2,
                    validators=NoRepeat(),
                    into=(
                        "CABLE_GAINE_FROT",
                        "VMIS_ISOT_LINE",
                        "VMIS_ISOT_TRAC",
                        "VMIS_CINE_LINE",
                        "PINTO_MENEGOTTO",
                        "ELAS",
                        "SANS",
                    ),
                ),
            ),
            b_kit_thm=BLOC(
                condition="""is_in("RELATION", ['KIT_THHM', 'KIT_THH','KIT_THM','KIT_THV','KIT_THH2M','KIT_THH2'])""",
                fr=tr("lois de comportements thermo-hydro-mecaniques"),
                RELATION_KIT=SIMP(
                    statut="o",
                    typ="TXM",
                    max=9,
                    validators=NoRepeat(),
                    into=(
                        "BARCELONE",
                        "CAM_CLAY",
                        "CJS",
                        "CZM_EXP_REG",
                        "CZM_LIN_REG",
                        "DRUCK_PRAGER",
                        "DRUCK_PRAG_N_A",
                        "ELAS",
                        "ENDO_ISOT_BETON",
                        "GonfElas",
                        "HOEK_BROWN_EFF",
                        "HOEK_BROWN_TOT",
                        "HUJEUX",
                        "Iwan",
                        "JOINT_BANDIS",
                        "NLH_CSRM",
                        "LAIGLE",
                        "LETK",
                        "LKR",
                        "MAZARS",
                        "MOHR_COULOMB",
                        "RANKINE",
                        "VISC_DRUC_PRAG",
                        "VISC_MAXWELL",
                        "VISC_MAXWELL_MT",
                    )
                    + (
                        "GAZ",
                        "LIQU_SATU",
                        "LIQU_GAZ_ATM",
                        "LIQU_VAPE_GAZ",
                        "LIQU_AD_GAZ_VAPE",
                        "LIQU_AD_GAZ",
                        "LIQU_VAPE",
                        "LIQU_GAZ",
                        "HYDR_UTIL",
                        "HYDR_TABBAL",
                        "HYDR_VGM",
                        "HYDR_VGC",
                        "HYDR_ENDO",
                    ),
                ),
                COMPOR_MFRONT=SIMP(
                    statut="c", typ=compor_mgis, fr=tr("objet ajouté automatiquement")
                ),
            ),
            b_kit_hm=BLOC(
                condition="""is_in("RELATION", ['KIT_HHM','KIT_HH', 'KIT_H','KIT_HM','KIT_HH2M','KIT_HH2',])""",
                fr=tr("lois de comportements thermo-hydro-mecaniques"),
                RELATION_KIT=SIMP(
                    statut="o",
                    typ="TXM",
                    max=9,
                    validators=NoRepeat(),
                    into=(
                        "BARCELONE",
                        "CAM_CLAY",
                        "CJS",
                        "CZM_EXP_REG",
                        "CZM_LIN_REG",
                        "DRUCK_PRAGER",
                        "DRUCK_PRAG_N_A",
                        "ELAS",
                        "ENDO_ISOT_BETON",
                        "GonfElas",
                        "HOEK_BROWN_EFF",
                        "HOEK_BROWN_TOT",
                        "HUJEUX",
                        "Iwan",
                        "JOINT_BANDIS",
                        "NLH_CSRM",
                        "LAIGLE",
                        "LETK",
                        "LKR",
                        "MAZARS",
                        "MFRONT",
                        "MOHR_COULOMB",
                        "RANKINE",
                        "VISC_DRUC_PRAG",
                        "VISC_MAXWELL",
                        "VISC_MAXWELL_MT",
                    )
                    + (
                        "GAZ",
                        "LIQU_SATU",
                        "LIQU_GAZ_ATM",
                        "LIQU_VAPE_GAZ",
                        "LIQU_AD_GAZ_VAPE",
                        "LIQU_AD_GAZ",
                        "LIQU_VAPE",
                        "LIQU_GAZ",
                        "HYDR_UTIL",
                        "HYDR_TABBAL",
                        "HYDR_VGM",
                        "HYDR_VGC",
                        "HYDR_ENDO",
                    ),
                ),
                b_mfr_hm=BLOC(
                    condition="""'MFRONT' in value("RELATION_KIT")""",
                    fr=tr("Comportement utilisateur meca THM de type MFRONT"),
                    COMPOR_MFRONT=SIMP(
                        statut="o", typ=compor_mgis, fr=tr("Comportement MFRONT à utiliser")
                    ),
                    VERI_BORNE=SIMP(
                        statut="f",
                        typ="TXM",
                        defaut="ARRET",
                        into=("ARRET", "SANS", "MESSAGE"),
                        fr=tr("Vérification des bornes physiques de la loi de comportement MFRONT"),
                    ),
                    ALGO_CPLAN=SIMP(
                        statut="f", typ="TXM", defaut="DEBORST", into=("DEBORST", "ANALYTIQUE")
                    ),
                    RESI_INTE_MAXI=SIMP(statut="f", typ="R", defaut=1.0e-8),
                    ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=100),
                    SYME_MATR_TANG=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
                ),
                b_mfr_hm_hidden=BLOC(
                    condition="""'MFRONT' not in value("RELATION_KIT")""",
                    COMPOR_MFRONT=SIMP(
                        statut="c", typ=compor_mgis, fr=tr("objet ajouté automatiquement")
                    ),
                ),
            ),
            b_kit_meta=BLOC(
                condition="""value("RELATION").startswith('META_') and not value("RELATION").startswith('META_LEMA_ANI')""",
                fr=tr("nombre de phases metallurgiques"),
                RELATION_KIT=SIMP(
                    statut="o", typ="TXM", max=1, validators=NoRepeat(), into=("ACIER", "ZIRC")
                ),
            ),
            DEFORMATION=SIMP(
                statut="f",
                typ="TXM",
                defaut="PETIT",
                into=(
                    "PETIT",
                    "PETIT_REAC",
                    "GROT_GDEP",
                    "SIMO_MIEHE",
                    "GDEF_LOG",
                    "GREEN_LAGRANGE",
                ),
            ),
            RESI_CPLAN_MAXI=SIMP(
                statut="f",
                typ="R",
                fr=tr("Critère d'arret absolu pour assurer la condition de contraintes planes"),
            ),
            b_resi_cplan=BLOC(
                condition=""" not exists("RESI_CPLAN_MAXI") """,
                RESI_CPLAN_RELA=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1.0e-6,
                    fr=tr(
                        "Critère d'arret relatif pour assurer la condition de contraintes planes"
                    ),
                ),
            ),
            ITER_CPLAN_MAXI=SIMP(
                statut="f",
                typ="I",
                defaut=10,
                fr=tr("Nombre d'itérations maxi pour assurer la condition de contraintes planes"),
            ),
            # Parametres d'integration
            b_mfront_resi=BLOC(
                condition="""(equal_to("RELATION", 'MFRONT'))""",
                RESI_INTE_MAXI=SIMP(statut="f", typ="R", defaut=1.0e-8),
                ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=100),
            ),
            b_flua_resi=BLOC(
                condition="""is_in("RELATION", ('RGI_BETON','FLUA_PORO_BETON','FLUA_ENDO_PORO', 'RGI_BETON_BA',))""",
                RESI_INTE_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=-1),
            ),
            b_other_resi=BLOC(
                condition="""not is_in("RELATION", ('MFRONT','RGI_BETON','FLUA_PORO_BETON','FLUA_ENDO_PORO'))""",
                RESI_INTE_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ITER_INTE_MAXI=SIMP(statut="f", typ="I", defaut=20),
            ),
            b_redec_local=BLOC(
                condition="""is_in("DEFORMATION", ('PETIT','PETIT_REAC','GROT_GDEP'))""",
                fr=tr("Nombre de redécoupages internes du pas de temps"),
                ITER_INTE_PAS=SIMP(statut="f", typ="I", defaut=0),
            ),
            ALGO_INTE=SIMP(
                statut="f",
                typ="TXM",
                into=(
                    "ANALYTIQUE",
                    "SECANTE",
                    "DEKKER",
                    "NEWTON_1D",
                    "BRENT",
                    "NEWTON",
                    "NEWTON_RELI",
                    "NEWTON_PERT",
                    "RUNGE_KUTTA",
                    "SPECIFIQUE",
                    "SEMI_EXPLICITE",
                    "BASCULE_EXPLICITE",
                    "SANS_OBJET",
                ),
            ),
            b_type_matr=BLOC(
                condition="""not is_in("RELATION", ('RGI_BETON','FLUA_PORO_BETON','FLUA_ENDO_PORO', 'RGI_BETON_BA', 'ENDO_PORO_BETON'))""",
                TYPE_MATR_TANG=SIMP(statut="f", typ="TXM", into=("PERTURBATION", "VERIFICATION")),
                b_perturb=BLOC(
                    condition=""" (exists("TYPE_MATR_TANG")) """,
                    fr=tr(
                        "Calcul de la matrice tangente par perturbation, valeur de la perturbation"
                    ),
                    VALE_PERT_RELA=SIMP(statut="f", typ="R", defaut=1.0e-5),
                ),
                b_tangsec=BLOC(
                    condition=""" equal_to("TYPE_MATR_TANG", 'TANGENTE_SECANTE') """,
                    fr=tr("Modification evolutive de la matrice tangente/secante"),
                    SEUIL=SIMP(statut="f", typ="R", defaut=3.0),
                    AMPLITUDE=SIMP(statut="f", typ="R", defaut=1.5),
                    TAUX_RETOUR=SIMP(statut="f", typ="R", defaut=0.05),
                ),
                PARM_THETA=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0, defaut=1.0),
                b_radi=BLOC(
                    condition="""not exists("TYPE_MATR_TANG")""",
                    RESI_RADI_RELA=SIMP(statut="f", typ="R"),
                ),
            ),
            b_ntype_matr=BLOC(
                condition="""is_in("RELATION", ('RGI_BETON','FLUA_PORO_BETON','FLUA_ENDO_PORO', 'RGI_BETON_BA', 'ENDO_PORO_BETON'))""",
                TYPE_MATR_TANG=SIMP(
                    statut="f", typ="TXM", into=("MATR_ELAS", "MATR_ENDO"), defaut="MATR_ELAS"
                ),
                PARM_THETA=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0, defaut=1.0),
                b_radi=BLOC(
                    condition="""not exists("TYPE_MATR_TANG")""",
                    RESI_RADI_RELA=SIMP(statut="f", typ="R"),
                ),
            ),
            **opts
        )

    return mcfact


# to be used by a CommandSyntax from C++
C_COMPORTEMENT_MNL = FACT(statut="o", COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"))
C_COMPORTEMENT_TNL = FACT(statut="o", COMPORTEMENT=C_COMPORTEMENT("THER_NON_LINE"))
