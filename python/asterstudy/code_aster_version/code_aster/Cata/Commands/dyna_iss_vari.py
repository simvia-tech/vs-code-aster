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

# person_in_charge: irmela.zentner at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def dyna_iss_vari_prod(self, EXCIT_SOL, **args):
    if args.get("__all__"):
        return (tran_gene, interspectre)

    if EXCIT_SOL is not None:
        return tran_gene
    else:
        return interspectre
    raise AsException("type de concept resultat non prevu")


DYNA_ISS_VARI = MACRO(
    nom="DYNA_ISS_VARI",
    op=OPS("code_aster.MacroCommands.dyna_iss_vari_ops.dyna_iss_vari_ops"),
    sd_prod=dyna_iss_vari_prod,
    fr=tr(
        "Calcul du spectre de réponse ou de la reponse temporelle "
        "sismique incoherente par decomposition spectrale"
    ),
    reentrant="n",
    regles=(UN_PARMI("EXCIT_SOL", "NB_FREQ"),),
    EXCIT_SOL=FACT(
        statut="f",
        max=1,
        regles=(AU_MOINS_UN("ACCE_X", "ACCE_Y", "ACCE_Z"),),
        ACCE_X=SIMP(statut="f", typ=fonction_sdaster),
        ACCE_Y=SIMP(statut="f", typ=fonction_sdaster),
        ACCE_Z=SIMP(statut="f", typ=fonction_sdaster),
    ),
    NB_FREQ=SIMP(statut="f", typ="I"),
    PRECISION=SIMP(statut="f", typ="R", defaut=0.999),
    ISSF=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
    INTERF=FACT(
        statut="o",
        GROUP_NO_INTERF=SIMP(statut="o", typ=grno),
        MODE_INTERF=SIMP(statut="o", typ="TXM", into=("CORP_RIGI", "TOUT", "QUELCONQUE")),
    ),
    MATR_COHE=FACT(
        statut="o",
        TYPE=SIMP(
            statut="o", typ="TXM", into=("MITA_LUCO", "ABRAHAMSON", "ABRA_ROCHER", "ABRA_SOLMOYEN")
        ),
        b_type_coh=BLOC(
            condition="""equal_to("TYPE", 'MITA_LUCO') """,
            VITE_ONDE=SIMP(statut="o", typ="R", val_min=0.0),
            PARA_ALPHA=SIMP(statut="f", typ="R", defaut=0.1),
        ),
    ),
    #        LIST_FREQ        =SIMP(statut='o',typ='liste' ),
    UNITE_RESU_FORC=SIMP(statut="f", typ=UnitType(), defaut=33, inout="in"),
    UNITE_RESU_IMPE=SIMP(statut="f", typ=UnitType(), defaut=32, inout="in"),
    TYPE=SIMP(statut="f", typ="TXM", into=("BINAIRE", "ASCII"), defaut="ASCII"),
    #         NOM_CHAM        =SIMP(statut='f',typ='TXM',into=("DEPL","VITE","ACCE") , validators=NoRepeat(),max=3,defaut="DEPL" ),
    #
    MATR_GENE=FACT(
        statut="o",
        MATR_MASS=SIMP(statut="o", typ=(matr_asse_gene_r)),
        MATR_RIGI=SIMP(statut="o", typ=(matr_asse_gene_r, matr_asse_gene_c)),
        MATR_AMOR=SIMP(statut="f", typ=(matr_asse_gene_r, matr_asse_gene_c)),
    ),
    #
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    #
    b_type_trans=BLOC(
        condition="""exists("EXCIT_SOL")""",
        FREQ_MAX=SIMP(statut="f", typ="R"),
        FREQ_PAS=SIMP(statut="f", typ="R"),
        regles=(ENSEMBLE("FREQ_MAX", "FREQ_PAS"),),
    ),
    b_type_spec=BLOC(
        condition="""exists("NB_FREQ")""",
        FREQ_INIT=SIMP(statut="o", typ="R"),
        FREQ_PAS=SIMP(statut="o", typ="R"),
        OPTION=SIMP(statut="f", typ="TXM", into=("TOUT", "DIAG"), defaut="TOUT"),
        NOM_CMP=SIMP(statut="o", typ="TXM", into=("DX", "DY", "DZ")),
    ),
)
