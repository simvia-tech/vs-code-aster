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

# person_in_charge: sam.cuvilliez at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_K_TRANS = MACRO(
    nom="POST_K_TRANS",
    op=OPS("code_aster.MacroCommands.post_k_trans_ops.post_k_trans_ops"),
    sd_prod=table_sdaster,
    fr=tr("Calcul des facteurs d intensite des contrainte par recombinaison modale"),
    reentrant="n",
    RESU_TRANS=SIMP(statut="o", typ=tran_gene),
    K_MODAL=FACT(
        statut="o",
        TABL_K_MODA=SIMP(statut="o", typ=table_sdaster),
        FOND_FISS=SIMP(statut="f", typ=fond_fissure),
        FISSURE=SIMP(statut="f", typ=fiss_xfem),
        regles=(UN_PARMI("FISSURE", "FOND_FISS"),),
    ),
    regles=(EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_INST", "LIST_ORDRE"),),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
