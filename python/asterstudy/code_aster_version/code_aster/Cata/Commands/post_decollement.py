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

# person_in_charge: georges-cc.devesa at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_DECOLLEMENT = MACRO(
    nom="POST_DECOLLEMENT",
    op=OPS("code_aster.MacroCommands.post_decollement_ops.post_decollement_ops"),
    sd_prod=table_sdaster,
    fr=tr("calcul du rapport de surfaces de contact radier/sol"),
    reentrant="n",
    RESULTAT=SIMP(statut="o", typ=(evol_noli, dyna_trans)),
    NOM_CHAM=SIMP(statut="f", typ="TXM", defaut="DEPL", into=C_NOM_CHAM_INTO(), max=1),
    NOM_CMP=SIMP(statut="f", typ="TXM", defaut="DZ", max=1),
    GROUP_MA=SIMP(statut="o", typ=grma, max=1),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
