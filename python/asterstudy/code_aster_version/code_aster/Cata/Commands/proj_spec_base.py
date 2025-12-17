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

PROJ_SPEC_BASE = OPER(
    nom="PROJ_SPEC_BASE",
    op=146,
    sd_prod=interspectre,
    reentrant="n",
    fr=tr(
        "Projecter un ou plusieurs spectres de turbulence sur une (ou plusieurs) base(s) modale(s) "
    ),
    regles=(
        UN_PARMI("BASE_ELAS_FLUI", "MODE_MECA", "CHAM_NO"),
        UN_PARMI("TOUT", "GROUP_MA"),
        PRESENT_PRESENT("CHAM_NO", "MODELE_INTERFACE"),
    ),
    SPEC_TURB=SIMP(statut="o", typ=spectre_sdaster, validators=NoRepeat(), max="**"),
    TOUT_CMP=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    BASE_ELAS_FLUI=SIMP(statut="f", typ=melasflu_sdaster),
    b_fluide=BLOC(
        condition="""exists("BASE_ELAS_FLUI")""",
        VITE_FLUI=SIMP(statut="o", typ="R"),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    CHAM_NO=SIMP(statut="f", typ=cham_no_sdaster),
    FREQ_INIT=SIMP(statut="o", typ="R", val_min=0.0e0),
    FREQ_FIN=SIMP(statut="o", typ="R", val_min=0.0e0),
    NB_POIN=SIMP(statut="o", typ="I"),
    OPTION=SIMP(statut="f", typ="TXM", defaut="TOUT", into=("TOUT", "DIAG")),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    #  Quel est le type attendu derriere  MODELE_INTERFACE
    MODELE_INTERFACE=SIMP(statut="f", typ=modele_sdaster),
    VECT_X=SIMP(statut="f", typ="R", min=3, max=3),
    VECT_Y=SIMP(statut="f", typ="R", min=3, max=3),
    ORIG_AXE=SIMP(statut="f", typ="R", min=3, max=3),
    TITRE=SIMP(statut="f", typ="TXM"),
)
