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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_FONC_FLUI = OPER(
    nom="DEFI_FONC_FLUI",
    op=142,
    sd_prod=fonction_sdaster,
    reentrant="n",
    fr=tr("Définit un profil de vitesse d'écoulement fluide le long d'une poutre"),
    regles=(UN_PARMI("NOEUD_INIT", "GROUP_NO_INIT"), UN_PARMI("NOEUD_FIN", "GROUP_NO_FIN")),
    MAILLAGE=SIMP(statut="o", typ=(maillage_sdaster)),
    NOEUD_INIT=SIMP(statut="c", typ=no, max=1),
    GROUP_NO_INIT=SIMP(statut="f", typ=grno, max=1),
    NOEUD_FIN=SIMP(statut="c", typ=no, max=1),
    GROUP_NO_FIN=SIMP(statut="f", typ=grno, max=1),
    VITE=FACT(
        statut="o",
        VALE=SIMP(statut="f", typ="R", defaut=1.0),
        PROFIL=SIMP(statut="o", typ="TXM", into=("UNIFORME", "LEONARD")),
        NB_BAV=SIMP(statut="f", typ="I", defaut=0, into=(0, 2, 3)),
    ),
    INTERPOL=SIMP(statut="f", typ="TXM", max=2, defaut="LIN", into=("LIN", "LOG")),
    PROL_DROITE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
