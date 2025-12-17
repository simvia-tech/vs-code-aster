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

# person_in_charge: natacha.bereux at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

RESOUDRE = OPER(
    nom="RESOUDRE",
    op=15,
    sd_prod=cham_no_sdaster,
    reentrant="f:CHAM_NO",
    fr=tr(
        "Résolution par méthode directe un système d'équations linéaires préalablement factorisé par FACT_LDLT"
        "ou Résolution d'un système linéaire par la méthode du gradient conjugué préconditionné"
    ),
    reuse=SIMP(statut="c", typ=CO),
    MATR=SIMP(
        statut="o",
        typ=(
            matr_asse_depl_r,
            matr_asse_depl_c,
            matr_asse_temp_r,
            matr_asse_temp_c,
            matr_asse_pres_r,
            matr_asse_pres_c,
        ),
    ),
    CHAM_NO=SIMP(statut="o", typ=cham_no_sdaster),
    CHAM_CINE=SIMP(statut="f", typ=cham_no_sdaster),
    # mot-clé commun aux solveurs MUMPS, GCPC et PETSc:
    RESI_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6),
    # mot-clé pour les posttraitements de la phase de solve de MUMPS
    POSTTRAITEMENTS=SIMP(
        statut="f", typ="TXM", defaut="AUTO", into=("SANS", "AUTO", "FORCE", "MINI")
    ),
    # mot-clé commun aux solveurs GCPC et PETSc:
    NMAX_ITER=SIMP(statut="f", typ="I", defaut=0),
    MATR_PREC=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r)),
    # mots-clés pour solveur PETSc:
    ALGORITHME=SIMP(
        statut="f", typ="TXM", into=("CG", "CR", "GMRES", "GCR", "FGMRES"), defaut="FGMRES"
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
