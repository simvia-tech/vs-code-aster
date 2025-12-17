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

# person_in_charge: jean-luc.flejou at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MACR_CARA_POUTRE = MACRO(
    nom="MACR_CARA_POUTRE",
    op=OPS("code_aster.MacroCommands.macr_cara_poutre_ops.macr_cara_poutre_ops"),
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr(
        "Calculer les caractéristiques d'une section transversale de "
        "poutre à partir d'un maillage 2D de la section"
    ),
    regles=(
        EXCLUS("SYME_Y", "GROUP_MA_BORD"),
        EXCLUS("SYME_Z", "GROUP_MA_BORD"),
        #            UN_PARMI('MAILLAGE', 'UNITE'),
    ),
    MAILLAGE=SIMP(statut="f", typ=maillage_sdaster, fr=tr("Nom du concept maillage")),
    b_maillage=BLOC(
        condition="""not exists("MAILLAGE")""",
        FORMAT=SIMP(
            statut="f", typ="TXM", defaut="MED", into=("ASTER", "MED"), fr=tr("Format du fichier")
        ),
    ),
    b_format_med=BLOC(
        condition=""" ( equal_to("FORMAT", 'MED') ) """,
        fr=tr("Informations complémentaires pour le format MED."),
        UNITE=SIMP(statut="f", typ=UnitType("med"), inout="in"),
    ),
    b_format_autre=BLOC(
        condition=""" ( not equal_to("FORMAT", 'MED') ) """,
        fr=tr("Informations complémentaires pour les autres formats."),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="in"),
    ),
    ORIG_INER=SIMP(
        statut="f",
        typ="R",
        max=3,
        defaut=(0.0e0, 0.0e0),
        fr=tr("Point par rapport auquel sont calculées les inerties"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TABLE_CARA=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
    SYME_Y=SIMP(statut="f", typ="TXM", into=("OUI",), fr=tr("demi maillage par rapport a y=0")),
    SYME_Z=SIMP(statut="f", typ="TXM", into=("OUI",), fr=tr("demi maillage par rapport a z=0")),
    GROUP_MA=SIMP(
        statut="f",
        typ=grma,
        validators=NoRepeat(),
        max="**",
        fr=tr("Calcul des caractéristiques équivalentes à plusieurs sections disjointes"),
    ),
    GROUP_MA_BORD=SIMP(
        statut="f",
        typ=grma,
        validators=NoRepeat(),
        max="**",
        fr=tr("Groupe(s) de mailles linéiques, bord(s) de(s) section(s)"),
    ),
    b_nom=BLOC(
        condition="""not (equal_to("TABLE_CARA", 'OUI') and exists("GROUP_MA"))""",
        NOM=SIMP(
            statut="o",
            typ="TXM",
            max=1,
            validators=LongStr(1, 8),
            fr=tr("Nom de la section, 8 caractères maximum."),
        ),
    ),
    b_gma_bord=BLOC(
        condition="""exists("GROUP_MA_BORD")""",
        fr=tr(" calcul des carac. mécaniques"),
        GROUP_NO=SIMP(
            statut="f",
            typ=grno,
            max="**",
            fr=tr(
                "Simplement pour empêcher des pivots nuls le cas échéant. "
                "Fournir un noeud quelconque par GROUP_MA"
            ),
        ),
        GROUP_MA_INTE=SIMP(
            statut="f",
            typ=grma,
            validators=NoRepeat(),
            max="**",
            fr=tr("groupes de mailles linéiques bordant des trous dans la section"),
        ),
    ),
    b_reseau=BLOC(
        condition="""(exists("GROUP_MA_BORD")) and (exists("GROUP_MA"))""",
        fr=tr(" calcul des coef de cisaillement équivalents a un reseau de poutres"),
        regles=(ENSEMBLE("LONGUEUR", "LIAISON", "MATERIAU"),),
        LONGUEUR=SIMP(statut="f", typ="R", fr=tr("Longueur du réseau de poutres")),
        MATERIAU=SIMP(
            statut="f", typ=mater_sdaster, fr=tr("Matériau élastique linéaire du réseau")
        ),
        LIAISON=SIMP(
            statut="f",
            typ="TXM",
            into=("ROTULE", "ENCASTREMENT"),
            fr=tr("type de conditions aux limites sur le plancher supérieur"),
        ),
    ),
)
