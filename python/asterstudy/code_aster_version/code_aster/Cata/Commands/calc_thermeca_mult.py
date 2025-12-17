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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_thermeca_mult_prod(self, RESU_THER, **args):
    if args.get("__all__"):
        return ([evol_elas], [None, evol_ther])

    if RESU_THER:
        self.type_sdprod(RESU_THER, evol_ther)

    return evol_elas


CALC_THERMECA_MULT = MACRO(
    nom="CALC_THERMECA_MULT",
    op=OPS("code_aster.MacroCommands.calc_thermeca_mult_ops.calc_thermeca_mult_ops"),
    sd_prod=calc_thermeca_mult_prod,
    reentrant="n",
    fr="Macro permettant la multiplication de resultats mecaniques ou thermiques issus de chocs thermiques unitaires",
    TEMP_FIN=SIMP(statut="o", typ="R"),
    TEMP_INIT=SIMP(statut="o", typ="R"),
    RESU_MECA_UNIT=SIMP(statut="o", typ=evol_elas),
    RESU_SUPL_THER=SIMP(statut="o", typ="TXM", into=("OUI", "NON")),
    b_resu_ther=BLOC(
        condition="equal_to('RESU_SUPL_THER', 'OUI')",
        fr=tr("Calcul du résultat thermique"),
        RESU_THER_UNIT=SIMP(statut="o", typ=evol_ther),
        RESU_THER=SIMP(statut="o", typ=CO),
    ),
)
