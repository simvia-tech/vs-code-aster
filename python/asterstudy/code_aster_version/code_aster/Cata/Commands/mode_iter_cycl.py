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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MODE_ITER_CYCL = OPER(
    nom="MODE_ITER_CYCL",
    op=80,
    sd_prod=mode_cycl,
    fr=tr(
        "Calcul des modes propres d'une structure à répétitivité cyclique à partir"
        " d'une base de modes propres réels"
    ),
    reentrant="n",
    BASE_MODALE=SIMP(statut="o", typ=mode_meca),
    NB_MODE=SIMP(statut="f", typ="I"),
    NB_SECTEUR=SIMP(statut="o", typ="I"),
    LIAISON=FACT(
        statut="o",
        DROITE=SIMP(statut="o", typ="TXM"),
        GAUCHE=SIMP(statut="o", typ="TXM"),
        AXE=SIMP(statut="f", typ="TXM"),
    ),
    VERI_CYCL=FACT(
        statut="f",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF",)),
        DIST_REFE=SIMP(statut="f", typ="R"),
    ),
    CALCUL=FACT(
        statut="o",
        regles=(UN_PARMI("TOUT_DIAM", "NB_DIAM"),),
        TOUT_DIAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NB_DIAM=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        OPTION=SIMP(
            statut="f", typ="TXM", defaut="PLUS_PETITE", into=("PLUS_PETITE", "CENTRE", "BANDE")
        ),
        b_centre=BLOC(condition="""equal_to("OPTION", 'CENTRE')""", FREQ=SIMP(statut="o", typ="R")),
        b_bande=BLOC(
            condition="""equal_to("OPTION", 'BANDE')""",
            FREQ=SIMP(statut="o", typ="R", min=2, validators=NoRepeat(), max=2),
        ),
        #  NMAX_FREQ n a-t-il pas un sens qu avec OPTION CENTRE
        NMAX_FREQ=SIMP(statut="f", typ="I", defaut=10),
        PREC_SEPARE=SIMP(statut="f", typ="R", defaut=100.0),
        PREC_AJUSTE=SIMP(statut="f", typ="R", defaut=1.0e-6),
        NMAX_ITER=SIMP(statut="f", typ="I", defaut=50),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
