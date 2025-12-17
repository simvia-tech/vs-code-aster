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

DEFI_CHAR_SOL = MACRO(
    nom="DEFI_CHAR_SOL",
    op=OPS("code_aster.MacroCommands.defi_char_sol_ops.defi_char_sol_ops"),
    sd_prod=char_meca,
    fr=tr("Définition des données de sol pour Miss"),
    reentrant="n",
    CHARGEMENT=SIMP(statut="f", typ="TXM", into=("FORCE", "ONDE_PLANE"), defaut="FORCE"),
    MODELE=SIMP(statut="o", typ=(modele_sdaster)),
    regles=(UN_PARMI("UNITE_TRAN_INIT", "RESU_INIT"),),
    UNITE_TRAN_INIT=SIMP(statut="f", typ=UnitType(), inout="in"),
    RESU_INIT=SIMP(statut="f", typ=(dyna_trans, evol_char, evol_noli)),
    b_unite_tran=BLOC(
        condition="""exists("UNITE_TRAN_INIT")""",
        LONG_CARA=SIMP(statut="f", typ="R", fr=tr("valeur de longueur caracteristique")),
        AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z")),
        NOM_PARA=SIMP(statut="f", typ="TXM", into=("Y", "Z"), defaut="Z"),
        Z0=SIMP(statut="f", typ="R", defaut=0.0e0),
        NOM_CMP=SIMP(
            statut="f",
            typ="TXM",
            into=("DX", "DY"),
            defaut="DX",
            fr=tr("sollicitation horizontale"),
        ),
        regles=(AU_MOINS_UN("GROUP_MA_DROITE", "GROUP_MA_GAUCHE"),),
        GROUP_MA_DROITE=SIMP(statut="f", typ=grma),
        GROUP_MA_GAUCHE=SIMP(statut="f", typ=grma),
        TABLE_MATER_ELAS=SIMP(statut="o", typ=table_sdaster),
    ),  # fin bloc b_unite_tran
    b_resu=BLOC(
        condition="""exists("RESU_INIT")""",
        MATR_RIGI=SIMP(statut="f", typ=matr_asse_depl_r),
        COEF=SIMP(statut="f", typ="R", defaut=1.0e0),
        NOM_CHAM_INIT=SIMP(
            statut="f", typ="TXM", defaut="FORC_NODA", into=("ACCE", "FORC_NODA", "REAC_NODA")
        ),
        DDL_EXCLUS=SIMP(statut="f", typ="TXM", into=("DX", "DY", "DZ", "DRX", "DRY", "DRZ")),
        MATR_AMOR=SIMP(statut="f", typ=matr_asse_depl_r),
        NUME_DDL=SIMP(statut="f", typ=nume_ddl_sdaster),
        LIST_INST=SIMP(statut="o", typ=listr8_sdaster),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),  # fin bloc b_resu
    TITRE=SIMP(statut="f", typ="TXM", fr=tr("Titre de la charge produite")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
