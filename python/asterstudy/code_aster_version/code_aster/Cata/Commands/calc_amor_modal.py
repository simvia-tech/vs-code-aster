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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_AMOR_MODAL = OPER(
    nom="CALC_AMOR_MODAL",
    op=172,
    sd_prod=listr8_sdaster,
    fr=tr("Création d'une liste d'amortissements modaux calculés selon la règle du RCC-G"),
    reentrant="n",
    regles=(
        EXCLUS("AMOR_RAYLEIGH", "ENER_SOL"),
        EXCLUS("AMOR_RAYLEIGH", "AMOR_INTERNE"),
        EXCLUS("AMOR_RAYLEIGH", "AMOR_SOL"),
        PRESENT_PRESENT("ENER_SOL", "AMOR_INTERNE"),
        PRESENT_PRESENT("ENER_SOL", "AMOR_SOL"),
    ),
    AMOR_RAYLEIGH=FACT(
        statut="f",
        AMOR_ALPHA=SIMP(statut="o", typ="R"),
        AMOR_BETA=SIMP(statut="o", typ="R"),
        MODE_MECA=SIMP(statut="o", typ=mode_meca),
    ),
    ENER_SOL=FACT(
        statut="f",
        regles=(
            UN_PARMI("GROUP_NO_RADIER", "GROUP_MA_RADIER"),
            PRESENT_ABSENT("COEF_GROUP", "FONC_GROUP"),
            #  Peut-on remplacer les deux règles suivantes par un ENSEMBLE_('KRX','KRY','KRZ')
            PRESENT_PRESENT("KRX", "KRY"),
            PRESENT_PRESENT("KRX", "KRZ"),
            PRESENT_ABSENT("COOR_CENTRE", "NOEUD_CENTRE"),
            PRESENT_ABSENT("GROUP_NO_CENTRE", "NOEUD_CENTRE"),
            PRESENT_ABSENT("GROUP_NO_CENTRE", "COOR_CENTRE"),
        ),
        METHODE=SIMP(statut="f", typ="TXM", defaut="DEPL", into=("DEPL", "RIGI_PARASOL")),
        MODE_MECA=SIMP(statut="o", typ=mode_meca),
        GROUP_NO_RADIER=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA_RADIER=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FONC_GROUP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_GROUP=SIMP(statut="f", typ="R", max="**"),
        KX=SIMP(statut="o", typ="R"),
        KY=SIMP(statut="o", typ="R"),
        KZ=SIMP(statut="o", typ="R"),
        KRX=SIMP(statut="f", typ="R"),
        KRY=SIMP(statut="f", typ="R"),
        KRZ=SIMP(statut="f", typ="R"),
        GROUP_NO_CENTRE=SIMP(statut="f", typ=grno),
        NOEUD_CENTRE=SIMP(statut="c", typ=no),
        COOR_CENTRE=SIMP(statut="f", typ="R", max=3),
    ),
    AMOR_INTERNE=FACT(
        statut="f",
        ENER_POT=SIMP(statut="o", typ=table_sdaster),
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
        AMOR_REDUIT=SIMP(statut="o", typ="R", max="**"),
    ),
    AMOR_SOL=FACT(
        statut="f",
        AMOR_REDUIT=SIMP(statut="f", typ="R", defaut=0.0e0),
        FONC_AMOR_GEO=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"),
        HOMOGENE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        SEUIL=SIMP(statut="f", typ="R", defaut=0.3),
    ),
    CORR_AMOR_NEGATIF=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "IGNORE", "OUI")),
    b_corr_amor=BLOC(
        condition="""equal_to("CORR_AMOR_NEGATIF", 'OUI')""",
        COEF_CORR_AMOR=SIMP(statut="o", typ="R", max=1, val_min=1.0e-3, val_max=1.0),
    ),
)
