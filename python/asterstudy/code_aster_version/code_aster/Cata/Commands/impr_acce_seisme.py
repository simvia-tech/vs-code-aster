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

# person_in_charge: adrien.guilloux at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_ACCE_SEISME = MACRO(
    nom="IMPR_ACCE_SEISME",
    op=OPS("code_aster.MacroCommands.impr_acce_seisme_ops.impr_acce_seisme_ops"),
    reentrant="n",
    fr=tr("Impression et visualisation, post-traitement de séisme"),
    regles=(ENSEMBLE("FREQ_MIN", "FREQ_MAX")),
    TABLE=SIMP(statut="o", typ=table_sdaster),
    TITRE=SIMP(statut="o", typ="TXM"),
    NOCI_REFE=FACT(
        statut="f",
        max="**",
        regles=(
            AU_MOINS_UN(
                "AMAX",
                "VMAX",
                "DMAX",
                "INTE_ARIAS",
                "DUREE_PHASE_FORTE",
                "VITE_ABSO_CUMU",
                "ACCE_SUR_VITE",
            )
        ),
        AMAX=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        VMAX=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        DMAX=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        INTE_ARIAS=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        DUREE_PHASE_FORTE=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        VITE_ABSO_CUMU=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
        ACCE_SUR_VITE=SIMP(
            statut="f", typ="R", min=3, max=3, fr=tr("Valeur moyenne et intervalle de confiance")
        ),
    ),
    DUREE=SIMP(statut="f", typ="R"),
    SPEC_OSCI=SIMP(statut="o", typ=(fonction_sdaster)),
    SPEC_1_SIGMA=SIMP(statut="f", typ=(fonction_sdaster)),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    FREQ_MIN=SIMP(statut="f", typ="R"),
    FREQ_MAX=SIMP(statut="f", typ="R"),
    RATIO_HV=SIMP(statut="f", typ="R", val_min=0.0, fr=tr("Ratio H/V pour le spectre vertical")),
)
