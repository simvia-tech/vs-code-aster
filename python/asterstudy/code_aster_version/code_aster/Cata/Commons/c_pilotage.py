# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2024 - EDF R&D - www.code-aster.org
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

# person_in_charge: kyrylo.kazymyrenko at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_PILOTAGE():
    return FACT(
        statut="f",
        regles=(EXCLUS("NOEUD", "GROUP_NO"), PRESENT_ABSENT("TOUT", "GROUP_MA")),
        TYPE=SIMP(
            statut="o",
            typ="TXM",
            into=(
                "DDL_IMPO",
                "LONG_ARC",
                "PRED_ELAS",
                "DEFORMATION",
                "ANA_LIM",
                "SAUT_IMPO",
                "SAUT_LONG_ARC",
            ),
        ),
        COEF_MULT=SIMP(statut="f", typ="R", defaut=1.0e0),
        EVOL_PARA=SIMP(
            statut="f", typ="TXM", defaut="SANS", into=("SANS", "CROISSANT", "DECROISSANT")
        ),
        ETA_PILO_MAX=SIMP(statut="f", typ="R"),
        ETA_PILO_MIN=SIMP(statut="f", typ="R"),
        ETA_PILO_R_MAX=SIMP(statut="f", typ="R"),
        ETA_PILO_R_MIN=SIMP(statut="f", typ="R"),
        PROJ_BORNES=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        b_long_arc=BLOC(
            condition="""equal_to("TYPE", 'LONG_ARC') or equal_to("TYPE", 'SAUT_LONG_ARC')""",
            SELECTION=SIMP(
                statut="f",
                typ="TXM",
                defaut="NORM_INCR_DEPL",
                into=("RESIDU", "MIXTE", "ANGL_INCR_DEPL", "NORM_INCR_DEPL"),
            ),
        ),
        b_other=BLOC(
            condition="""not equal_to("TYPE", 'LONG_ARC') and not equal_to("TYPE", 'SAUT_LONG_ARC')""",
            SELECTION=SIMP(
                statut="f",
                typ="TXM",
                defaut="NORM_INCR_DEPL",
                into=("RESIDU", "MIXTE", "NORM_INCR_DEPL"),
            ),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FISSURE=SIMP(statut="f", typ=fiss_xfem, validators=NoRepeat(), max="**"),
        NOEUD=SIMP(statut="f", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
        DIRE_PILO=SIMP(statut="f", typ="TXM", max="**"),
    )
