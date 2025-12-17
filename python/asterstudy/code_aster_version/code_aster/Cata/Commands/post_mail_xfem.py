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

POST_MAIL_XFEM = OPER(
    nom="POST_MAIL_XFEM",
    op=187,
    sd_prod=maillage_sdaster,
    reentrant="n",
    fr=tr("Crée un maillage se conformant à la fissure pour le post-traitement des éléments XFEM"),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    PREF_NOEUD_X=SIMP(statut="f", typ="TXM", defaut="NX", validators=LongStr(1, 2)),
    PREF_NOEUD_M=SIMP(statut="f", typ="TXM", defaut="NM", validators=LongStr(1, 2)),
    PREF_NOEUD_P=SIMP(statut="f", typ="TXM", defaut="NP", validators=LongStr(1, 2)),
    PREF_MAILLE_X=SIMP(statut="f", typ="TXM", defaut="MX", validators=LongStr(1, 2)),
    PREF_GROUP_CO=SIMP(statut="f", typ=grno, defaut="NFISSU"),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
