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

# person_in_charge: david.haboussa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

RECA_WEIBULL = OPER(
    nom="RECA_WEIBULL",
    op=197,
    sd_prod=table_sdaster,
    fr=tr("Recaler les paramètres du modèle de WEIBULL sur des données expérimentales"),
    reentrant="n",
    LIST_PARA=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max=2, into=("SIGM_REFE", "M")),
    RESU=FACT(
        statut="o",
        max="**",
        regles=(
            EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_INST"),
            AU_MOINS_UN("TOUT", "GROUP_MA", "MAILLE"),
        ),
        EVOL_NOLI=SIMP(statut="o", typ=evol_noli),
        MODELE=SIMP(statut="o", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="o", typ=cham_mater),
        TEMPE=SIMP(statut="f", typ="R"),
        LIST_INST_RUPT=SIMP(statut="o", typ="R", validators=NoRepeat(), max="**"),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        b_acce_reel=BLOC(
            condition="""exists("INST") or exists("LIST_INST")""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""equal_to("CRITERE", 'RELATIF')""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""equal_to("CRITERE", 'ABSOLU')""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        COEF_MULT=SIMP(statut="f", typ="R", defaut=1.0e0),
    ),
    OPTION=SIMP(statut="f", typ="TXM", defaut="SIGM_ELGA", into=("SIGM_ELGA", "SIGM_ELMOY")),
    CORR_PLAST=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    METHODE=SIMP(statut="f", typ="TXM", defaut="MAXI_VRAI", into=("MAXI_VRAI", "REGR_LINE")),
    INCO_GLOB_RELA=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ITER_GLOB_MAXI=SIMP(statut="f", typ="I", defaut=10),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
