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

POST_DYNA_ALEA = MACRO(
    nom="POST_DYNA_ALEA",
    op=OPS("code_aster.MacroCommands.post_dyna_alea_ops.post_dyna_alea_ops"),
    sd_prod=table_sdaster,
    fr=tr(
        "Traitements statistiques de résultats de type interspectre " "et impression sur fichiers"
    ),
    reentrant="n",
    regles=(UN_PARMI("FRAGILITE", "INTERSPECTRE"),),
    FRAGILITE=FACT(
        statut="f",
        fr=tr("donnees pour courbe de fragilite"),
        max=1,
        regles=(UN_PARMI("VALE", "LIST_PARA"),),
        TABL_RESU=SIMP(statut="o", typ=table_sdaster),
        VALE=SIMP(statut="f", typ="R", min=1, validators=NoRepeat(), max="**"),
        LIST_PARA=SIMP(statut="f", typ=listr8_sdaster),
        METHODE=SIMP(statut="o", typ="TXM", into=("EMV", "REGRESSION")),
        a_methode=BLOC(
            condition="""equal_to("METHODE", 'REGRESSION')""", SEUIL=SIMP(statut="o", typ="R")
        ),
        b_methode=BLOC(
            condition="""equal_to("METHODE", 'EMV')""",
            SEUIL=SIMP(statut="f", typ="R"),
            AM_INI=SIMP(statut="o", typ="R"),
            BETA_INI=SIMP(statut="f", typ="R", defaut=0.3),
            FRACTILE=SIMP(
                statut="f",
                typ="R",
                min=1,
                validators=NoRepeat(),
                max="**",
                val_min=0.0,
                val_max=1.0,
            ),
            b_inte_spec_f=BLOC(
                condition="""exists("FRACTILE")""", NB_TIRAGE=SIMP(statut="f", typ="I")
            ),
        ),
    ),
    INTERSPECTRE=FACT(
        statut="f",
        max=1,
        fr=tr("donnees pour interspectre"),
        regles=(UN_PARMI("NOEUD_I", "NUME_ORDRE_I", "OPTION"),),
        INTE_SPEC=SIMP(statut="o", typ=interspectre),
        NUME_ORDRE_I=SIMP(statut="f", typ="I", max="**"),
        NOEUD_I=SIMP(statut="f", typ=no, max="**"),
        OPTION=SIMP(statut="f", typ="TXM", into=("DIAG", "TOUT")),
        b_nume_ordre_i=BLOC(
            condition="""exists("NUME_ORDRE_I")""", NUME_ORDRE_J=SIMP(statut="o", typ="I", max="**")
        ),
        b_noeud_i=BLOC(
            condition="""exists("NOEUD_I")""",
            NOEUD_J=SIMP(statut="o", typ=no, max="**"),
            NOM_CMP_I=SIMP(statut="o", typ="TXM", max="**"),
            NOM_CMP_J=SIMP(statut="o", typ="TXM", max="**"),
        ),
        FRACTILE=SIMP(
            statut="f",
            typ="R",
            defaut=0.5,
            val_min=0.0,
            val_max=1.0,
            fr=tr("fractile pour le calcul du facteur de pic"),
        ),
        MOMENT=SIMP(
            statut="f",
            typ="I",
            max="**",
            fr=tr("Moments spectraux en complément des cinq premiers"),
        ),
        DUREE=SIMP(statut="f", typ="R", fr=tr("durée de la phase forte pour facteur de peak")),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
