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


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def combinaison_charge_prod(self, TABLE_RESU, **args):
    """Typage du concept résultat"""
    if args.get("__all__"):
        return table_sdaster

    for m in TABLE_RESU:
        self.type_sdprod(m["TBALE"], table_sdaster)


COMBINAISON_CHARGE = MACRO(
    nom="COMBINAISON_CHARGE",
    op=OPS("code_aster.MacroCommands.combinaison_charge_ops.combinaison_charge_ops"),
    sd_prod=combinaison_charge_prod,
    fr=tr("Combinaison des calculs avec des chargements mécaniques et thermiques "),
    MODELE_MECA=SIMP(statut="o", typ=modele_sdaster),
    MODELE_THER=SIMP(statut="f", typ=modele_sdaster),
    CHAM_MATER_MECA=SIMP(statut="o", typ=cham_mater),
    CARA_ELEM_MECA=SIMP(statut="o", typ=cara_elem),
    CARA_ELEM_THER=SIMP(statut="f", typ=cara_elem),
    BLOC=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
    BLOC_THER=SIMP(statut="f", typ=(char_meca, char_cine_meca)),
    EXCIT_MECA=FACT(
        statut="o",
        max="**",
        CHAR_MECA=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
        NOM_CHAR=SIMP(statut="o", typ="TXM"),
    ),
    EXCIT_THER=FACT(
        statut="f",
        max="**",
        CHAM_MATER_THER=SIMP(statut="o", typ=cham_mater),
        NOM_CHAR=SIMP(statut="o", typ="TXM"),
    ),
    LIST_INST_THER=SIMP(statut="f", typ=(listr8_sdaster, list_inst)),
    COMPORTEMENT=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        RELATION=SIMP(statut="f", typ="TXM", defaut="ELAS", into=("ELAS", "MULTIFIBRE", "CABLE")),
    ),
    TABLE_COEF=SIMP(statut="o", typ=table_sdaster),
    CHAM_RESU=FACT(
        statut="o",
        max="**",
        NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
        NOM_CMP=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**"),
    ),
    TABLE_RESU=FACT(
        statut="o",
        max=3,
        UNITE=SIMP(statut="f", typ=UnitType(), inout="out"),
        OPTION=SIMP(statut="o", typ="TXM", into=("COEF_COMB", "CALC_COMB", "EXTREMA")),
        TABLE=SIMP(statut="o", typ=CO),
        b_extrema=BLOC(
            condition="""equal_to("OPTION", 'EXTREMA')""",
            CRIT_COMP=SIMP(
                statut="f",
                typ="TXM",
                defaut="TOUT",
                validators=NoRepeat(),
                max="**",
                into=("TOUT", "MAXI", "MAXI_ABS", "MINI", "MINI_ABS"),
            ),
        ),
    ),
    IMPRESSION=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    b_impression=BLOC(
        condition="""equal_to("IMPRESSION", 'OUI')""",
        UNITE=SIMP(statut="o", typ=UnitType(), inout="out"),
    ),
)
