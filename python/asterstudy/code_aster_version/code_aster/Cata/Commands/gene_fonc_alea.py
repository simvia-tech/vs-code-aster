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

# person_in_charge: irmela.zentner at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

GENE_FONC_ALEA = OPER(
    nom="GENE_FONC_ALEA",
    op=118,
    sd_prod=interspectre,
    fr=tr("Génération de la fonction temporelle à partir d une matrice interspectrale"),
    reentrant="n",
    INTE_SPEC=SIMP(statut="o", typ=interspectre),
    NUME_VITE_FLUI=SIMP(statut="f", typ="I"),
    INTERPOL=SIMP(statut="f", typ="TXM", defaut="OUI", into=("NON", "OUI")),
    b_interpol_oui=BLOC(
        condition="""equal_to("INTERPOL", 'OUI') """,
        fr=tr("Parametres cas interpolation autorisee"),
        DUREE_TIRAGE=SIMP(statut="f", typ="R"),
        FREQ_INIT=SIMP(statut="f", typ="R"),
        FREQ_FIN=SIMP(statut="f", typ="R"),
    ),
    NB_POIN=SIMP(statut="f", typ="I"),
    NB_TIRAGE=SIMP(statut="f", typ="I", defaut=1),
    INIT_ALEA=SIMP(statut="f", typ="I"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
