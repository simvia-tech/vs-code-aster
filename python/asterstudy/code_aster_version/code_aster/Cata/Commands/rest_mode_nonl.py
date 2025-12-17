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


def rest_mode_nonl_prod(TYPE_RESU, **args):
    if args.get("__all__"):
        return (dyna_trans, mode_meca)
    if TYPE_RESU == "DYNA_TRANS":
        return dyna_trans
    elif TYPE_RESU == "MODE_MECA":
        return mode_meca
    raise AsException("type de concept resultat non prevu")


REST_MODE_NONL = OPER(
    nom="REST_MODE_NONL",
    op=63,
    sd_prod=rest_mode_nonl_prod,
    reentrant="n",
    fr=tr("Post traitement de mode_non_line : récuperation résultats"),
    MODE_NON_LINE=SIMP(statut="o", typ=table_container, max=1),
    TYPE_RESU=SIMP(
        statut="f", typ="TXM", into=("MODE_MECA", "DYNA_TRANS"), defaut="DYNA_TRANS", max=1
    ),
    NUME_ORDRE=SIMP(statut="o", typ="I", max=1),
    b_dyna_trans=BLOC(
        condition="""equal_to("TYPE_RESU", 'DYNA_TRANS')""",
        NB_INST=SIMP(statut="f", typ="I", max=1, defaut=512),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
