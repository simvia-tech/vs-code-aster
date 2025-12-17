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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MODI_BASE_MODALE = OPER(
    nom="MODI_BASE_MODALE",
    op=149,
    sd_prod=mode_meca,
    reentrant="f:BASE",
    fr=tr("Définir la base modale d'une structure sous écoulement"),
    regles=(EXCLUS("AMOR_UNIF", "AMOR_REDUIT"),),
    reuse=SIMP(statut="c", typ=CO),
    BASE=SIMP(statut="o", typ=mode_meca),
    BASE_ELAS_FLUI=SIMP(statut="o", typ=melasflu_sdaster),
    NUME_VITE_FLUI=SIMP(statut="o", typ="I"),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
    AMOR_UNIF=SIMP(statut="f", typ="R"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
