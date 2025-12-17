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

# person_in_charge: j-pierre.lefebvre at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def DEFIC_prod(self, ACTION, UNITE, **args):
    if args.get("__all__"):
        return (None, entier)

    if ACTION == "ASSOCIER" or ACTION == "RESERVER":
        if UNITE is not None:
            return
        else:
            return entier
    elif ACTION == "LIBERER":
        return
    else:
        raise AsException("ACTION non prevue : %s" % ACTION)


DEFI_FICHIER = MACRO(
    nom="DEFI_FICHIER",
    op=None,
    sd_prod=DEFIC_prod,
    reentrant="n",
    fr=tr("Ouvre ou ferme un fichier associé à un numéro d'unité logique"),
    ACTION=SIMP(statut="f", typ="TXM", into=("ASSOCIER", "LIBERER", "RESERVER"), defaut="ASSOCIER"),
    b_associer=BLOC(
        condition="""equal_to("ACTION", 'ASSOCIER')""",
        fr=tr("Paramètres pour l'ouverture du fichier"),
        regles=(AU_MOINS_UN("FICHIER", "UNITE"),),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="out"),
        FICHIER=SIMP(statut="f", typ="TXM", validators=LongStr(1, 255)),
        TYPE=SIMP(statut="f", typ="TXM", into=("ASCII", "BINARY", "LIBRE"), defaut="ASCII"),
        b_type_ascii=BLOC(
            condition="""equal_to("TYPE", 'ASCII')""",
            fr=tr("Paramètres pour le type ASCII"),
            ACCES=SIMP(statut="f", typ="TXM", into=("NEW", "APPEND", "OLD"), defaut="NEW"),
        ),
        b_type_autre=BLOC(
            condition="""not equal_to("TYPE", 'ASCII')""",
            fr=tr("Paramètres pour les types BINARY et LIBRE"),
            ACCES=SIMP(statut="f", typ="TXM", into=("NEW", "OLD"), defaut="NEW"),
        ),
    ),
    b_reserver=BLOC(
        condition="""equal_to("ACTION", 'RESERVER')""",
        fr=tr("Paramètres pour la réservation de l'unité du fichier"),
        regles=(AU_MOINS_UN("FICHIER", "UNITE"),),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="out"),
        FICHIER=SIMP(statut="f", typ="TXM", validators=LongStr(1, 255)),
        TYPE=SIMP(statut="f", typ="TXM", into=("ASCII",), defaut="ASCII"),
        ACCES=SIMP(statut="f", typ="TXM", into=("APPEND",), defaut="APPEND"),
    ),
    b_liberer=BLOC(
        condition="""equal_to("ACTION", 'LIBERER')""",
        fr=tr("Paramètres pour la fermeture du fichier"),
        regles=(UN_PARMI("FICHIER", "UNITE"),),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="out"),
        FICHIER=SIMP(statut="f", typ="TXM", validators=LongStr(1, 255)),
    ),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
