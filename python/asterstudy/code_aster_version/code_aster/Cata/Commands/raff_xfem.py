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

# person_in_charge: sam.cuvilliez at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def raff_xfem_prod(self, TYPE, **args):
    if args.get("__all__"):
        return (cham_no_sdaster, carte_sdaster)

    if TYPE == "DISTANCE":
        return cham_no_sdaster
    elif TYPE == "ZONE":
        return carte_sdaster
    else:
        raise AsException("type de concept non prevu")


RAFF_XFEM = MACRO(
    nom="RAFF_XFEM",
    op=OPS("code_aster.MacroCommands.raff_xfem_ops.raff_xfem_ops"),
    sd_prod=raff_xfem_prod,
    fr=tr("Calcul d'un indicateur pour le raffinement"),
    reentrant="n",
    TYPE=SIMP(statut="f", typ="TXM", into=("DISTANCE", "ZONE"), defaut="DISTANCE"),
    FISSURE=SIMP(statut="o", typ=fiss_xfem, min=1, max="**"),
    b_zone=BLOC(
        condition="""equal_to("TYPE", 'ZONE') """,
        fr=tr("Paramètres de la zone"),
        RAYON=SIMP(statut="o", typ="R", val_min=0.0),
    ),
)
