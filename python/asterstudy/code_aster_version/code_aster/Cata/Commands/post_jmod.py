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

from ..Language.Syntax import *
from ..Language.DataStructure import *
from ..Commons import *

POST_JMOD = MACRO(
    nom="POST_JMOD",
    op=OPS("code_aster.MacroCommands.post_jmod_ops.post_jmod_ops"),
    sd_prod=table_sdaster,
    fr=tr("calcul de J-integrale"),
    reentrant="n",
    FOND_FISS=SIMP(statut="f", typ=fond_fissure),
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli), fr=tr("Displacement results")),
    NB_COUCHES=SIMP(statut="f", typ="I", defaut=4),
    OPTION=SIMP(statut="f", typ="TXM", max="**", into=("J", "JMOD"), default="JMOD"),
    ETAT_INIT=FACT(statut="f", EPSI=SIMP(statut="o", typ=(cham_no_sdaster, cham_elem))),
    GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    NB_POINT_FOND=SIMP(statut="f", typ="I"),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    b_acce_reel=BLOC(
        condition="""(exists("INST"))""", PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6)
    ),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    regles=(EXCLUS("INST", "NUME_ORDRE"),),
    TITRE=SIMP(statut="f", typ="TXM", defaut="POST_JMOD"),
)
