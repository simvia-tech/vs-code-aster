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

# person_in_charge: serguei.potapov at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

LIRE_PLEXUS = OPER(
    nom="LIRE_PLEXUS",
    op=184,
    sd_prod=evol_char,
    fr=tr("Lire le fichier de résultats au format IDEAS produit par le logiciel EUROPLEXUS"),
    reentrant="n",
    regles=(UN_PARMI("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_INST", "LIST_ORDRE"),),
    UNITE=SIMP(statut="f", typ=UnitType(), defaut=19, inout="in"),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="IDEAS", into=("IDEAS",)),
    MAIL_PLEXUS=SIMP(statut="o", typ=maillage_sdaster),
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    b_prec_crit=BLOC(
        condition="""exists("LIST_INST") or exists("INST")""",
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
