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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_BASE_MODALE = OPER(
    nom="DEFI_BASE_MODALE",
    op=99,
    sd_prod=mode_meca,
    reentrant="f:RITZ:BASE_MODALE",
    fr=tr("Définit la base d'une sous-structuration dynamique ou d'une recombinaison modale"),
    regles=(UN_PARMI("CLASSIQUE", "RITZ", "DIAG_MASS", "ORTHO_BASE"),),
    reuse=SIMP(statut="c", typ=CO),
    CLASSIQUE=FACT(
        statut="f",
        INTERF_DYNA=SIMP(statut="o", typ=interf_dyna_clas),
        MODE_MECA=SIMP(statut="o", typ=mode_meca, max="**"),
        NMAX_MODE=SIMP(statut="f", typ="I", max="**"),
    ),
    RITZ=FACT(
        statut="f",
        max=2,
        regles=(UN_PARMI("MODE_MECA", "BASE_MODALE", "MODE_INTF"),),
        MODE_MECA=SIMP(statut="f", typ=mode_meca, max="**"),
        NMAX_MODE=SIMP(statut="f", typ="I", max="**"),
        BASE_MODALE=SIMP(statut="f", typ=mode_meca),
        MODE_INTF=SIMP(statut="f", typ=(mode_meca, mult_elas)),
    ),
    b_ritz=BLOC(
        condition="""exists("RITZ")""",
        INTERF_DYNA=SIMP(statut="f", typ=interf_dyna_clas),
        NUME_REF=SIMP(statut="f", typ=nume_ddl_sdaster),
        ORTHO=SIMP(
            statut="f",
            typ="TXM",
            defaut="NON",
            into=("OUI", "NON"),
            fr=tr("Reorthonormalisation de la base de Ritz"),
        ),
        LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        b_ortho=BLOC(
            condition="""equal_to("ORTHO", 'OUI') """,
            MATRICE=SIMP(
                statut="o",
                typ=(matr_asse_depl_r, matr_asse_depl_c, matr_asse_gene_r, matr_asse_pres_r),
            ),
        ),
    ),
    DIAG_MASS=FACT(
        statut="f",
        MODE_MECA=SIMP(statut="o", typ=mode_meca, max="**"),
        MODE_STAT=SIMP(statut="o", typ=mode_meca),
    ),
    ORTHO_BASE=FACT(
        statut="f",
        BASE=SIMP(statut="o", typ=(mode_meca, mult_elas)),
        MATRICE=SIMP(
            statut="o", typ=(matr_asse_depl_r, matr_asse_depl_c, matr_asse_gene_r, matr_asse_pres_r)
        ),
    ),
    # -------------------------------------------------------------------
    #       Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("DEFI_BASE_MODALE"),
    # -------------------------------------------------------------------
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
