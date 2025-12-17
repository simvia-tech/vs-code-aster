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

LIRE_INTE_SPEC = MACRO(
    nom="LIRE_INTE_SPEC",
    op=OPS("code_aster.MacroCommands.lire_inte_spec_ops.lire_inte_spec_ops"),
    sd_prod=interspectre,
    fr=tr(
        "Lecture sur un fichier externe de fonctions complexes pour "
        "créer une matrice interspectrale"
    ),
    reentrant="n",
    UNITE=SIMP(statut="o", typ=UnitType(), inout="in"),
    FORMAT_C=SIMP(statut="f", typ="TXM", defaut="MODULE_PHASE", into=("REEL_IMAG", "MODULE_PHASE")),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="ASTER", into=("ASTER", "IDEAS")),
    NOM_PARA=SIMP(
        statut="f",
        typ="TXM",
        defaut="FREQ",
        into=(
            "DX",
            "DY",
            "DZ",
            "DRX",
            "DRY",
            "DRZ",
            "TEMP",
            "INST",
            "X",
            "Y",
            "Z",
            "EPSI",
            "FREQ",
            "PULS",
            "AMOR",
            "ABSC",
        ),
    ),
    NOM_RESU=SIMP(statut="f", typ="TXM", defaut="DSP"),
    INTERPOL=SIMP(statut="f", typ="TXM", max=2, into=("LIN", "LOG")),
    PROL_DROITE=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
