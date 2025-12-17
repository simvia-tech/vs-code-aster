# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2023 - EDF R&D - www.code-aster.org
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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_SQUELETTE = OPER(
    nom="DEFI_SQUELETTE",
    op=110,
    sd_prod=squelette,
    fr=tr("Définit un maillage pour visualiser les résultats d'une sous-structuration dynamique"),
    reentrant="n",
    regles=(
        UN_PARMI("CYCLIQUE", "MODELE_GENE", "MAILLAGE"),
        PRESENT_PRESENT("CYCLIQUE", "SECTEUR"),
        EXCLUS("SOUS_STRUC", "SECTEUR"),
        PRESENT_PRESENT("NOM_GROUP_MA", "MODELE_GENE"),
        PRESENT_PRESENT("NOM_GROUP_MA", "SOUS_STRUC"),
    ),
    CYCLIQUE=FACT(
        statut="f",
        regles=(UN_PARMI("MODE_CYCL", "MAILLAGE"), PRESENT_PRESENT("NB_SECTEUR", "MAILLAGE")),
        MODE_CYCL=SIMP(statut="f", typ=mode_cycl),
        NB_SECTEUR=SIMP(statut="f", typ="I", max=1),
        MAILLAGE=SIMP(statut="f", typ=maillage_sdaster),
    ),
    MODELE_GENE=SIMP(statut="f", typ=modele_gene),
    SQUELETTE=SIMP(statut="f", typ=squelette),
    RECO_GLOBAL=FACT(
        statut="f",
        max="**",
        regles=(
            EXCLUS("TOUT", "GROUP_NO_1"),
            PRESENT_PRESENT("GROUP_NO_1", "GROUP_NO_2"),
            PRESENT_PRESENT("GROUP_NO_1", "SOUS_STRUC_1"),
            PRESENT_PRESENT("GROUP_NO_2", "SOUS_STRUC_2"),
            PRESENT_PRESENT("SOUS_STRUC_1", "SOUS_STRUC_2"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_NO_1=SIMP(statut="f", typ=grno),
        SOUS_STRUC_1=SIMP(statut="f", typ="TXM"),
        GROUP_NO_2=SIMP(statut="f", typ=grno),
        SOUS_STRUC_2=SIMP(statut="f", typ="TXM"),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        DIST_REFE=SIMP(statut="f", typ="R"),
    ),
    NOM_GROUP_MA=FACT(
        statut="f",
        max="**",
        NOM=SIMP(statut="o", typ="TXM"),
        SOUS_STRUC=SIMP(statut="o", typ="TXM"),
        GROUP_MA=SIMP(statut="o", typ=grma),
    ),
    EXCLUSIF=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    MAILLAGE=SIMP(statut="f", typ=maillage_sdaster),
    GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    TRANS=SIMP(statut="f", typ="R", min=3, max=3),
    ANGL_NAUT=SIMP(statut="f", typ="R", min=3, max=3),
    SOUS_STRUC=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        NOM=SIMP(statut="o", typ="TXM"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),
    SECTEUR=FACT(
        statut="f",
        max="**",
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
