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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_CONVERGENCE(command):
    assert command in ("MECA_NON_LINE", "SIMU_POINT_MAT", "THER_NON_LINE")
    if command in ("SIMU_POINT_MAT", "THER_NON_LINE"):
        mcfact = FACT(
            statut="d",
            regles=(AU_MOINS_UN("RESI_GLOB_MAXI", "RESI_GLOB_RELA", RESI_GLOB_RELA=1.0e-6),),
            RESI_GLOB_MAXI=SIMP(statut="f", typ="R"),
            RESI_GLOB_RELA=SIMP(statut="f", typ="R"),
            ITER_GLOB_MAXI=SIMP(statut="f", typ="I", defaut=10),
        )
    else:
        mcfact = FACT(
            statut="d",
            regles=(
                PRESENT_ABSENT(
                    "RESI_REFE_RELA", "RESI_GLOB_MAXI", "RESI_GLOB_RELA", "RESI_COMP_RELA"
                ),
                AU_MOINS_UN(
                    "RESI_REFE_RELA", "RESI_GLOB_MAXI", "RESI_GLOB_RELA", RESI_GLOB_RELA=1.0e-6
                ),
            ),
            b_refe_rela=BLOC(
                condition="""exists("RESI_REFE_RELA")""",
                regles=(
                    AU_MOINS_UN(
                        "SIGM_REFE",
                        "EPSI_REFE",
                        "FLUX_THER_REFE",
                        "EFFORT_REFE",
                        "MOMENT_REFE",
                        "FLUX_HYD1_REFE",
                        "FLUX_HYD2_REFE",
                        "VARI_REFE",
                        "DEPL_REFE",
                        "LAGR_REFE",
                        "PI_REFE",
                    ),
                ),
                EFFORT_REFE=SIMP(
                    statut="f", typ="R", fr=tr("Force de référence pour les éléments de structure.")
                ),
                MOMENT_REFE=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr("Moment de référence pour les éléments de structure."),
                ),
                SIGM_REFE=SIMP(statut="f", typ="R"),
                DEPL_REFE=SIMP(statut="f", typ="R"),
                EPSI_REFE=SIMP(statut="f", typ="R"),
                FLUX_THER_REFE=SIMP(statut="f", typ="R"),
                FLUX_HYD1_REFE=SIMP(statut="f", typ="R"),
                FLUX_HYD2_REFE=SIMP(statut="f", typ="R"),
                VARI_REFE=SIMP(statut="f", typ="R"),
                LAGR_REFE=SIMP(statut="f", typ="R"),
                PI_REFE=SIMP(statut="f", typ="R"),
            ),
            RESI_REFE_RELA=SIMP(statut="f", typ="R"),
            RESI_GLOB_MAXI=SIMP(statut="f", typ="R"),
            RESI_GLOB_RELA=SIMP(statut="f", typ="R"),
            RESI_COMP_RELA=SIMP(statut="f", typ="R"),
            ITER_GLOB_MAXI=SIMP(statut="f", typ="I", defaut=10),
            ITER_GLOB_ELAS=SIMP(statut="f", typ="I", defaut=25),
            ARRET=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
            VERIF=SIMP(statut="f", typ="TXM", defaut="TOUT", into=("TOUT", "AU_MOINS_UN")),
        )
    return mcfact
