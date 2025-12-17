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

# person_in_charge: ayaovi-dzifa.kudawoo at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

COMB_FOURIER = OPER(
    nom="COMB_FOURIER",
    op=161,
    sd_prod=comb_fourier,
    reentrant="n",
    fr=tr("Recombiner les modes de Fourier d'une SD Résultat dans des directions particulières"),
    RESULTAT=SIMP(statut="o", typ=(fourier_elas, fourier_ther)),
    ANGLE=SIMP(statut="o", typ="R", max="**"),
    NOM_CHAM=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max=6,
        into=("DEPL", "REAC_NODA", "SIEF_ELGA", "EPSI_ELNO", "SIGM_ELNO", "TEMP", "FLUX_ELNO"),
    ),
)
