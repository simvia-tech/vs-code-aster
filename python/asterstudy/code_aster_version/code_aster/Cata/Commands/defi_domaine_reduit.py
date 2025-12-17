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
# person_in_charge: mickael.abbas at edf.fr
#
from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

#
DEFI_DOMAINE_REDUIT = OPER(
    nom="DEFI_DOMAINE_REDUIT",
    op=50,
    sd_prod=maillage_sdaster,
    reentrant="o:MAILLAGE",
    reuse=SIMP(statut="c", typ=CO),
    BASE_PRIMAL=SIMP(statut="o", typ=mode_empi, max=1),
    BASE_DUAL=SIMP(statut="o", typ=mode_empi, max=1),
    NOM_DOMAINE=SIMP(statut="o", typ="TXM", max=1),
    NB_COUCHE_SUPPL=SIMP(statut="f", typ="I", defaut=0),
    GROUP_NO_INTERF=SIMP(statut="o", typ="TXM", max=1),
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster, fr=tr("Maillage réutlisé en entrée")),
    DOMAINE_MINI=FACT(
        statut="f",
        max=1,
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    ),
    DOMAINE_MAXI=FACT(
        statut="f", max=1, GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**")
    ),
    CORR_COMPLET=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    p_correcteur=BLOC(
        condition="""(equal_to("CORR_COMPLET", 'OUI'))""",
        GROUP_NO_ENCASTRE=SIMP(statut="o", typ="TXM", max=1),
        NB_COUCHE_ENCASTRE=SIMP(statut="f", typ="I", defaut=0),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
