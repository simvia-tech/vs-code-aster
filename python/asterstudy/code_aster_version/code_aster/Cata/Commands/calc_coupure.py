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

import sys
from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


CALC_COUPURE = MACRO(
    nom="CALC_COUPURE",
    op=OPS("code_aster.Commands.calc_coupure.calc_coupure_ops"),
    sd_prod=table_sdaster,
    fr=tr("Calcul du torseur résultant"),
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster),
    FORCE=SIMP(statut="f", typ="TXM", defaut="REAC_NODA", into=C_NOM_CHAM_INTO(phenomene="FORCE")),
    MODAL_SPECTRAL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    b_modspec=BLOC(
        condition="equal_to('MODAL_SPECTRAL', 'OUI')",
        COMB_MODE=SIMP(statut="o", typ="TXM", into=("CQC",)),
        AMOR_REDUIT=SIMP(statut="o", typ="R", max="**"),
        MODE_CORR=SIMP(statut="f", typ=mode_meca),
        SPEC_OSCI=SIMP(statut="o", typ=nappe_sdaster, max=3, min=3),
        ECHELLE=SIMP(statut="f", typ="R", defaut=(1, 1, 1), max=3, min=3),
        MODE_SIGNE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        COMB_DIRECTION=SIMP(statut="f", typ="TXM", defaut="QUAD", into=("QUAD", "NEWMARK")),
    ),
    COUPURE=FACT(
        statut="o",
        max="**",
        NOM=SIMP(statut="o", typ="TXM"),
        GROUP_NO=SIMP(statut="o", typ=grno, max="**"),
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, max="**"),
        POINT=SIMP(statut="o", typ="R", min=3, max=3),
        AXE_X=SIMP(statut="f", typ="R", defaut=(1, 0, 0), max=3, min=3),
        AXE_Y=SIMP(statut="f", typ="R", defaut=(0, 1, 0), max=3, min=3),
        AXE_Z=SIMP(statut="f", typ="R", defaut=(0, 0, 1), max=3, min=3),
        VERI_ORTHO=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    ),
)
