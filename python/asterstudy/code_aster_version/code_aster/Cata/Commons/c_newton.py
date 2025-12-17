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

# person_in_charge: mickael.abbas at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_NEWTON(command="STAT_NON_LINE"):
    # TODO remove 'command' as soon as all features are supported
    assert command in ("MECA_NON_LINE", "STAT_NON_LINE")

    if command == "MECA_NON_LINE":
        mfact = FACT(
            statut="d",
            PREDICTION=SIMP(
                statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE", "ELASTIQUE")
            ),
            MATRICE=SIMP(statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE", "ELASTIQUE")),
            REAC_ITER=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            REAC_INCR=SIMP(statut="f", typ="I", defaut=1, val_min=0),
        )
    else:
        mfact = FACT(
            statut="d",
            REAC_INCR=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            PREDICTION=SIMP(
                statut="f", typ="TXM", into=("DEPL_CALCULE", "TANGENTE", "ELASTIQUE", "EXTRAPOLE")
            ),
            MATRICE=SIMP(statut="f", typ="TXM", defaut="TANGENTE", into=("TANGENTE", "ELASTIQUE")),
            PAS_MINI_ELAS=SIMP(statut="f", typ="R", val_min=0.0),
            REAC_ITER=SIMP(statut="f", typ="I", defaut=1, val_min=0),
            REAC_ITER_ELAS=SIMP(statut="f", typ="I", defaut=0, val_min=0),
            EVOL_NOLI=SIMP(statut="f", typ=evol_noli),
            MATR_RIGI_SYME=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        )

    return mfact
