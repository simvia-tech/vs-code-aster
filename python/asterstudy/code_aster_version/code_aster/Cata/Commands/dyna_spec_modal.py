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

DYNA_SPEC_MODAL = OPER(
    nom="DYNA_SPEC_MODAL",
    op=147,
    sd_prod=interspectre,
    fr=tr(
        "Calcul de la réponse par recombinaison modale d'une structure linéaire pour une excitation aléatoire"
    ),
    reentrant="n",
    BASE_ELAS_FLUI=SIMP(statut="o", typ=melasflu_sdaster),
    VITE_FLUI=SIMP(statut="o", typ="R"),
    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
    EXCIT=FACT(statut="o", INTE_SPEC_GENE=SIMP(statut="o", typ=interspectre)),
    OPTION=SIMP(statut="f", typ="TXM", defaut="TOUT", into=("TOUT", "DIAG")),
    TITRE=SIMP(statut="f", typ="TXM"),
)
