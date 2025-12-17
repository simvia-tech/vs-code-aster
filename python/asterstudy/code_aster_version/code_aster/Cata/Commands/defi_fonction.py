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


def defi_fonction_prod(VALE, VALE_PARA, VALE_C, NOEUD_PARA, ABSCISSE, **args):
    if args.get("__all__"):
        return (fonction_sdaster, fonction_c)
    if VALE is not None:
        return fonction_sdaster
    if VALE_C is not None:
        return fonction_c
    if VALE_PARA is not None:
        return fonction_sdaster
    if ABSCISSE is not None:
        return fonction_sdaster
    if NOEUD_PARA is not None:
        return fonction_sdaster
    raise AsException("type de concept resultat non prevu")


DEFI_FONCTION = OPER(
    nom="DEFI_FONCTION",
    op=3,
    sd_prod=defi_fonction_prod,
    fr=tr("Définit une fonction réelle ou complexe d'une variable réelle"),
    reentrant="n",
    regles=(UN_PARMI("VALE", "VALE_C", "VALE_PARA", "NOEUD_PARA", "ABSCISSE"),),
    NOM_PARA=SIMP(statut="o", typ="TXM", into=C_PARA_FONCTION()),
    NOM_RESU=SIMP(statut="f", typ="TXM", defaut="TOUTRESU"),
    VALE=SIMP(
        statut="f",
        typ="R",
        min=2,
        max="**",
        fr=tr("Fonction réelle définie par une liste de couples " "(abscisse,ordonnée)"),
    ),
    ABSCISSE=SIMP(
        statut="f", typ="R", min=2, max="**", fr=tr("Liste d abscisses d une fonction réelle")
    ),
    VALE_C=SIMP(
        statut="f",
        typ="R",
        min=2,
        max="**",
        fr=tr(
            "Fonction complexe définie par une liste de triplets "
            "(absc, partie réelle, partie imaginaire)"
        ),
    ),
    VALE_PARA=SIMP(
        statut="f",
        typ=listr8_sdaster,
        fr=tr("Fonction réelle définie par deux concepts de type listr8"),
    ),
    b_vale_para=BLOC(
        condition="""exists("VALE_PARA")""", VALE_FONC=SIMP(statut="o", typ=listr8_sdaster)
    ),
    b_abscisse=BLOC(
        condition="""exists("ABSCISSE")""",
        ORDONNEE=SIMP(
            statut="o", typ="R", min=2, max="**", fr=tr("Liste d ordonnées d une fonction réelle")
        ),
    ),
    NOEUD_PARA=SIMP(
        statut="f",
        typ=no,
        max="**",
        fr=tr("Fonction réelle définie par une liste de noeuds et un maillage"),
    ),
    b_noeud_para=BLOC(
        condition="""exists("NOEUD_PARA")""",
        MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
        VALE_Y=SIMP(statut="o", typ="R", max="**"),
    ),
    INTERPOL=SIMP(statut="f", typ="TXM", max=2, defaut="LIN", into=("LIN", "LOG")),
    PROL_DROITE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    VERIF=SIMP(statut="f", typ="TXM", defaut="CROISSANT", into=("CROISSANT", "NON")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
    translation={
        "DEFI_FONCTION": "Define function",
        "VERIF": "Check order",
        "VALE_PARA": "List of X-coordinate",
        "VALE_FONC": "List of Y-coordinate",
        "NOEUD_PARA": "Nodes as X-coordinate",
        "VALE_Y": "Y-coordinates",
        "INTERPOL": "Interpolations",
        "VALE": "Coordinates",
        "VALE_C": "Complex coordinates",
    },
)
