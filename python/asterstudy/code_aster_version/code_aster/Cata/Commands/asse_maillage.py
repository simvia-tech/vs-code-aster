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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def asse_maillage_prod(self, **args):
    if args.get("__all__"):
        return (super_mesh, maillage_sdaster)
    if args["OPERATION"] == "SOUS_STR":
        return super_mesh
    else:
        return maillage_sdaster


ASSE_MAILLAGE = OPER(
    nom="ASSE_MAILLAGE",
    op=105,
    sd_prod=asse_maillage_prod,
    fr=tr("Assembler deux maillages pour en former un nouveau"),
    reentrant="n",
    MAILLAGE_1=SIMP(statut="o", typ=maillage_sdaster),
    MAILLAGE_2=SIMP(statut="o", typ=maillage_sdaster),
    OPERATION=SIMP(statut="o", typ="TXM", into=("SOUS_STR", "SUPERPOSE", "COLLAGE")),
    b_collage=BLOC(
        condition="""equal_to("OPERATION", 'COLLAGE')""",
        COLLAGE=FACT(
            statut="o", GROUP_MA_1=SIMP(statut="o", typ=grma), GROUP_MA_2=SIMP(statut="o", typ=grma)
        ),
    ),
)
