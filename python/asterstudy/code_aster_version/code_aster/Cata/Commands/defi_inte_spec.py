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

DEFI_INTE_SPEC = OPER(
    nom="DEFI_INTE_SPEC",
    op=115,
    sd_prod=interspectre,
    reentrant="n",
    fr=tr("Définit une matrice interspectrale"),
    DIMENSION=SIMP(statut="f", typ="I", defaut=1),
    regles=(UN_PARMI("PAR_FONCTION", "KANAI_TAJIMI", "CONSTANT"),),
    PAR_FONCTION=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("NUME_ORDRE_I", "NOEUD_I"),),
        NOEUD_I=SIMP(statut="f", typ=no, max=1),
        NUME_ORDRE_I=SIMP(statut="f", typ="I", max=1),
        b_nume_ordre_i=BLOC(
            condition="""exists("NUME_ORDRE_I")""", NUME_ORDRE_J=SIMP(statut="o", typ="I", max=1)
        ),
        b_noeud_i=BLOC(
            condition="""exists("NOEUD_I")""",
            NOEUD_J=SIMP(statut="o", typ=no, max=1),
            NOM_CMP_I=SIMP(statut="o", typ="TXM", max=1),
            NOM_CMP_J=SIMP(statut="o", typ="TXM", max=1),
        ),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c), max=1),
    ),
    KANAI_TAJIMI=FACT(
        statut="f",
        max="**",
        regles=(EXCLUS("VALE_R", "VALE_C"), UN_PARMI("NUME_ORDRE_I", "NOEUD_I")),
        NUME_ORDRE_I=SIMP(statut="f", typ="I", max=1),
        NOEUD_I=SIMP(statut="f", typ=no, max=1),
        b_nume_ordre_i=BLOC(
            condition="""exists("NUME_ORDRE_I")""", NUME_ORDRE_J=SIMP(statut="o", typ="I", max=1)
        ),
        b_noeud_i=BLOC(
            condition="""exists("NOEUD_I")""",
            NOEUD_J=SIMP(statut="o", typ=no, max=1),
            NOM_CMP_I=SIMP(statut="o", typ="TXM", max=1),
            NOM_CMP_J=SIMP(statut="o", typ="TXM", max=1),
        ),
        FREQ_MIN=SIMP(statut="f", typ="R", defaut=0.0e0),
        FREQ_MAX=SIMP(statut="f", typ="R", defaut=100.0),
        PAS=SIMP(statut="f", typ="R", defaut=1.0),
        AMOR_REDUIT=SIMP(statut="f", typ="R", defaut=0.6),
        FREQ_MOY=SIMP(statut="f", typ="R", defaut=5.0),
        VALE_R=SIMP(statut="f", typ="R"),
        VALE_C=SIMP(statut="f", typ="C"),
        INTERPOL=SIMP(statut="f", typ="TXM", max=2, defaut="LIN", into=("LIN", "LOG")),
        PROL_DROITE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
        PROL_GAUCHE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
    ),
    CONSTANT=FACT(
        statut="f",
        max="**",
        regles=(EXCLUS("VALE_R", "VALE_C"), UN_PARMI("NUME_ORDRE_I", "NOEUD_I")),
        NUME_ORDRE_I=SIMP(statut="f", typ="I", max=1),
        NOEUD_I=SIMP(statut="f", typ=no, max=1),
        b_nume_ordre_i=BLOC(
            condition="""exists("NUME_ORDRE_I")""", NUME_ORDRE_J=SIMP(statut="o", typ="I", max=1)
        ),
        b_noeud_i=BLOC(
            condition="""exists("NOEUD_I")""",
            NOEUD_J=SIMP(statut="o", typ=no, max=1),
            NOM_CMP_I=SIMP(statut="o", typ="TXM", max=1),
            NOM_CMP_J=SIMP(statut="o", typ="TXM", max=1),
        ),
        FREQ_MIN=SIMP(statut="f", typ="R", defaut=0.0e0),
        FREQ_MAX=SIMP(statut="f", typ="R", defaut=100.0),
        PAS=SIMP(statut="f", typ="R", defaut=1.0),
        VALE_R=SIMP(statut="f", typ="R"),
        VALE_C=SIMP(statut="f", typ="C"),
        INTERPOL=SIMP(statut="f", typ="TXM", max=2, defaut="LIN", into=("LIN", "LOG")),
        PROL_DROITE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
        PROL_GAUCHE=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
