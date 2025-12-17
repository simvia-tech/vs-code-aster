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

INFO_EXEC_ASTER = OPER(
    nom="INFO_EXEC_ASTER",
    op=35,
    sd_prod=table_sdaster,
    fr=tr("Récupère différentes informations propres à l'exécution en cours"),
    reentrant="n",
    regles=(),
    LISTE_INFO=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max=3,
        into=("TEMPS_RESTANT", "UNITE_LIBRE", "ETAT_UNITE"),
    ),
    b_etat_unite=BLOC(
        condition="""is_in('LISTE_INFO', 'ETAT_UNITE')""",
        regles=(UN_PARMI("UNITE", "FICHIER"),),
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            inout="in",
            fr=tr("Unité logique dont on veut obtenir l'état"),
        ),
        FICHIER=SIMP(
            statut="f",
            typ="TXM",
            validators=LongStr(1, 255),
            fr=tr("Nom du fichier dont on veut obtenir l'état"),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
