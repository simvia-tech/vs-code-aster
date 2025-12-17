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

# person_in_charge: sylvie.audebert at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def post_roche_prod(RESU_MECA, **args):
    if args.get("__all__"):
        return (cham_elem, evol_noli)

    if RESU_MECA is not None:
        return cham_elem
    else:
        return evol_noli


POST_ROCHE = MACRO(
    nom="POST_ROCHE",
    op=OPS("code_aster.MacroCommands.post_roche_ops.post_roche_ops"),
    sd_prod=cham_elem,
    fr=tr(
        "Méthode Roche de représentation du comportement élasto-plastique des lignes de tuyauteries"
    ),
    reentrant="n",
    regles=(UN_PARMI("RESU_MECA", "RESU_MECA_TRAN"),),
    ZONE_ANALYSE=FACT(
        statut="o",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_ORIG=SIMP(statut="o", typ=grno, validators=NoRepeat(), min=1, max=1),
    ),
    COUDE=FACT(
        statut="f",
        max="**",
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        ANGLE=SIMP(statut="o", typ="R"),
        RCOURB=SIMP(statut="o", typ="R"),
    ),
    #        pour le cas ou un mode_meca est donné en première occurence
    MODELE=SIMP(statut="f", typ=(modele_sdaster)),
    #        pour le cas ou il n'y a que des CHAM_GD
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    INST_TEMP=SIMP(statut="f", typ="R", defaut=0.0),
    RESU_MECA=FACT(
        statut="f",
        max="**",
        TYPE_CHAR=SIMP(
            statut="o", typ="TXM", into=("SISM_INER_SPEC", "DEPLACEMENT", "DILAT_THERM", "POIDS")
        ),
        b_sism_iner_spec=BLOC(
            condition="""equal_to("TYPE_CHAR", 'SISM_INER_SPEC') """,
            # RESULTAT=SIMP(statut="o", typ=(mode_meca,)),
            RESULTAT=SIMP(statut="o", typ=(mult_elas, mode_meca)),
            DIRECTION=SIMP(statut="f", typ="TXM", into=("COMBI", "X", "Y", "Z"), defaut="COMBI"),
            TYPE_RESU=SIMP(statut="f", typ="TXM", into=("DYN_QS", "DYN", "QS"), defaut="DYN_QS"),
        ),
        b_autre=BLOC(
            condition="""not equal_to("TYPE_CHAR", 'SISM_INER_SPEC') """,
            regles=(UN_PARMI("CHAM_GD", "RESULTAT"), UN_PARMI("CHAM_GD", "NUME_ORDRE", "INST")),
            CHAM_GD=SIMP(statut="f", typ=cham_elem),
            RESULTAT=SIMP(statut="f", typ=(evol_elas)),
            NUME_ORDRE=SIMP(statut="f", typ="I", max=1),
            INST=SIMP(statut="f", typ="R", max=1),
            b_inst=BLOC(
                condition="""exists("INST") """,
                CRITERE=SIMP(statut="f", typ="TXM", into=("RELATIF", "ABSOLU"), defaut=("RELATIF")),
                PRECISION=SIMP(statut="f", typ="R", defaut=1e-6),
            ),
        ),
    ),
    RESU_MECA_TRAN=FACT(
        statut="f",
        max="**",
        TYPE_CHAR=SIMP(
            statut="o", typ="TXM", into=("SISM_INER_TRAN", "DEPLACEMENT", "DILAT_THERM", "POIDS")
        ),
        b_sism_iner_tran=BLOC(
            condition="""equal_to("TYPE_CHAR", 'SISM_INER_TRAN') """,
            regles=(UN_PARMI("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_ORDRE", "LIST_INST"),),
            RESULTAT=SIMP(statut="o", typ=(dyna_trans)),
            RESU_CORR=SIMP(statut="f", typ=(dyna_trans)),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            b_inst=BLOC(
                condition="""exists("INST") or  exists("LIST_INST")""",
                CRITERE=SIMP(statut="f", typ="TXM", into=("RELATIF", "ABSOLU"), defaut=("RELATIF")),
                PRECISION=SIMP(statut="f", typ="R", defaut=1e-6),
            ),
        ),
        b_autre=BLOC(
            condition="""not equal_to("TYPE_CHAR", 'SISM_INER_TRAN') """,
            regles=(UN_PARMI("CHAM_GD", "RESULTAT"), UN_PARMI("CHAM_GD", "NUME_ORDRE", "INST")),
            CHAM_GD=SIMP(statut="f", typ=cham_elem),
            RESULTAT=SIMP(statut="f", typ=(evol_elas)),
            NUME_ORDRE=SIMP(statut="f", typ="I", max=1),
            INST=SIMP(statut="f", typ="R", max=1),
            b_inst=BLOC(
                condition="""exists("INST") """,
                CRITERE=SIMP(statut="f", typ="TXM", into=("RELATIF", "ABSOLU"), defaut=("RELATIF")),
                PRECISION=SIMP(statut="f", typ="R", defaut=1e-6),
            ),
        ),
    ),
    PRESSION=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        VALE=SIMP(statut="o", typ="R", val_min=0.0),
    ),
    RCCM_RX=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut=("OUI")),
)
