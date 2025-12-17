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


def proj_base_prod(
    self, MATR_ASSE_GENE, VECT_ASSE_GENE, RESU_GENE, NUME_DDL_GENE, STOCKAGE, **args
):
    if args.get("__all__"):
        return (
            [None],
            [None, nume_ddl_gene],
            [None, matr_asse_gene_r],
            [None, vect_asse_gene],
            [None, tran_gene],
        )

    if NUME_DDL_GENE is not None and NUME_DDL_GENE.is_typco():
        self.type_sdprod(NUME_DDL_GENE, nume_ddl_gene)
    if MATR_ASSE_GENE is not None:
        for m in MATR_ASSE_GENE:
            self.type_sdprod(m["MATRICE"], matr_asse_gene_r)
    if VECT_ASSE_GENE is not None:
        for v in VECT_ASSE_GENE:
            self.type_sdprod(v["VECTEUR"], vect_asse_gene)
    if RESU_GENE is not None:
        for v in RESU_GENE:
            self.type_sdprod(v["RESULTAT"], tran_gene)
    return None


PROJ_BASE = MACRO(
    nom="PROJ_BASE",
    op=OPS("code_aster.MacroCommands.proj_base_ops.proj_base_ops"),
    regles=(AU_MOINS_UN("MATR_ASSE_GENE", "VECT_ASSE_GENE", "RESU_GENE")),
    sd_prod=proj_base_prod,
    fr=tr("Projection des matrices et/ou vecteurs assembles sur une base (modale ou de RITZ)"),
    BASE=SIMP(statut="o", typ=(mode_meca, mode_gene)),
    NB_VECT=SIMP(statut="f", typ="I"),
    STOCKAGE=SIMP(statut="f", typ="TXM", defaut="PLEIN", into=("PLEIN", "DIAG")),
    NUME_DDL_GENE=SIMP(statut="f", typ=(nume_ddl_gene, CO)),
    MATR_ASSE_GENE=FACT(
        statut="f",
        max="**",
        MATRICE=SIMP(statut="o", typ=CO),
        regles=(UN_PARMI("MATR_ASSE", "MATR_ASSE_GENE"),),
        MATR_ASSE=SIMP(statut="f", typ=matr_asse_depl_r),
        MATR_ASSE_GENE=SIMP(statut="f", typ=matr_asse_gene_r),
    ),
    VECT_ASSE_GENE=FACT(
        statut="f",
        max="**",
        VECTEUR=SIMP(statut="o", typ=CO),
        regles=(UN_PARMI("VECT_ASSE", "VECT_ASSE_GENE"),),
        TYPE_VECT=SIMP(statut="o", typ="TXM", into=("FORC", "DEPL", "VITE", "ACCE")),
        VECT_ASSE=SIMP(statut="f", typ=cham_no_sdaster),
        VECT_ASSE_GENE=SIMP(statut="f", typ=vect_asse_gene),
    ),
    RESU_GENE=FACT(
        statut="f",
        max="**",
        RESULTAT=SIMP(statut="o", typ=CO),
        TYPE_VECT=SIMP(statut="o", typ="TXM", into=("FORC", "DEPL", "VITE", "ACCE")),
        RESU=SIMP(statut="o", typ=dyna_trans),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
