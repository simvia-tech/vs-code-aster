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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

keywords = dict(
    FORMAT=SIMP(
        statut="f",
        typ="TXM",
        defaut="MED",
        into=("ASTER", "GIBI", "GMSH", "IDEAS", "MED"),
        fr=tr("Format du fichier : ASTER ou MED."),
    ),
    VERI_MAIL=FACT(
        statut="d",
        VERIF=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        APLAT=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ),
    b_format_autre=BLOC(
        condition=""" ( not equal_to("FORMAT", 'MED') ) """,
        fr=tr("Informations complémentaires pour la lecture ASTER."),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=20, inout="in", val_min=2),
    ),
    b_format_med=BLOC(
        condition=""" ( equal_to("FORMAT", 'MED') ) """,
        fr=tr("Informations complémentaires pour la lecture MED."),
        UNITE=SIMP(statut="f", typ=UnitType("med"), defaut=20, inout="in", val_min=2),
        # Pour une lecture dans un fichier MED, on peut préciser le nom sous lequel
        # le maillage y a été enregistré. Par défaut, on va le chercher sous le
        # nom du concept à créer.
        NOM_MED=SIMP(statut="f", typ="TXM", fr=tr("Nom du maillage dans le fichier MED.")),
        INFO_MED=SIMP(statut="f", typ="I", defaut=0, into=(0, 1)),
        PARTITIONNEUR=SIMP(
            statut="f",
            typ="TXM",
            defaut="SANS",
            into=("SANS", "PTSCOTCH"),
            fr=tr("Partitionner le maillage pour un calcul parallèle"),
        ),
    ),
    b_format_ideas=BLOC(
        condition=""" ( equal_to("FORMAT", 'IDEAS') ) """,
        CREA_GROUP_COUL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(0, 1, 2)),
    translation={
        "LIRE_MAILLAGE": "Read a mesh",
        "FORMAT": "Mesh file format",
        "UNITE": "Mesh file location",
        "VERI_MAIL": "Mesh check",
        "VERIF": "Check",
        "APLAT": "Flat criterion",
    },
)


def lire_maillage_sdprod(FORMAT, PARTITIONNEUR, **args):
    if args.get("__all__"):
        return (maillage_sdaster, maillage_p)

    if FORMAT == "MED" and PARTITIONNEUR != "SANS":
        return maillage_p

    return maillage_sdaster


LIRE_MAILLAGE = OPER(
    nom="LIRE_MAILLAGE",
    op=1,
    sd_prod=lire_maillage_sdprod,
    fr=tr("Crée un maillage par lecture d'un fichier"),
    reentrant="n",
    **keywords
)
