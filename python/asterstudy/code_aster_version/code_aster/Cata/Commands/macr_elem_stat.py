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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MACR_ELEM_STAT = OPER(
    nom="MACR_ELEM_STAT",
    op=86,
    sd_prod=macr_elem_stat,
    reentrant="f:MACR_ELEM",
    fr=tr("Définition d'un macro-élément pour l'analyse statique par sous-structuration"),
    regles=(
        AU_MOINS_UN("DEFINITION", "RIGI_MECA", "MASS_MECA", "CAS_CHARGE"),
        ENSEMBLE("DEFINITION", "EXTERIEUR"),
    ),
    reuse=SIMP(statut="c", typ=CO),
    MACR_ELEM=SIMP(statut="f", typ=macr_elem_stat, fr=tr("Résultat utilisé en cas de réécriture")),
    DEFINITION=FACT(
        statut="f",
        regles=(PRESENT_PRESENT("PROJ_MESU", "MODE_MESURE"),),
        MODELE=SIMP(statut="o", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        CHAR_MACR_ELEM=SIMP(statut="f", typ=char_meca),
        INST=SIMP(statut="f", typ="R", defaut=0.0e0),
        NMAX_CAS=SIMP(statut="f", typ="I", defaut=10),
        NMAX_CHAR=SIMP(statut="f", typ="I", defaut=10),
        PROJ_MESU=SIMP(statut="f", typ=(mode_gene, tran_gene, harm_gene), max=1),
        #           MODE_MESURE     =SIMP(statut='f',typ=( mode_meca,base_modale) ),
        MODE_MESURE=SIMP(statut="f", typ=mode_meca),
    ),
    EXTERIEUR=FACT(
        statut="f",
        regles=(AU_MOINS_UN("NOEUD", "GROUP_NO"),),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    ),
    RIGI_MECA=FACT(statut="f"),
    MASS_MECA=FACT(statut="f"),
    AMOR_MECA=FACT(statut="f"),
    CAS_CHARGE=FACT(
        statut="f",
        max="**",
        NOM_CAS=SIMP(statut="o", typ="TXM"),
        SUIV=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        CHARGE=SIMP(statut="f", typ=char_meca, validators=NoRepeat(), max="**"),
        INST=SIMP(statut="f", typ="R", defaut=0.0e0),
    ),
)
