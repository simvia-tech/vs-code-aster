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

# Le calcul de la pression sur une interface est utilie en mécanique notamment
# en mécanique de contact, mécanique de la rupture,....
# Cette routine produit un cham_gd calculé à partir du tenseur de contraintes nodale SIEF_NOEU
# L'option n'existe que pour les éléments isoparamétriques mais elle pourra être étendue
# au frottement et aux éléments de structures si le besoin se manifeste.


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_pression_prod(self, RESULTAT, **args):
    if args.get("__all__"):
        return (
            evol_elas,
            evol_noli,
            evol_ther,
            mult_elas,
            mode_meca,
            mode_meca_c,
            dyna_trans,
            dyna_harmo,
            fourier_elas,
            fourier_ther,
            evol_varc,
            evol_char,
        )

    if AsType(RESULTAT) is not None:
        return AsType(RESULTAT)
    raise AsException("type de concept resultat non prevu")


CALC_PRESSION = MACRO(
    nom="CALC_PRESSION",
    op=OPS("code_aster.MacroCommands.calc_pression_ops.calc_pression_ops"),
    sd_prod=calc_pression_prod,
    reentrant="o:RESULTAT",
    fr="Calcul de la pression nodale sur une interface a partir de SIEF_NOEU. Cette option n existe que pour les éléments isoparamétriques.",
    reuse=SIMP(statut="c", typ=CO),
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli)),
    GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
    regles=(UN_PARMI("TOUT_ORDRE", "INST"),),
    INST=SIMP(statut="f", typ="R", max="**"),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    GEOMETRIE=SIMP(statut="f", typ="TXM", defaut="DEFORMEE", into=("INITIALE", "DEFORMEE")),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
