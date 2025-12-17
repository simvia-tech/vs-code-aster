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

MODI_MODELE_XFEM = OPER(
    nom="MODI_MODELE_XFEM",
    op=113,
    sd_prod=modele_sdaster,
    docu="U4.44.12-e",
    reentrant="n",
    fr=tr("Engendrer ou enrichir une structure de donnees en affectant les cham_gd associes"),
    regles=(UN_PARMI("FISSURE", "MODELE_THER")),
    reuse=SIMP(statut="c", typ=CO),
    MODELE_IN=SIMP(statut="o", typ=modele_sdaster, min=1, max=1),
    FISSURE=SIMP(statut="f", typ=fiss_xfem, min=1, max=99),
    MODELE_THER=SIMP(statut="f", typ=modele_sdaster, min=1, max=1),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    CONTACT=SIMP(
        statut="f", typ="TXM", defaut="SANS", into=("SANS", "STANDARD", "MORTAR"), min=1, max=1
    ),
    PRETRAITEMENTS=SIMP(statut="f", typ="TXM", defaut="AUTO", into=("AUTO", "SANS", "FORCE")),
    DECOUPE_FACETTE=SIMP(statut="f", typ="TXM", defaut="DEFAUT", into=("DEFAUT", "SOUS_ELEMENTS")),
)
