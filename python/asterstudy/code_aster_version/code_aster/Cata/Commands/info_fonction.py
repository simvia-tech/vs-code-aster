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


def info_fonction_prod(self, **args):
    if args.get("__all__"):
        return (table_sdaster,)
    return table_sdaster


INFO_FONCTION = MACRO(
    nom="INFO_FONCTION",
    op=OPS("code_aster.MacroCommands.info_fonction_ops.info_fonction_ops"),
    sd_prod=info_fonction_prod,
    fr=tr("Opérations mathématiques sur des concepts de type fonction, " "fonction_c ou nappe"),
    reentrant="n",
    regles=(UN_PARMI("MAX", "RMS", "NOCI_SEISME", "NORME", "ECART_TYPE"),),
    RMS=FACT(
        statut="f",
        fr=tr("Valeur RMS d'une fonction"),
        max="**",
        METHODE=SIMP(statut="f", typ="TXM", defaut="TRAPEZE", into=("SIMPSON", "TRAPEZE")),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        INST_INIT=SIMP(
            statut="f", typ="R", fr=tr("Instant initial définissant le début du signal")
        ),
        INST_FIN=SIMP(statut="f", typ="R", fr=tr("Instant final définissant la fin du signal")),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6, val_min=0.0e0),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    NOCI_SEISME=FACT(
        statut="f",
        regles=(UN_PARMI("FONCTION", "SPEC_OSCI"),),
        FONCTION=SIMP(statut="f", typ=fonction_sdaster),
        SPEC_OSCI=SIMP(statut="f", typ=nappe_sdaster),
        b_option_f=BLOC(
            condition="""exists("FONCTION")""",
            OPTION=SIMP(
                statut="f",
                typ="TXM",
                defaut="TOUT",
                validators=NoRepeat(),
                into=(
                    "INTE_ARIAS",
                    "POUV_DEST",
                    "INTE_SPEC",
                    "VITE_ABSO_CUMU",
                    "DUREE_PHAS_FORT",
                    "MAXI",
                    "ACCE_SUR_VITE",
                    "ASA",
                    "TOUT",
                ),
            ),
            b_asa=BLOC(
                condition="""is_in('OPTION', ("TOUT", "ASA"))""",
                FREQ_FOND=SIMP(statut="o", typ="R", val_min=0.0e0),
                FREQ_PAS=SIMP(statut="f", typ="R", defaut=0.01),
                NORME=SIMP(statut="f", typ="R", defaut=1.0e0),
                RATIO=SIMP(statut="f", typ="R", defaut=0.40),
            ),
            b_amor_red=BLOC(
                condition="""is_in('OPTION', ("TOUT", "INTE_SPEC","ASA" )) """,
                AMOR_REDUIT=SIMP(statut="o", typ="R"),
            ),
            b_pesanteur=BLOC(
                condition="""is_in('OPTION', ("TOUT", "INTE_ARIAS", "POUV_DEST", "DUREE_PHAS_FORT")) """,
                PESANTEUR=SIMP(statut="o", typ="R"),
            ),
        ),
        b_option_n=BLOC(
            condition="""exists("SPEC_OSCI")""",
            OPTION=SIMP(statut="f", typ="TXM", defaut="INTE_SPEC", into=("INTE_SPEC",)),
            NATURE=SIMP(statut="o", typ="TXM", into=("DEPL", "VITE", "ACCE")),
            AMOR_REDUIT=SIMP(statut="o", typ="R"),
        ),
        INST_INIT=SIMP(statut="f", typ="R"),
        INST_FIN=SIMP(statut="f", typ="R"),
        COEF=SIMP(statut="f", typ="R", defaut=0.0e0),
        FREQ_INIT=SIMP(statut="f", typ="R", defaut=4.0e-1),
        FREQ_FIN=SIMP(statut="f", typ="R", defaut=10.0e0),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", max="**"),
        NORME=SIMP(statut="f", typ="R", defaut=1.0e0),
        BORNE_INF=SIMP(statut="f", typ="R", defaut=0.05e0),
        BORNE_SUP=SIMP(statut="f", typ="R", defaut=0.95e0),
        b_acce_reel=BLOC(
            condition="""(exists("INST_INIT"))or(exists("INST_FIN"))or(exists("FREQ_INIT"))or(exists("FREQ_FIN"))""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6, val_min=0.0e0),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
    ),
    MAX=FACT(
        statut="f",
        fr=tr("Extrémas locaux d'une fonction"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster), max="**"),
        INTERVALLE=SIMP(
            statut="f",
            typ="R",
            min=2,
            max="**",
            fr=tr(
                "définition des bornes des intervalles sous forme de couples (xi_i1,xs_i1,xi_i2,xs_i2)"
            ),
        ),
    ),
    NORME=FACT(
        statut="f", fr=tr("Norme L2 d'une fonction"), FONCTION=SIMP(statut="o", typ=nappe_sdaster)
    ),
    ECART_TYPE=FACT(
        statut="f",
        fr=tr("Ecart-type d'une fonction"),
        METHODE=SIMP(statut="f", typ="TXM", defaut="TRAPEZE", into=("SIMPSON", "TRAPEZE")),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        INST_INIT=SIMP(
            statut="f", typ="R", fr=tr("Instant initial définissant le début du signal")
        ),
        INST_FIN=SIMP(statut="f", typ="R", fr=tr("Instant final définissant la fin du signal")),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6, val_min=0.0e0),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
