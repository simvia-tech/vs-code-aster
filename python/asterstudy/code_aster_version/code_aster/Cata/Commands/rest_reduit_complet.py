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


def post_champ_prod(RESULTAT_REDUIT, **args):
    if args.get("__all__"):
        return (evol_noli, evol_ther)

    if AsType(RESULTAT_REDUIT) == evol_noli:
        return evol_noli
    if AsType(RESULTAT_REDUIT) == evol_ther:
        return evol_ther


REST_REDUIT_COMPLET = OPER(
    nom="REST_REDUIT_COMPLET",
    op=54,
    sd_prod=post_champ_prod,
    reentrant="n",
    CHAM_GD=FACT(
        statut="o",
        max="**",
        NOM_CHAM=SIMP(
            statut="o",
            typ="TXM",
            validators=NoRepeat(),
            into=("DEPL", "TEMP", "SIEF_NOEU", "FLUX_NOEU", "SIEF_ELGA", "VARI_ELGA"),
        ),
        BASE=SIMP(statut="o", typ=mode_empi, max=1),
        OPERATION=SIMP(statut="o", typ="TXM", into=("GAPPY_POD", "COMB")),
        b_gappy=BLOC(
            condition="""equal_to("OPERATION", 'GAPPY_POD')""",
            GROUP_NO_INTERF=SIMP(statut="f", typ=grno, max=1),
        ),
    ),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    RESULTAT_REDUIT=SIMP(statut="o", typ=resultat_sdaster, max=1),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TABL_COOR_REDUIT=SIMP(statut="f", typ=table_sdaster),
    TITRE=SIMP(statut="f", typ="TXM"),
)
