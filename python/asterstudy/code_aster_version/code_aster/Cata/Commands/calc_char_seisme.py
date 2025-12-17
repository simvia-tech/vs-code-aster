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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_char_seisme_prod(MATR_MASS, **args):
    if args.get("__all__"):
        return (cham_no_sdaster,)

    if AsType(MATR_MASS) == matr_asse_depl_r:
        return cham_no_sdaster
    raise AsException("type de concept resultat non prevu")


CALC_CHAR_SEISME = OPER(
    nom="CALC_CHAR_SEISME",
    op=92,
    sd_prod=calc_char_seisme_prod,
    reentrant="n",
    fr=tr("Calcul du chargement sismique"),
    regles=(UN_PARMI("MONO_APPUI", "MODE_STAT"),),
    MATR_MASS=SIMP(statut="o", typ=matr_asse_depl_r, fr=tr("Matrice de masse")),
    DIRECTION=SIMP(statut="o", typ="R", max=6, fr=tr("Directions du séisme imposé")),
    MONO_APPUI=SIMP(statut="f", typ="TXM", into=("OUI",)),
    MODE_STAT=SIMP(statut="f", typ=(mode_meca,)),
    b_mode_stat=BLOC(
        condition="""exists("MODE_STAT")""",
        GROUP_NO=SIMP(statut="o", typ=grno, validators=NoRepeat(), max="**"),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
