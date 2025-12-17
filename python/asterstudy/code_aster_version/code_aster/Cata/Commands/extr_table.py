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


def extr_table_prod(TYPE_RESU, **args):
    alltypes = (
        matr_asse_gene_r,
        matr_elem_depl_r,
        vect_elem_depl_r,
        matr_elem_temp_r,
        vect_elem_temp_r,
        cham_gd_sdaster,
        cham_no_sdaster,
        carte_sdaster,
        cham_elem,
        mode_meca,
        table_sdaster,
        fonction_sdaster,
        fonction_c,
        nappe_sdaster,
        entier,
        reel,
    )
    if args.get("__all__"):
        return alltypes

    defs = dict([(typ.__name__, typ) for typ in alltypes])
    typ = TYPE_RESU.lower()
    if defs.get(typ) is not None:
        return defs[typ]
    raise AsException("type de concept resultat non prevu: TYPE_RESU='{0}'".format(TYPE_RESU))


EXTR_TABLE = OPER(
    nom="EXTR_TABLE",
    op=173,
    sd_prod=extr_table_prod,
    reentrant="n",
    fr=tr("Extraire d'une table des concepts Code_Aster"),
    TYPE_RESU=SIMP(
        statut="o",
        typ="TXM",
        into=(
            "MATR_ASSE_GENE_R",
            "MATR_ELEM_DEPL_R",
            "VECT_ELEM_DEPL_R",
            "MATR_ELEM_TEMP_R",
            "VECT_ELEM_TEMP_R",
            "CHAM_GD_SDASTER",
            "CHAM_NO_SDASTER",
            "CARTE_SDASTER",
            "CHAM_ELEM",
            "MODE_MECA",
            "TABLE_SDASTER",
            "FONCTION_SDASTER",
            "FONCTION_C",
            "NAPPE_SDASTER",
            "ENTIER",
            "REEL",
        ),
    ),
    TABLE=SIMP(statut="o", typ=(table_sdaster, table_container)),
    NOM_PARA=SIMP(statut="o", typ="TXM"),
    FILTRE=FACT(
        statut="f",
        min=1,
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
            VALE_K=SIMP(statut="f", typ="TXM"),
        ),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
