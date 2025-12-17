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

# person_in_charge: nicolas.greffet at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_transfert_prod(self, SIGNAL, **args):
    if args.get("__all__"):
        return ([table_sdaster], [None, table_sdaster])

    #   self.type_sdprod(tabfrf,table_sdaster)
    if SIGNAL is not None:
        if type(SIGNAL) not in (list, tuple):
            SIGNAL = (SIGNAL,)
        for sign in SIGNAL:
            self.type_sdprod(sign["TABLE_RESU"], table_sdaster)
    return table_sdaster


CALC_TRANSFERT = MACRO(
    nom="CALC_TRANSFERT",
    op=OPS("code_aster.MacroCommands.calc_transfert_ops.calc_transfert_ops"),
    sd_prod=calc_transfert_prod,
    fr=tr("Calcul des fonctions de transfert et des signaux deconvolues "),
    NOM_CHAM=SIMP(statut="o", typ="TXM", max=1, into=("DEPL", "VITE", "ACCE")),
    ENTREE=FACT(statut="o", max=1, GROUP_NO=SIMP(statut="o", typ=grno, max=1)),
    SORTIE=FACT(statut="o", max=1, GROUP_NO=SIMP(statut="o", typ=grno, max=1)),
    REPERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_repere=BLOC(
        condition="""equal_to("REPERE", 'RELATIF')""",
        ENTRAINEMENT=FACT(
            statut="o",
            max=1,
            DX=SIMP(statut="o", typ=(fonction_sdaster, fonction_c)),
            DY=SIMP(statut="o", typ=(fonction_sdaster, fonction_c)),
            DZ=SIMP(statut="f", typ=(fonction_sdaster, fonction_c)),
        ),
    ),
    RESULTAT_X=SIMP(statut="o", typ=(harm_gene, tran_gene, dyna_harmo, dyna_trans)),
    RESULTAT_Y=SIMP(statut="o", typ=(harm_gene, tran_gene, dyna_harmo, dyna_trans)),
    RESULTAT_Z=SIMP(statut="f", typ=(harm_gene, tran_gene, dyna_harmo, dyna_trans)),
    SIGNAL=FACT(
        statut="f",
        max=1,
        MESURE_X=SIMP(statut="o", typ=(fonction_sdaster, fonction_c)),
        MESURE_Y=SIMP(statut="o", typ=(fonction_sdaster, fonction_c)),
        MESURE_Z=SIMP(statut="f", typ=(fonction_sdaster, fonction_c)),
        TABLE_RESU=SIMP(statut="o", typ=CO),
        TYPE_RESU=SIMP(statut="f", typ="TXM", defaut="HARMONIQUE", into=("HARMONIQUE", "TEMPOREL")),
    ),
)
