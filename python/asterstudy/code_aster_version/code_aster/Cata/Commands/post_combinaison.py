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


def post_combinaison_prod(self, TABLE_COEF_FIN=None, **args):
    """Define the type of the result."""
    if TABLE_COEF_FIN != None:
        self.type_sdprod(TABLE_COEF_FIN, table_sdaster)
    combination_type = args.get("TYPE_COMB")
    if combination_type == "RESULTAT":
        return mult_elas
    elif combination_type == "TABLE":
        return table_sdaster


POST_COMBINAISON = MACRO(
    nom="POST_COMBINAISON",
    op=OPS("code_aster.MacroCommands.post_combinaison_ops.post_combinaison_ops"),
    sd_prod=post_combinaison_prod,
    fr=tr("Combinaison de grandeurs physiques issues de différents calculs mécaniques"),
    TABLE_COEF=SIMP(statut="o", typ=table_sdaster),
    TABLE_COEF_RESU=SIMP(statut="f", typ=CO, defaut=None),
    TYPE_COMB=SIMP(statut="o", typ="TXM", into=("TABLE", "RESULTAT")),
    b_resultats=BLOC(
        condition="equal_to('TYPE_COMB', 'RESULTAT')",
        regles=(PRESENT_ABSENT("TOUT", "GROUP_MA", "GROUP_NO"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, max="**", validators=NoRepeat()),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**", validators=NoRepeat()),
        MODELE=SIMP(statut="o", typ=modele_sdaster, fr=tr("Modèle support en sortie")),
        NOM_CHAM=SIMP(statut="f", typ="TXM", fr=tr("Nom du champ à combiner"), max="**"),
        AFFE=FACT(
            statut="o",
            max="**",
            NOM_CAS=SIMP(statut="o", typ="TXM"),
            RESULTAT=SIMP(
                statut="o",
                typ=(mult_elas, evol_elas, mode_meca),
                fr=tr("Renseignement d'un résultat"),
            ),
        ),
    ),
    b_tables=BLOC(
        condition="equal_to('TYPE_COMB', 'TABLE')",
        FILTRE=FACT(
            statut="f",
            max="**",
            NOM_PARA=SIMP(statut="o", typ="TXM"),
            CRIT_COMP=SIMP(
                statut="f",
                typ="TXM",
                defaut="EQ",
                into=(
                    "EQ",
                    "LT",
                    "GT",
                    "NE",
                    "LE",
                    "GE",
                    "VIDE",
                    "NON_VIDE",
                    "MAXI",
                    "MAXI_ABS",
                    "MINI",
                    "MINI_ABS",
                ),
            ),
            b_vale=BLOC(
                condition="""(is_in("CRIT_COMP", ('EQ','NE','GT','LT','GE','LE')))""",
                regles=(UN_PARMI("VALE", "VALE_I", "VALE_K", "VALE_C"),),
                VALE=SIMP(statut="f", typ="R"),
                VALE_I=SIMP(statut="f", typ="I"),
                VALE_C=SIMP(statut="f", typ="C"),
                VALE_K=SIMP(statut="f", typ="TXM", max="**"),
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
            ),
        ),
        AFFE=FACT(
            statut="o",
            max="**",
            NOM_CAS=SIMP(statut="o", typ="TXM"),
            TABLE=SIMP(statut="o", typ=table_sdaster, fr=tr("Renseignement d'une table")),
        ),
    ),
)
