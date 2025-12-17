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

# person_in_charge: irmela.zentner at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_INTE_SPEC = OPER(
    nom="CALC_INTE_SPEC",
    op=120,
    sd_prod=interspectre,
    fr=tr("Calcul d'une matrice interspectrale à partir d'une fonction du temps"),
    reentrant="n",
    INST_INIT=SIMP(statut="f", typ="R", defaut=0.0e0),
    INST_FIN=SIMP(statut="o", typ="R"),
    DUREE_ANALYSE=SIMP(statut="f", typ="R"),
    DUREE_DECALAGE=SIMP(statut="f", typ="R"),
    NB_POIN=SIMP(statut="o", typ="I"),
    FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"),
    TITRE=SIMP(statut="f", typ="TXM", validators=NoRepeat()),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
