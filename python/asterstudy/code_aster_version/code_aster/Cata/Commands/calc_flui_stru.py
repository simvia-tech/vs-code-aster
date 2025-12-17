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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_FLUI_STRU = OPER(
    nom="CALC_FLUI_STRU",
    op=144,
    sd_prod=melasflu_sdaster,
    reentrant="n",
    fr=tr("Calculer les paramètres modaux d'une structure soumise à un écoulement"),
    VITE_FLUI=FACT(
        statut="f",
        fr=tr("Définir la plage de vitesse fluide étudiée"),
        VITE_MIN=SIMP(statut="f", typ="R"),
        VITE_MAX=SIMP(statut="f", typ="R"),
        NB_POIN=SIMP(statut="f", typ="I"),
    ),
    BASE_MODALE=FACT(
        statut="o",
        regles=(AU_MOINS_UN("AMOR_REDUIT", "AMOR_UNIF", "AMOR_REDUIT_CONN"),),
        MODE_MECA=SIMP(statut="o", typ=mode_meca),
        NUME_ORDRE=SIMP(statut="f", typ="I", max="**"),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
        AMOR_UNIF=SIMP(statut="f", typ="R", val_min=0.0e00),
        AMOR_REDUIT_CONN=SIMP(statut="f", typ="R", max="**", val_min=0.0e00),
    ),
    TYPE_FLUI_STRU=SIMP(statut="o", typ=type_flui_stru),
    IMPRESSION=FACT(
        statut="f",
        fr=tr("Choix des informations à imprimer dans le fichier RESULTAT"),
        PARA_COUPLAGE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        DEFORMEE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    ),
    STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
)
