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

# person_in_charge: nicolas.sellenet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_champ_prod(RESULTAT, **args):
    if args.get("__all__"):
        return (resultat_sdaster,)

    if AsType(RESULTAT) is not None:
        return AsType(RESULTAT)
    raise AsException(
        "type de concept resultat non prevu : RESULTAT=%s (type %s)" % (RESULTAT, type(RESULTAT))
    )


CALC_CHAMP = OPER(
    nom="CALC_CHAMP",
    op=52,
    sd_prod=calc_champ_prod,
    reentrant="f:RESULTAT",
    fr=tr("Completer ou creer un resultat en calculant des champs par elements ou aux noeuds"),
    reuse=SIMP(statut="c", typ=CO),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster, fr=tr("Resultat d'une commande globale")),
    regles=(
        EXCLUS(
            "TOUT_ORDRE",
            "NUME_ORDRE",
            "INST",
            "FREQ",
            "NUME_MODE",
            "NOEUD_CMP",
            "LIST_INST",
            "LIST_FREQ",
            "LIST_ORDRE",
            "NOM_CAS",
        ),
        PRESENT_ABSENT("TOUT", "GROUP_MA"),
    ),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    NOM_CAS=SIMP(statut="f", typ="TXM"),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    TOUT=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI",),
        fr=tr("le calcul sera effectue sur toutes les mailles"),
    ),
    GROUP_MA=SIMP(
        statut="f",
        typ=grma,
        validators=NoRepeat(),
        max="**",
        fr=tr("le calcul ne sera effectue que sur ces groupes de mailles"),
    ),
    # Bloc lineaire
    b_lineaire=BLOC(
        condition="""is_type("RESULTAT") in (evol_elas,mode_meca,mode_meca_c,comb_fourier,mult_elas,fourier_elas,mode_flamb)""",
        regles=(
            AU_MOINS_UN(
                "CONTRAINTE",
                "DEFORMATION",
                "ENERGIE",
                "CRITERES",
                "VARI_INTERNE",
                "PROPRIETES",
                "FORCE",
                "CHAM_UTIL",
            ),
        ),
        CONTRAINTE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de contraintes et efforts generalises"),
            into=C_NOM_CHAM_INTO(phenomene="CONTRAINTE", categorie="lin"),
        ),
        DEFORMATION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de deformations"),
            into=C_NOM_CHAM_INTO(phenomene="DEFORMATION", categorie="lin"),
        ),
        ENERGIE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul d'energies"),
            into=C_NOM_CHAM_INTO(phenomene="ENERGIE", categorie="lin"),
        ),
        CRITERES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de criteres"),
            into=C_NOM_CHAM_INTO(phenomene="CRITERES", categorie="lin"),
        ),
        VARI_INTERNE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de variables internes"),
            into=C_NOM_CHAM_INTO(phenomene="VARI_INTERNE", categorie="lin"),
        ),
        PROPRIETES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de propriétés"),
            into=C_NOM_CHAM_INTO(phenomene="PROPRIETES", categorie="lin"),
        ),
        FORCE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour des forces nodales et des reactions nodales"),
            into=C_NOM_CHAM_INTO(phenomene="FORCE"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            fr=tr("Charges contenant les temperatures, les efforts repartis pour les poutres..."),
            regles=(EXCLUS("FONC_MULT", "COEF_MULT"),),
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
        CHAM_UTIL=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FORMULE", "CRITERE", "NORME"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("Nom du champ utilisé en donnée")),
            FORMULE=SIMP(
                statut="f", typ=formule, max="**", fr=tr("Formule permet d'obtenir le critère")
            ),
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("TRACE", "VMIS", "INVA_2"),
                fr=tr("Calcul d'un critère pré-défini"),
            ),
            NORME=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("L2", "FROBENIUS"),
                fr=tr("Calcul d'une norme pré-définie"),
            ),
            NUME_CHAM_RESU=SIMP(
                statut="o",
                typ="I",
                val_min=1,
                val_max=20,
                fr=tr("Numéro du champ produit. Exemple: 6 produit le champ UT06"),
            ),
        ),
    ),
    # Bloc dyna
    b_dyna=BLOC(
        condition="""is_type("RESULTAT") in (dyna_harmo,dyna_trans)""",
        regles=(
            AU_MOINS_UN(
                "CONTRAINTE",
                "DEFORMATION",
                "ENERGIE",
                "CRITERES",
                "VARI_INTERNE",
                "PROPRIETES",
                "ACOUSTIQUE",
                "FORCE",
                "CHAM_UTIL",
            ),
        ),
        CONTRAINTE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de contraintes et efforts generalises"),
            into=C_NOM_CHAM_INTO(phenomene="CONTRAINTE", categorie="lin"),
        ),
        DEFORMATION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de deformations"),
            into=C_NOM_CHAM_INTO(phenomene="DEFORMATION", categorie="lin"),
        ),
        ENERGIE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul d'energies"),
            into=C_NOM_CHAM_INTO(phenomene="ENERGIE", categorie="lin"),
        ),
        CRITERES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de criteres"),
            into=C_NOM_CHAM_INTO(phenomene="CRITERES", categorie="lin"),
        ),
        VARI_INTERNE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de variables internes"),
            into=C_NOM_CHAM_INTO(phenomene="VARI_INTERNE", categorie="lin"),
        ),
        PROPRIETES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de propriétés"),
            into=C_NOM_CHAM_INTO(phenomene="PROPRIETES", categorie="lin"),
        ),
        ACOUSTIQUE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de champs en acoustique"),
            into=C_NOM_CHAM_INTO(phenomene="ACOUSTIQUE"),
        ),
        FORCE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour des forces nodales et des reactions nodales"),
            into=C_NOM_CHAM_INTO(phenomene="FORCE"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            fr=tr("Charges contenant les temperatures, les efforts repartis pour les poutres..."),
            regles=(EXCLUS("FONC_MULT", "COEF_MULT"),),
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            # pour les chgt harmo
            PHAS_DEG=SIMP(statut="f", typ="R", defaut=0.0e0),
            PUIS_PULS=SIMP(statut="f", typ="I", defaut=0),
            FONC_MULT_C=SIMP(statut="f", typ=(fonction_c, formule_c)),
            COEF_MULT_C=SIMP(statut="f", typ="C"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
        CHAM_UTIL=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FORMULE", "CRITERE", "NORME"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("Nom du champ utilisé en donnée")),
            FORMULE=SIMP(
                statut="f", typ=formule, max="**", fr=tr("Formule permet d'obtenir le critère")
            ),
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("TRACE", "VMIS", "INVA_2"),
                fr=tr("Calcul d'un critère pré-défini"),
            ),
            NORME=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("L2", "FROBENIUS"),
                fr=tr("Calcul d'une norme pré-définie"),
            ),
            NUME_CHAM_RESU=SIMP(
                statut="o",
                typ="I",
                val_min=1,
                val_max=20,
                fr=tr("Numéro du champ produit. Exemple: 6 produit le champ UT06"),
            ),
        ),
    ),
    # Bloc non-lineaire
    b_non_lin=BLOC(
        condition="""is_type("RESULTAT") in (evol_noli,)""",
        regles=(
            AU_MOINS_UN(
                "SOUS_POINT",
                "CONTRAINTE",
                "DEFORMATION",
                "ENERGIE",
                "CRITERES",
                "VARI_INTERNE",
                "PROPRIETES",
                "HYDRAULIQUE",
                "FORCE",
                "CHAM_UTIL",
            ),
        ),
        SOUS_POINT=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de champs aux sous-points"),
            into=("DEPL_ELGA", "TEMP_ELGA"),
        ),
        CONTRAINTE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de contraintes et efforts generalises"),
            into=C_NOM_CHAM_INTO(phenomene="CONTRAINTE", categorie="nonlin"),
        ),
        DEFORMATION=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de deformations"),
            into=C_NOM_CHAM_INTO(phenomene="DEFORMATION", categorie="nonlin"),
        ),
        ENERGIE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul d'energies"),
            into=C_NOM_CHAM_INTO(phenomene="ENERGIE", categorie="nonlin"),
        ),
        CRITERES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de criteres"),
            into=C_NOM_CHAM_INTO(phenomene="CRITERES", categorie="nonlin"),
        ),
        VARI_INTERNE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de variables internes"),
            into=C_NOM_CHAM_INTO(phenomene="VARI_INTERNE", categorie="nonlin"),
        ),
        PROPRIETES=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de propriétés"),
            into=C_NOM_CHAM_INTO(phenomene="PROPRIETES", categorie="nonlin"),
        ),
        HYDRAULIQUE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de flux hydraulique"),
            into=C_NOM_CHAM_INTO(phenomene="HYDRAULIQUE", categorie="nonlin"),
        ),
        FORCE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour des forces nodales et des reactions nodales"),
            into=C_NOM_CHAM_INTO(phenomene="FORCE"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            fr=tr("Charges contenant les temperatures, les efforts repartis pour les poutres..."),
            regles=(EXCLUS("FONC_MULT", "COEF_MULT"),),
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            TYPE_CHARGE=SIMP(
                statut="f",
                typ="TXM",
                defaut="FIXE_CSTE",
                into=("FIXE_CSTE", "FIXE_PILO", "SUIV", "DIDI"),
            ),
        ),
        CHAM_UTIL=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FORMULE", "CRITERE", "NORME"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("Nom du champ utilisé en donnée")),
            FORMULE=SIMP(
                statut="f", typ=formule, max="**", fr=tr("Formule permet d'obtenir le critère")
            ),
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("TRACE", "VMIS", "INVA_2"),
                fr=tr("Calcul d'un critère pré-défini"),
            ),
            NORME=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("L2", "FROBENIUS"),
                fr=tr("Calcul d'une norme pré-définie"),
            ),
            NUME_CHAM_RESU=SIMP(
                statut="o",
                typ="I",
                val_min=1,
                val_max=20,
                fr=tr("Numéro du champ produit. Exemple: 6 produit le champ UT06"),
            ),
        ),
    ),
    # Bloc Thermique
    b_ther=BLOC(
        condition="""is_type("RESULTAT") in (evol_ther,fourier_ther,)""",
        regles=(AU_MOINS_UN("THERMIQUE", "CHAM_UTIL"),),
        THERMIQUE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de champs en thermique"),
            into=C_NOM_CHAM_INTO(phenomene="THERMIQUE"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            fr=tr("Charges contenant les temperatures, les efforts repartis pour les poutres..."),
            regles=(EXCLUS("FONC_MULT", "COEF_MULT"),),
            CHARGE=SIMP(statut="o", typ=(char_ther, char_cine_ther)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
        CHAM_UTIL=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FORMULE", "CRITERE", "NORME"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("Nom du champ utilisé en donnée")),
            FORMULE=SIMP(
                statut="f", typ=formule, max="**", fr=tr("Formule permet d'obtenir le critère")
            ),
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("TRACE", "VMIS", "INVA_2"),
                fr=tr("Calcul d'un critère pré-défini"),
            ),
            NORME=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("L2", "FROBENIUS"),
                fr=tr("Calcul d'une norme pré-définie"),
            ),
            NUME_CHAM_RESU=SIMP(
                statut="o",
                typ="I",
                val_min=1,
                val_max=20,
                fr=tr("Numéro du champ produit. Exemple: 6 produit le champ UT06"),
            ),
        ),
    ),
    # Bloc acoustique
    b_acou=BLOC(
        condition="""is_type("RESULTAT") in (acou_harmo,mode_acou,tran_gene,harm_gene)""",
        regles=(AU_MOINS_UN("ACOUSTIQUE", "CHAM_UTIL"),),
        ACOUSTIQUE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max="**",
            fr=tr("Options pour le calcul de champs en acoustique"),
            into=C_NOM_CHAM_INTO(phenomene="ACOUSTIQUE"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            fr=tr("Charges contenant les temperatures, les efforts repartis pour les poutres..."),
            regles=(EXCLUS("FONC_MULT", "COEF_MULT"),),
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            # pour les chgt harmo
            PHAS_DEG=SIMP(statut="f", typ="R", defaut=0.0e0),
            PUIS_PULS=SIMP(statut="f", typ="I", defaut=0),
            FONC_MULT_C=SIMP(statut="f", typ=(fonction_c, formule_c)),
            COEF_MULT_C=SIMP(statut="f", typ="C"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
        CHAM_UTIL=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FORMULE", "CRITERE", "NORME"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("Nom du champ utilisé en donnée")),
            FORMULE=SIMP(
                statut="f", typ=formule, max="**", fr=tr("Formule permet d'obtenir le critère")
            ),
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("TRACE", "VMIS", "INVA_2"),
                fr=tr("Calcul d'un critère pré-défini"),
            ),
            NORME=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                into=("L2", "FROBENIUS"),
                fr=tr("Calcul d'une norme pré-définie"),
            ),
            NUME_CHAM_RESU=SIMP(
                statut="o",
                typ="I",
                val_min=1,
                val_max=20,
                fr=tr("Numéro du champ produit. Exemple: 6 produit le champ UT06"),
            ),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2, 3)),
    PARALLELISME_TEMPS=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    TITRE=SIMP(statut="f", typ="TXM"),
)
