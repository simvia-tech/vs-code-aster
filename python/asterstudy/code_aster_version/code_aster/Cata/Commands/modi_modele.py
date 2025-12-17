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

MODI_MODELE = OPER(
    nom="MODI_MODELE",
    op=103,
    sd_prod=modele_sdaster,
    reentrant="o:MODELE",
    fr=tr("Modifier la partition d'un modèle (parallélisme) "),
    reuse=SIMP(statut="c", typ=CO),
    MODELE=SIMP(statut="o", typ=modele_sdaster, min=1, max=1),
    DISTRIBUTION=FACT(
        statut="d",
        METHODE=SIMP(
            statut="f",
            typ="TXM",
            defaut="SOUS_DOMAINE",
            into=("MAIL_CONTIGU", "MAIL_DISPERSE", "CENTRALISE", "SOUS_DOMAINE", "GROUP_ELEM"),
        ),
        # remarque : "GROUP_ELEM" et "SOUS_DOMAINE" ne servent à rien car on ne modifie la distribution des éléments.
        #            Mais on les acceptent pour simplifier la programmation de calc_modes_multi_bandes.py
        b_dist_maille=BLOC(
            condition="""is_in("METHODE", ('MAIL_DISPERSE','MAIL_CONTIGU'))""",
            CHARGE_PROC0_MA=SIMP(statut="f", typ="I", defaut=100, val_min=0),
        ),
    ),
)
