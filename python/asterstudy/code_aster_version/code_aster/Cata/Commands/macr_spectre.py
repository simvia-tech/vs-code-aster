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

# person_in_charge: francois.voldoire at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MACR_SPECTRE = MACRO(
    nom="MACR_SPECTRE",
    op=OPS("code_aster.MacroCommands.macr_spectre_ops.macr_spectre_ops"),
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr("Calcul de spectre, post-traitement de séisme"),
    MAILLAGE=SIMP(statut="f", typ=maillage_sdaster),
    b_maillage=BLOC(
        condition="""exists("MAILLAGE")""",
        PLANCHER=FACT(
            statut="o",
            max="**",
            NOM=SIMP(statut="o", typ="TXM"),
            BATIMENT=SIMP(statut="f", typ="TXM"),
            COMMENTAIRE=SIMP(statut="f", typ="TXM"),
            regles=(AU_MOINS_UN("GROUP_NO", "NOEUD"),),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),  # fin b_maillage
    b_not_maillage=BLOC(
        condition="""not exists("MAILLAGE")""",
        PLANCHER=FACT(
            statut="o",
            max="**",
            NOM=SIMP(statut="o", typ="TXM"),
            BATIMENT=SIMP(statut="f", typ="TXM"),
            COMMENTAIRE=SIMP(statut="f", typ="TXM"),
            NOEUD=SIMP(statut="o", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),  # fin b_not_maillage
    NOM_CHAM=SIMP(statut="o", typ="TXM", into=("ACCE", "DEPL")),
    CALCUL=SIMP(statut="o", typ="TXM", into=("ABSOLU", "RELATIF")),
    b_acce_rela=BLOC(
        condition="""equal_to("NOM_CHAM", 'ACCE') and equal_to("CALCUL", 'RELATIF')""",
        regles=(UN_PARMI("LIST_FREQ", "FREQ"),),
        AMOR_SPEC=SIMP(statut="o", typ="R", max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", max="**"),
        NORME=SIMP(statut="o", typ="R"),
        RESU=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("RESU_GENE", "RESULTAT", "TABLE"),),
            TABLE=SIMP(statut="f", typ=table_sdaster),
            RESU_GENE=SIMP(statut="f", typ=tran_gene),
            RESULTAT=SIMP(statut="f", typ=(dyna_trans, evol_noli)),
            ACCE_X=SIMP(statut="o", typ=fonction_sdaster),
            ACCE_Y=SIMP(statut="o", typ=fonction_sdaster),
            ACCE_Z=SIMP(statut="o", typ=fonction_sdaster),
        ),
    ),  # fin b_acce_rela
    b_acce_abso=BLOC(
        condition="""equal_to("NOM_CHAM", 'ACCE') and equal_to("CALCUL", 'ABSOLU')""",
        regles=(UN_PARMI("LIST_FREQ", "FREQ"),),
        AMOR_SPEC=SIMP(statut="o", typ="R", max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", max="**"),
        NORME=SIMP(statut="o", typ="R"),
        RESU=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("RESU_GENE", "RESULTAT", "TABLE"),),
            TABLE=SIMP(statut="f", typ=table_sdaster),
            RESU_GENE=SIMP(statut="f", typ=tran_gene),
            RESULTAT=SIMP(statut="f", typ=(dyna_trans, evol_noli)),
        ),
        MULT_APPUI=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),  # fin b_acce_abso
    b_impr=BLOC(
        condition="""equal_to("NOM_CHAM", 'ACCE') """,
        IMPRESSION=FACT(
            statut="f",
            TRI=SIMP(statut="f", typ="TXM", defaut="AMOR_SPEC", into=("AMOR_SPEC", "DIRECTION")),
            FORMAT=SIMP(statut="f", typ="TXM", defaut="TABLEAU", into=("TABLEAU", "XMGRACE")),
            UNITE=SIMP(
                statut="f",
                typ=UnitType(),
                defaut=29,
                inout="out",
                fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
            ),
            b_pilote=BLOC(
                condition="""equal_to("FORMAT", 'XMGRACE')""",
                PILOTE=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="",
                    into=(
                        "",
                        "POSTSCRIPT",
                        "EPS",
                        "MIF",
                        "SVG",
                        "PNM",
                        "PNG",
                        "JPEG",
                        "PDF",
                        "INTERACTIF",
                    ),
                ),
            ),
            TOUT=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        ),
    ),  # fin b_impr
    b_depl_rela=BLOC(
        condition="""equal_to("NOM_CHAM", 'DEPL') and equal_to("CALCUL", 'RELATIF')""",
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        RESU=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("RESU_GENE", "RESULTAT", "TABLE"),),
            TABLE=SIMP(statut="f", typ=table_sdaster),
            RESU_GENE=SIMP(statut="f", typ=tran_gene),
            RESULTAT=SIMP(statut="f", typ=(dyna_trans, evol_noli)),
        ),
    ),  # fin b_depl_rela
    b_depl_abso=BLOC(
        condition="""equal_to("NOM_CHAM", 'DEPL') and equal_to("CALCUL", 'ABSOLU')""",
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        RESU=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("RESU_GENE", "RESULTAT", "TABLE"),),
            TABLE=SIMP(statut="f", typ=table_sdaster),
            RESU_GENE=SIMP(statut="f", typ=tran_gene),
            RESULTAT=SIMP(statut="f", typ=(dyna_trans, evol_noli)),
            DEPL_X=SIMP(statut="o", typ=fonction_sdaster),
            DEPL_Y=SIMP(statut="o", typ=fonction_sdaster),
            DEPL_Z=SIMP(statut="o", typ=fonction_sdaster),
        ),
    ),  # fin b_depl_abso
)
