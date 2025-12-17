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


def compat_syntax(keywords):
    """Update keywords for compatibility"""

    # reuse
    if "reuse" in keywords and "RESULTAT" not in keywords:
        keywords["RESULTAT"] = keywords["reuse"]

    # change STATIONNAIRE to STAT
    if "ETAT_INIT" in keywords:
        if "STATIONNAIRE" in keywords["ETAT_INIT"]:
            del keywords["ETAT_INIT"]["STATIONNAIRE"]
            keywords["ETAT_INIT"]["STAT"] = "OUI"

    # fix that INCREMENT is mandatory for transitory
    if "TYPE_CALCUL" not in keywords:
        if "ETAT_INIT" not in keywords or "STAT" in keywords["ETAT_INIT"]:
            if "INCREMENT" not in keywords:
                keywords["TYPE_CALCUL"] = "STAT"
                if "ETAT_INIT" in keywords:
                    del keywords["ETAT_INIT"]

    # report default keywords
    if "TYPE_CALCUL" not in keywords or keywords["TYPE_CALCUL"] == "TRAN":
        if "ETAT_INIT" not in keywords:
            keywords["ETAT_INIT"] = {"STAT": "OUI"}

    if "NEWTON" in keywords:
        if "RECH_LINEAIRE" not in keywords:
            keywords["RECH_LINEAIRE"] = {}
        keys = ("RESI_LINE_RELA", "ITER_LINE_MAXI")
        for key in keys:
            if key in keywords["NEWTON"]:
                keywords["RECH_LINEAIRE"][key] = keywords["NEWTON"][key]
                del keywords["NEWTON"][key]

    if "PARM_THETA" in keywords:
        keywords["SCHEMA_TEMPS"] = {"SCHEMA": "HHT", "THETA": keywords["PARM_THETA"]}
        del keywords["PARM_THETA"]


THER_NON_LINE = MACRO(
    nom="THER_NON_LINE",
    op=OPS("code_aster.MacroCommands.ther_non_line_ops.ther_non_line_ops"),
    sd_prod=evol_ther,
    compat_syntax=compat_syntax,
    reentrant="f:RESULTAT",
    fr=tr(
        "Résoudre un problème thermique non linéaire (conditions limites ou comportement matériau)"
        " stationnaire ou transitoire"
    ),
    regles=ENSEMBLE("reuse", "RESULTAT"),
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(
        statut="f", typ=evol_ther, fr=tr("Objet qui sera enrichi des nouveaux instants calculés")
    ),
    MODELE=SIMP(statut="o", typ=(modele_sdaster)),
    CHAM_MATER=SIMP(statut="o", typ=(cham_mater)),
    CARA_ELEM=SIMP(statut="f", typ=(cara_elem)),
    COMPORTEMENT=C_COMPORTEMENT("THER_NON_LINE"),
    EVOL_THER_SECH=SIMP(statut="f", typ=evol_ther),
    EXCIT=FACT(
        statut="o",
        max="**",
        CHARGE=SIMP(statut="o", typ=(char_ther, char_cine_ther)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
    ),
    # -------------------------------------------------------------------
    AFFICHAGE=C_AFFICHAGE(),
    # -------------------------------------------------------------------
    METHODE=SIMP(
        statut="f", typ="TXM", defaut="NEWTON", into=("NEWTON", "MODELE_REDUIT", "NEWTON_KRYLOV")
    ),
    b_meth_newton=BLOC(
        condition="""equal_to("METHODE", 'NEWTON') or equal_to("METHODE", 'NEWTON_KRYLOV')""",
        NEWTON=FACT(
            statut="d",
            REAC_ITER=SIMP(statut="f", typ="I", defaut=0, val_min=0),
            REAC_INCR=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            PREDICTION=SIMP(statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE",)),
            MATRICE=SIMP(statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE",)),
        ),
        # -------------------------------------------------------------------
        RECH_LINEAIRE=C_RECH_LINEAIRE("THER_NON_LINE"),
    ),
    b_meth_rom=BLOC(
        condition="""equal_to("METHODE", 'MODELE_REDUIT')""",
        MODELE_REDUIT=FACT(
            statut="d",
            REAC_ITER=SIMP(statut="f", typ="I", defaut=0, val_min=0),
            REAC_INCR=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            BASE_PRIMAL=SIMP(statut="o", typ=mode_empi, max=1),
            DOMAINE_REDUIT=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            b_hr_cond=BLOC(
                condition="""(equal_to("DOMAINE_REDUIT", 'OUI'))""",
                GROUP_NO_INTERF=SIMP(statut="o", typ=grno, max=1),
                CORR_COMPLET=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
                b_hrcoor_cond=BLOC(
                    condition="""(equal_to("CORR_COMPLET", 'OUI'))""",
                    GROUP_NO_ENCASTRE=SIMP(statut="o", typ=grno, max=1),
                    COEF_PENA=SIMP(statut="f", typ="R", defaut=1.0e6),
                ),
            ),
        ),
    ),
    # -------------------------------------------------------------------
    TYPE_CALCUL=SIMP(statut="f", typ="TXM", into=("STAT", "TRAN"), defaut="TRAN"),
    # -------------------------------------------------------------------
    b_trans=BLOC(
        condition="""(equal_to("TYPE_CALCUL", 'TRAN'))""",
        # -------------------------------------------------------------------
        ETAT_INIT=FACT(
            statut="o",
            regles=(UN_PARMI("EVOL_THER", "CHAM_NO", "VALE", "STAT"), EXCLUS("NUME_ORDRE", "INST")),
            STAT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            EVOL_THER=SIMP(statut="f", typ=evol_ther),
            CHAM_NO=SIMP(statut="f", typ=cham_no_sdaster),
            VALE=SIMP(statut="f", typ="R"),
            b_evol=BLOC(
                condition="""exists("EVOL_THER")""",
                NUME_ORDRE=SIMP(statut="f", typ="I"),
                INST=SIMP(statut="f", typ="R"),
                b_inst=BLOC(
                    condition="""exists("INST")""",
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
        SCHEMA_TEMPS=FACT(
            max=1,
            statut="d",
            SCHEMA=SIMP(statut="f", min=1, max=1, typ="TXM", into=("HHT",), defaut="HHT"),
            b_hht=BLOC(
                condition="""equal_to("SCHEMA", 'HHT')""",
                THETA=SIMP(statut="f", typ="R", defaut=0.57, val_min=0.0, val_max=1.0),
            ),
        ),
    ),
    # -------------------------------------------------------------------
    b_stat=BLOC(
        condition="""(equal_to("TYPE_CALCUL", 'STAT'))""",
        ETAT_INIT=FACT(statut="d", STAT=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI")),
    ),
    # -------------------------------------------------------------------
    INCREMENT=C_INCREMENT(),
    # -------------------------------------------------------------------
    CONVERGENCE=C_CONVERGENCE("THER_NON_LINE"),
    # -------------------------------------------------------------------
    SOLVEUR=C_SOLVEUR("THER_NON_LINE"),
    # -------------------------------------------------------------------
    ARCHIVAGE=C_ARCHIVAGE(),
    # -------------------------------------------------------------------
    OBSERVATION=C_OBSERVATION("THERMIQUE"),
    # -------------------------------------------------------------------
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
