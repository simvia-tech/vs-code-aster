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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_TEST_REFERENCE(keyword, max=1):  # COMMUN#
    """Mots-clés communs pour TEST_RESU, TEST_TABLE, TEST_FONCTION.
    On retourne un bloc pour ajouter la règle UN_PARMI."""
    assert keyword in (
        "CHAM_NO",
        "CHAM_ELEM",
        "CARTE",
        "RESU",
        "GENE",
        "OBJET",
        "TABLE",
        "FONCTION",
        "FICHIER",
        "MAILLAGE",
    )
    with_int = keyword not in ("FONCTION",)
    with_complex = keyword not in ("OBJET", "FICHIER", "MAILLAGE")
    with_string = keyword in ("FICHIER", "TABLE")
    vale_abs = keyword not in ("CARTE", "FICHIER")
    type_test = keyword not in ("CARTE", "GENE", "OBJET")
    multi_prec = keyword in ("RESU", "GENE")
    reference = keyword not in ("FICHIER",)
    un_parmi = keyword not in ("FICHIER",)

    opts = {}
    opts_ref = {}
    types = [""]

    def add_type(typ):
        ttyp = typ == "K" and "TXM" or typ
        types.append("_" + typ)
        opts["VALE_CALC_" + typ] = SIMP(statut="f", typ=ttyp, max=max)
        opts_ref["VALE_REFE_" + typ] = SIMP(statut="f", typ=ttyp, max=max)

    if with_int:
        add_type("I")
    if with_complex:
        add_type("C")
    if with_string:
        add_type("K")
    if vale_abs:
        opts["VALE_ABS"] = SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON"))
    if type_test:
        opts["TYPE_TEST"] = SIMP(statut="f", typ="TXM", into=("SOMM_ABS", "SOMM", "MAX", "MIN"))
    if not multi_prec:
        opts["TOLE_MACHINE"] = SIMP(statut="f", typ="R", defaut=1.0e-6)
        opts["CRITERE"] = SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU"))
    else:
        opts["TOLE_MACHINE"] = SIMP(statut="f", typ="R", max=2)
        opts["CRITERE"] = SIMP(statut="f", typ="TXM", max=2, into=("RELATIF", "ABSOLU"))
    if un_parmi:
        opts["regles"] = UN_PARMI(*["VALE_CALC" + t for t in types])
        opts_ref["regles"] = UN_PARMI(*["VALE_REFE" + t for t in types])
    if reference:
        opts["b_reference"] = BLOC(
            condition="""exists("REFERENCE")""",
            VALE_REFE=SIMP(statut="f", typ="R", max=max),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
            **opts_ref
        )
        opts["REFERENCE"] = SIMP(
            statut="f",
            typ="TXM",
            into=("ANALYTIQUE", "SOURCE_EXTERNE", "AUTRE_ASTER", "NON_DEFINI"),
        )
    kwargs = {
        "b_values": BLOC(
            condition="""True""",
            VALE_CALC=SIMP(statut="f", typ="R", max=max),
            # tricky because VALE_CALC may be a tuple or a scalar
            b_ordre_grandeur=BLOC(
                condition="""exists("VALE_CALC") and abs(VALE_CALC if type(VALE_CALC) not in (list, tuple) else VALE_CALC[0]) < 1.e-16""",
                ORDRE_GRANDEUR=SIMP(statut="f", typ="R"),
            ),
            LEGENDE=SIMP(statut="f", typ="TXM"),
            **opts
        )
    }
    return kwargs
