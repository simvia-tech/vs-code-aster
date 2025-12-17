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


def post_cham_xfem_prod(RESULTAT, **args):
    if args.get("__all__"):
        return (evol_noli, mode_meca, evol_elas, evol_ther)

    if AsType(RESULTAT) == evol_noli:
        return evol_noli
    if AsType(RESULTAT) == mode_meca:
        return mode_meca
    if AsType(RESULTAT) == evol_elas:
        return evol_elas
    if AsType(RESULTAT) == evol_ther:
        return evol_ther

    raise AsException("type de concept resultat non prevu")


POST_CHAM_XFEM = OPER(
    nom="POST_CHAM_XFEM",
    op=196,
    sd_prod=post_cham_xfem_prod,
    reentrant="n",
    fr=tr(
        "Calcul des champs DEPL, SIEF_ELGA et VARI_ELGA sur le maillage de visualisation (fissuré)"
    ),
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster),
    MODELE_VISU=SIMP(statut="o", typ=modele_sdaster),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
