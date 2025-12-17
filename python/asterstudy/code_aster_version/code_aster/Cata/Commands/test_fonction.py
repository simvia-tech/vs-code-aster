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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

TEST_FONCTION = MACRO(
    nom="TEST_FONCTION",
    op=OPS("code_aster.MacroCommands.test_fonction_ops.test_fonction_ops"),
    sd_prod=None,
    fr=tr(
        "Extraction d'une valeur numérique ou d'un attribut de fonction pour comparaison à une valeur de référence"
    ),
    VALEUR=FACT(
        statut="f",
        max="**",
        fr=tr("Tester la valeur d une fonction ou d une nappe"),
        regles=(UN_PARMI("VALE_PARA", "INTERVALLE"),),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c, nappe_sdaster, formule)),
        NOM_PARA=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max=2),
        VALE_PARA=SIMP(statut="f", typ="R", validators=NoRepeat(), max=2),
        INTERVALLE=SIMP(statut="f", typ="R", validators=NoRepeat(), min=2, max=2),
        **C_TEST_REFERENCE("FONCTION", max="**")
    ),
    ATTRIBUT=FACT(
        statut="f",
        max="**",
        fr=tr("Tester la valeur d un attribut d une fonction ou d''une nappe"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c, nappe_sdaster, formule)),
        PARA=SIMP(statut="f", typ="R"),
        CRIT_PARA=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        PREC_PARA=SIMP(statut="f", typ="R", defaut=1.0e-3),
        ATTR=SIMP(
            statut="o",
            typ="TXM",
            into=(
                "NOM_PARA",
                "NOM_RESU",
                "PROL_DROITE",
                "PROL_GAUCHE",
                "INTERPOL",
                "PROL_GAUCHE_FONC",
                "PROL_DROITE_FONC",
                "INTERPOL_FONC",
                "NOM_PARA_FONC",
            ),
        ),
        ATTR_REFE=SIMP(statut="o", typ="TXM"),
        REFERENCE=SIMP(statut="f", typ="TXM", into=("ANALYTIQUE", "SOURCE_EXTERNE", "AUTRE_ASTER")),
    ),
)
