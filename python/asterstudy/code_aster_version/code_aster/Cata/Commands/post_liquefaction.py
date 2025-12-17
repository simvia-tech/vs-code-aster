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

POST_LIQUEFACTION = MACRO(
    nom="POST_LIQUEFACTION",
    op=OPS("code_aster.MacroCommands.post_liquefaction_ops.post_liquefaction_ops"),
    sd_prod=evol_noli,
    reentrant="n",
    AXE=SIMP(
        statut="o", typ="TXM", into=("X", "Y", "Z"), max=1, fr=tr("Direction de la pesanteur")
    ),
    RESULTAT=SIMP(statut="o", typ=evol_noli, fr=tr("Resultat contenant les pressions")),
    CRITERE=SIMP(
        statut="o",
        typ="TXM",
        into=("DP_SIGV_REF", "DP_SIGM_REF", "DP", "P_SIGM"),
        max=1,
        fr=tr("Choix de la formule du critere de liquefaction"),
    ),
    b_def_ref=BLOC(
        condition="""equal_to('CRITERE', 'DP_SIGV_REF')""",
        fr=tr("Bloc associe aux donnees à l instant de reference pour le critere DP_SIGV_REF"),
        RESU_REF=SIMP(statut="o", typ=evol_noli),
        INST_REF=SIMP(statut="o", typ="R"),
    ),
    b_moy_ref=BLOC(
        condition="""equal_to('CRITERE', 'DP_SIGM_REF')""",
        fr=tr("Bloc associe aux donnees à l instant de reference pour le critere DP_SIGM_REF"),
        RESU_REF=SIMP(statut="o", typ=evol_noli),
        INST_REF=SIMP(statut="o", typ="R"),
    ),
    b_delta_ref=BLOC(
        condition="""equal_to('CRITERE', 'DP')""",
        fr=tr("Bloc associe aux donnees à l instant de reference pour le critere DP"),
        RESU_REF=SIMP(statut="o", typ=evol_noli),
        INST_REF=SIMP(statut="o", typ="R"),
    ),
)
