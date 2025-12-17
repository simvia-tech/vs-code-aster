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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_NAPPE = OPER(
    nom="DEFI_NAPPE",
    op=4,
    sd_prod=nappe_sdaster,
    fr=tr("Définir une fonction réelle de deux variables réelles"),
    reentrant="n",
    regles=(
        UN_PARMI("FONCTION", "DEFI_FONCTION"),
        EXCLUS("FONCTION", "NOM_PARA_FONC"),
        ENSEMBLE("NOM_PARA_FONC", "DEFI_FONCTION"),
    ),
    NOM_PARA=SIMP(statut="o", typ="TXM", into=C_PARA_FONCTION()),
    NOM_RESU=SIMP(statut="f", typ="TXM", defaut="TOUTRESU"),
    PARA=SIMP(statut="o", typ="R", max="**"),
    FONCTION=SIMP(statut="f", typ=fonction_sdaster, max="**"),
    NOM_PARA_FONC=SIMP(statut="f", typ="TXM", into=C_PARA_FONCTION()),
    DEFI_FONCTION=FACT(
        statut="f",
        max="**",
        VALE=SIMP(statut="o", typ="R", max="**"),
        INTERPOL=SIMP(
            statut="f",
            typ="TXM",
            max=2,
            defaut="LIN",
            into=("LIN", "LOG"),
            fr=tr("Type d'interpolation pour les abscisses et les ordonnées de la fonction."),
        ),
        PROL_DROITE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
        PROL_GAUCHE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
    ),
    INTERPOL=SIMP(
        statut="f",
        typ="TXM",
        max=2,
        defaut="LIN",
        into=("LIN", "LOG"),
        fr=tr("Type d'interpolation pour le paramètre de la nappe"),
    ),
    PROL_DROITE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    VERIF=SIMP(statut="f", typ="TXM", into=("CROISSANT",)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
