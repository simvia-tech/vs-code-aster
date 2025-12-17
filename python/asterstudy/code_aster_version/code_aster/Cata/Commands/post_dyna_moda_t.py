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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_DYNA_MODA_T = OPER(
    nom="POST_DYNA_MODA_T",
    op=130,
    sd_prod=table_sdaster,
    fr=tr("Post-traiter les résultats en coordonnées généralisées produit par DYNA_TRAN_MODAL"),
    reentrant="n",
    regles=(UN_PARMI("CHOC", "RELA_EFFO_DEPL"),),
    RESU_GENE=SIMP(statut="o", typ=tran_gene),
    CHOC=FACT(
        statut="f",
        max="**",
        fr=tr("Analyse des non linéarités de choc"),
        INST_INIT=SIMP(statut="f", typ="R", defaut=-1.0),
        INST_FIN=SIMP(statut="f", typ="R", defaut=999.0),
        NB_BLOC=SIMP(statut="f", typ="I", defaut=1),
        SEUIL_FORCE=SIMP(statut="f", typ="R", defaut=0.0e0),
        DUREE_REPOS=SIMP(statut="f", typ="R", defaut=0.0e0),
        OPTION=SIMP(statut="f", typ="TXM", defaut="USURE", into=("IMPACT", "USURE")),
        NB_CLASSE=SIMP(statut="f", typ="I", defaut=10),
    ),
    RELA_EFFO_DEPL=FACT(
        statut="f",
        fr=tr("Analyse des relationsnon linéaires effort-déplacement"),
        GROUP_NO=SIMP(statut="o", typ=grno),
        NOM_CMP=SIMP(statut="o", typ="TXM"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
