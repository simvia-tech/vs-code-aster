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

POST_FATI_ALEA = OPER(
    nom="POST_FATI_ALEA",
    op=170,
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr(
        "Calculer le dommage de fatigue subi par une structure soumise à une sollicitation de type aléatoire"
    ),
    regles=(
        ENSEMBLE("MOMENT_SPEC_0", "MOMENT_SPEC_2"),
        PRESENT_PRESENT("MOMENT_SPEC_4", "MOMENT_SPEC_0"),
        UN_PARMI("TABL_POST_ALEA", "MOMENT_SPEC_0"),
    ),
    MOMENT_SPEC_0=SIMP(statut="f", typ="R"),
    MOMENT_SPEC_2=SIMP(statut="f", typ="R"),
    MOMENT_SPEC_4=SIMP(statut="f", typ="R"),
    TABL_POST_ALEA=SIMP(statut="f", typ=table_sdaster),
    COMPTAGE=SIMP(statut="o", typ="TXM", into=("PIC", "NIVEAU")),
    DUREE=SIMP(statut="f", typ="R", defaut=1.0),
    CORR_KE=SIMP(statut="f", typ="TXM", into=("RCCM",)),
    DOMMAGE=SIMP(statut="o", typ="TXM", into=("WOHLER",)),
    MATER=SIMP(statut="o", typ=mater_sdaster),
    TITRE=SIMP(statut="f", typ="TXM"),
)
