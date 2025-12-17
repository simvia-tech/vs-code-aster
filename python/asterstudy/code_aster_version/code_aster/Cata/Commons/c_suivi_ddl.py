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

# person_in_charge: mickael.abbas at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_SUIVI_DDL():
    return FACT(
        statut="f",
        max=4,
        regles=(UN_PARMI("NOM_CMP", "NOM_VARI"),),
        NOM_CHAM=SIMP(
            statut="o",
            typ="TXM",
            max=1,
            into=("DEPL", "VITE", "ACCE", "FORC_NODA", "SIEF_ELGA", "VARI_ELGA", "EPSI_ELGA"),
        ),
        EVAL_CHAM=SIMP(
            statut="f",
            typ="TXM",
            max=1,
            defaut="VALE",
            into=("MIN", "MAX", "MOY", "MAXI_ABS", "MINI_ABS", "VALE"),
        ),
        NOM_CMP=SIMP(statut="f", typ="TXM", max=20),
        NOM_VARI=SIMP(statut="f", typ="TXM", max=20),
        EVAL_CMP=SIMP(statut="f", typ="TXM", max=1, defaut="VALE", into=("VALE", "FORMULE")),
        b_formule=BLOC(
            condition="""(equal_to("EVAL_CMP", 'FORMULE'))""",
            FORMULE=SIMP(statut="o", typ=formule, max=1),
        ),
        b_cham_no=BLOC(
            condition="""is_in("NOM_CHAM", ('DEPL','VITE','ACCE','FORC_NODA','CONT_NOEU'))""",
            regles=(UN_PARMI("NOEUD", "GROUP_NO", "GROUP_MA", "MAILLE", "TOUT")),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOEUD=SIMP(statut="f", typ=no, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        ),
        b_cham_elga=BLOC(
            condition="""is_in("NOM_CHAM", ('SIEF_ELGA','EPSI_ELGA','VARI_ELGA'))""",
            regles=(UN_PARMI("GROUP_MA", "MAILLE", "TOUT")),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            MAILLE=SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            EVAL_ELGA=SIMP(
                statut="f", typ="TXM", max=1, defaut="VALE", into=("MIN", "MAX", "VALE")
            ),
            b_elga_vale=BLOC(
                condition="""(equal_to("EVAL_ELGA", 'VALE'))""",
                POINT=SIMP(statut="o", typ="I", validators=NoRepeat(), max="**"),
                SOUS_POINT=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            ),
        ),
        # a decommenter quand un champ ELEM sera disponible
        # b_cham_elem    =BLOC(condition="(NOM_CHAM=='XXXX_ELEM')",
        # regles          =(UN_PARMI('GROUP_MA','MAILLE','TOUT')),
        # TOUT            =SIMP(statut='f',typ='TXM',into=("OUI",) ),
        # MAILLE          =SIMP(statut='f',typ=ma   ,validators=NoRepeat(),max='**'),
        # GROUP_MA        =SIMP(statut='f',typ=grma ,validators=NoRepeat(),max='**'),
        # ),
        TITRE=SIMP(statut="f", typ="TXM", max=3),
    )
