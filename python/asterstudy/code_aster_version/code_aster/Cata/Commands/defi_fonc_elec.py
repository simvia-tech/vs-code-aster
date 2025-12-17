# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2022 - EDF R&D - www.code-aster.org
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

# person_in_charge: nicolas.relun at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_FONC_ELEC = MACRO(
    nom="DEFI_FONC_ELEC",
    op=OPS("code_aster.MacroCommands.defi_fonc_elec_ops.defi_fonc_elec_ops"),
    sd_prod=fonction_sdaster,
    reentrant="n",
    fr=tr("Définir une fonction du temps intervenant dans le calcul des " "forces de LAPLACE"),
    regles=(UN_PARMI("COUR_PRIN", "COUR"), EXCLUS("COUR", "COUR_SECO")),
    FREQ=SIMP(statut="f", typ="R", defaut=50.0),
    SIGNAL=SIMP(statut="f", typ="TXM", defaut="COMPLET", into=("COMPLET", "CONTINU")),
    COUR=FACT(
        statut="f",
        max="**",
        fr=tr("Définition du courant de court-circuit"),
        regles=(UN_PARMI("PHI_CC_1", "INTC_CC_1"), UN_PARMI("PHI_CC_2", "INTC_CC_2")),
        INTE_CC_1=SIMP(statut="o", typ="R"),
        TAU_CC_1=SIMP(statut="o", typ="R"),
        PHI_CC_1=SIMP(statut="f", typ="R"),
        INTC_CC_1=SIMP(statut="f", typ="R"),
        INTE_CC_2=SIMP(statut="o", typ="R"),
        TAU_CC_2=SIMP(statut="o", typ="R"),
        PHI_CC_2=SIMP(statut="f", typ="R"),
        INTC_CC_2=SIMP(statut="f", typ="R"),
        INST_CC_INIT=SIMP(statut="o", typ="R"),
        INST_CC_FIN=SIMP(statut="o", typ="R"),
    ),
    COUR_PRIN=FACT(
        statut="f",
        fr=tr("Définition du courant de court-circuit avec réenclenchement"),
        regles=(UN_PARMI("PHI_CC_1", "INTC_CC_1"),),
        INTE_CC_1=SIMP(statut="o", typ="R"),
        TAU_CC_1=SIMP(statut="o", typ="R"),
        PHI_CC_1=SIMP(statut="f", typ="R"),
        INTC_CC_1=SIMP(statut="f", typ="R"),
        INTE_RENC_1=SIMP(statut="f", typ="R"),
        TAU_RENC_1=SIMP(statut="f", typ="R"),
        PHI_RENC_1=SIMP(statut="f", typ="R"),
        INST_CC_INIT=SIMP(statut="o", typ="R"),
        INST_CC_FIN=SIMP(statut="o", typ="R"),
        INST_RENC_INIT=SIMP(statut="f", typ="R", defaut=0.0e0),
        INST_RENC_FIN=SIMP(statut="f", typ="R", defaut=0.0e0),
    ),
    COUR_SECO=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Définition du courant de court-circuit avec un intervalle de temps différent de celui de COUR_PRIN"
        ),
        regles=(UN_PARMI("PHI_CC_2", "INTC_CC_2"),),
        INTE_CC_2=SIMP(statut="o", typ="R"),
        TAU_CC_2=SIMP(statut="o", typ="R"),
        PHI_CC_2=SIMP(statut="f", typ="R"),
        INTC_CC_2=SIMP(statut="f", typ="R"),
        INTE_RENC_2=SIMP(statut="f", typ="R"),
        TAU_RENC_2=SIMP(statut="f", typ="R"),
        PHI_RENC_2=SIMP(statut="f", typ="R"),
        DIST=SIMP(statut="f", typ="R", defaut=1.0e0),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
