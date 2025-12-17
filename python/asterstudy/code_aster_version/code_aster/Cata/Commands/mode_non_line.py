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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MODE_NON_LINE = OPER(
    nom="MODE_NON_LINE",
    op=61,
    sd_prod=table_container,
    fr=tr("Calcul des modes non-linéaires"),
    reentrant="f:ETAT_INIT:MODE_NON_LINE",
    reuse=SIMP(statut="c", typ=CO),
    ETAT_INIT=FACT(
        statut="o",
        max=1,
        regles=(UN_PARMI("MODE_LINE", "MODE_NON_LINE"),),
        MODE_LINE=SIMP(statut="f", typ=mode_meca, max=1),
        MODE_NON_LINE=SIMP(statut="f", typ=table_container, max=1),
        NUME_ORDRE=SIMP(statut="o", typ="I"),
        DIR_EVOLUTION=SIMP(statut="f", typ="I", defaut=-1, into=(-1, 1)),
        COEF_AMPL=SIMP(statut="f", typ="R", defaut=1),
    ),
    CHOC=FACT(
        statut="f",
        max="**",
        OBSTACLE=SIMP(statut="f", typ="TXM", into=("PLAN", "BI_PLAN", "CERCLE")),
        b_cercle=BLOC(
            condition="""equal_to("OBSTACLE", 'CERCLE')""",
            NOM_CMP=SIMP(
                statut="o", typ="TXM", min=2, max=2, validators=NoRepeat(), into=("DX", "DY", "DZ")
            ),
            ORIG_OBST=SIMP(statut="f", typ="R", defaut=(0.0, 0.0, 0.0), min=3, max=3),
        ),
        b_bi_plan=BLOC(
            condition="""equal_to("OBSTACLE", 'BI_PLAN')""",
            NOM_CMP=SIMP(statut="o", typ="TXM", min=1, max=1, into=("DX", "DY", "DZ")),
        ),
        b_plan=BLOC(
            condition="""equal_to("OBSTACLE", 'PLAN')""",
            NOM_CMP=SIMP(statut="o", typ="TXM", min=1, max=1, into=("DX", "DY", "DZ")),
        ),
        GROUP_NO=SIMP(statut="o", typ=grno, max=1),
        JEU=SIMP(statut="o", typ="R", max=1),
        RIGI_NOR=SIMP(statut="o", typ="R", max=1),
        PARA_REGUL=SIMP(statut="f", typ="R", defaut=0.005),
    ),
    MATR_RIGI=SIMP(statut="o", typ=(matr_asse_depl_r,)),
    MATR_MASS=SIMP(statut="o", typ=(matr_asse_depl_r,)),
    RESOLUTION=FACT(
        statut="o",
        max=1,
        METHODE=SIMP(statut="f", typ="TXM", defaut="EHMAN", into=("EHMAN",)),
        b_ehman=BLOC(
            condition="""equal_to("METHODE", 'EHMAN')""",
            NB_HARM_LINE=SIMP(statut="o", typ="I", val_min=1),
            NB_HARM_NONL=SIMP(statut="f", typ="I", defaut=201, val_min=1),
            NB_BRANCHE=SIMP(statut="o", typ="I", val_min=0),
            NB_PAS_MAN=SIMP(statut="o", typ="I", val_min=1),
            NB_ORDRE_MAN=SIMP(statut="f", typ="I", defaut=20, val_min=2),
            PREC_MAN=SIMP(statut="f", typ="R", defaut=1.0e-9, val_min=0.0e0),
            PREC_NEWTON=SIMP(statut="f", typ="R", defaut=1.0e-8, val_min=0.0e0),
            ITER_NEWTON_MAXI=SIMP(statut="f", typ="I", defaut=15, val_min=1),
            CRIT_ORDR_BIFURCATION=SIMP(statut="f", typ="I", defaut=3, val_min=1),
            RESI_RELA_BIFURCATION=SIMP(statut="f", typ="R", defaut=1.0e-4, val_min=0.0e0),
        ),
    ),
    SOLVEUR=C_SOLVEUR("MODE_NON_LINE"),
    INFO=SIMP(statut="f", typ="I", defaut=1),
)
