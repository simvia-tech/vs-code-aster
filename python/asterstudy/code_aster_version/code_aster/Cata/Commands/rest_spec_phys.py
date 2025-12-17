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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

REST_SPEC_PHYS = OPER(
    nom="REST_SPEC_PHYS",
    op=148,
    sd_prod=interspectre,
    reentrant="n",
    fr=tr("Calculer la réponse d'une structure dans la base physique"),
    regles=(AU_MOINS_UN("BASE_ELAS_FLUI", "MODE_MECA"), UN_PARMI("NOEUD", "GROUP_NO")),
    BASE_ELAS_FLUI=SIMP(statut="f", typ=melasflu_sdaster),
    b_fluide=BLOC(
        condition="""exists("BASE_ELAS_FLUI")""",
        VITE_FLUI=SIMP(statut="o", typ="R"),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    BANDE=SIMP(statut="f", typ="R", min=2, validators=NoRepeat(), max=2),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    INTE_SPEC_GENE=SIMP(statut="o", typ=interspectre),
    NOEUD=SIMP(statut="c", typ=no, max="**"),
    GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
    GROUP_MA=SIMP(statut="f", typ=grma, max="**"),
    NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
    NOM_CHAM=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max=7,
        into=("DEPL", "VITE", "ACCE", "EFGE_ELNO", "SIPO_ELNO", "SIGM_ELNO", "FORC_NODA"),
    ),
    MODE_STAT=SIMP(statut="f", typ=mode_meca),
    EXCIT=FACT(
        statut="f",
        regles=(EXCLUS("NOEUD", "GROUP_NO"), AU_MOINS_UN("NOEUD", "GROUP_NO")),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
    ),
    MOUVEMENT=SIMP(
        statut="f", typ="TXM", defaut="ABSOLU", into=("RELATIF", "ABSOLU", "DIFFERENTIEL")
    ),
    OPTION=SIMP(
        statut="f",
        typ="TXM",
        defaut="DIAG_DIAG",
        into=("DIAG_TOUT", "DIAG_DIAG", "TOUT_TOUT", "TOUT_DIAG"),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
