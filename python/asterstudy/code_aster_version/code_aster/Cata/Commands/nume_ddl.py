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

NUME_DDL = MACRO(
    nom="NUME_DDL",
    op=OPS("code_aster.MacroCommands.nume_ddl_ops.nume_ddl_ops"),
    sd_prod=nume_ddl_sdaster,
    reentrant="n",
    fr=tr(
        "Etablissement de la numérotation des ddl avec ou sans renumérotation et du stockage de la matrice"
    ),
    regles=(UN_PARMI("MATR_RIGI", "MODELE"),),
    MATR_RIGI=SIMP(
        statut="f",
        validators=NoRepeat(),
        max=100,
        typ=(matr_elem_depl_r, matr_elem_depl_c, matr_elem_temp_r, matr_elem_pres_c),
    ),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    b_modele=BLOC(
        condition="""exists("MODELE")""",
        CHARGE=SIMP(
            statut="f", validators=NoRepeat(), max="**", typ=(char_meca, char_ther, char_acou)
        ),
    ),
    INFO=SIMP(statut="f", typ="I", into=(1, 2), defaut=1),
)
