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

# person_in_charge: mickael.abbas at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_OBSERVATION(phys):
    assert phys in ("MECANIQUE", "THERMIQUE", "DYNAVIBRA")
    _meca = phys == "MECANIQUE"
    _ther = phys == "THERMIQUE"
    _dyna = phys == "DYNAVIBRA"

    # Select nodal fields
    _BlocNode = {}
    _BlocNode["TOUT"] = SIMP(statut="f", typ="TXM", into=("OUI",))
    _BlocNode["NOEUD"] = SIMP(statut="f", typ=no, validators=NoRepeat(), max="**")
    _BlocNode["GROUP_NO"] = SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**")
    _BlocNode["MAILLE"] = SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**")
    _BlocNode["GROUP_MA"] = SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**")

    # Select element fields
    _BlocElem = {}
    _BlocElem["TOUT"] = SIMP(statut="f", typ="TXM", into=("OUI",))
    _BlocElem["MAILLE"] = SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**")
    _BlocElem["GROUP_MA"] = SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**")

    # All keywords
    _Keywords = {}
    _Keywords["TITRE"] = SIMP(statut="f", typ="TXM", max=1)
    _Keywords["OBSE_ETAT_INIT"] = SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI")
    _Keywords["EVAL_CHAM"] = SIMP(
        statut="f",
        typ="TXM",
        max=1,
        defaut="VALE",
        into=("MIN", "MAX", "MOY", "MAXI_ABS", "MINI_ABS", "VALE"),
    )
    _Keywords["NOM_CMP"] = SIMP(statut="f", typ="TXM", max=20)
    _Keywords["NOM_VARI"] = SIMP(statut="f", typ="TXM", max=20)
    _Keywords["EVAL_CMP"] = SIMP(
        statut="f", typ="TXM", max=1, defaut="VALE", into=("VALE", "FORMULE")
    )
    _Keywords["INST"] = SIMP(statut="f", typ="R", validators=NoRepeat(), max="**")
    _Keywords["LIST_INST"] = SIMP(statut="f", typ=listr8_sdaster)
    _Keywords["PAS_OBSE"] = SIMP(statut="f", typ="I")
    _Keywords["CRITERE"] = SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU"))

    if _dyna:
        _Keywords["NOM_CHAM"] = SIMP(statut="o", typ="TXM", max=1, into=("DEPL", "VITE", "ACCE"))

    if _meca:
        _Keywords["NOM_CHAM"] = SIMP(
            statut="o",
            typ="TXM",
            max=1,
            into=(
                "CONT_NOEU",
                "FORC_NODA",
                "CONT_ELEM",
                "DEPL",
                "VITE",
                "ACCE",
                "SIEF_ELGA",
                "VARI_ELGA",
                "EPSI_ELGA",
                "DEPL_ABSOLU",
                "VITE_ABSOLU",
                "ACCE_ABSOLU",
            ),
        )
    if _ther:
        _Keywords["NOM_CHAM"] = SIMP(statut="o", typ="TXM", max=1, into=("TEMP",))

    mcfact = FACT(
        statut="f",
        max=99,
        regles=(UN_PARMI("NOM_CMP", "NOM_VARI"),),
        b_formule=BLOC(
            condition="""(equal_to("EVAL_CMP", 'FORMULE'))""",
            FORMULE=SIMP(statut="o", typ=formule, max=1),
        ),
        b_cham_no=BLOC(
            condition="""is_in("NOM_CHAM", ('DEPL','VITE','ACCE','TEMP','FORC_NODA','CONT_NOEU','DEPL_ABSOLU','VITE_ABSOLU','ACCE_ABSOLU'))""",
            regles=(UN_PARMI("NOEUD", "GROUP_NO", "GROUP_MA", "MAILLE", "TOUT")),
            **_BlocNode
        ),
        b_cham_elga=BLOC(
            condition="""is_in("NOM_CHAM", ('SIEF_ELGA','EPSI_ELGA','VARI_ELGA'))""",
            regles=(UN_PARMI("GROUP_MA", "MAILLE", "TOUT")),
            EVAL_ELGA=SIMP(
                statut="f", typ="TXM", max=1, defaut="VALE", into=("MIN", "MAX", "VALE")
            ),
            b_elga_vale=BLOC(
                condition="""(equal_to("EVAL_ELGA", 'VALE'))""",
                POINT=SIMP(statut="o", typ="I", validators=NoRepeat(), max="**"),
                SOUS_POINT=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            ),
            **_BlocElem
        ),
        b_cham_elem=BLOC(
            condition="""(equal_to("NOM_CHAM", 'CONT_ELEM'))""",
            regles=(UN_PARMI("GROUP_MA", "MAILLE", "TOUT")),
            **_BlocElem
        ),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        **_Keywords
    )

    return mcfact
