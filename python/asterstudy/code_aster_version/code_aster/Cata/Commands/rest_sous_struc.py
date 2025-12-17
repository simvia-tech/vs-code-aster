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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def rest_sous_struc_prod(RESU_GENE, RESULTAT, **args):
    if args.get("__all__"):
        return (dyna_trans, mode_meca, dyna_harmo, evol_noli)
    if AsType(RESU_GENE) == tran_gene:
        return dyna_trans
    if AsType(RESU_GENE) == mode_gene:
        return mode_meca
    if AsType(RESU_GENE) == mode_cycl:
        return mode_meca
    if AsType(RESU_GENE) == harm_gene:
        return dyna_harmo
    if AsType(RESULTAT) == evol_noli:
        return evol_noli
    if AsType(RESULTAT) == dyna_trans:
        return dyna_trans
    if AsType(RESULTAT) == mode_meca:
        return mode_meca
    raise AsException("type de concept resultat non prevu")


REST_SOUS_STRUC = OPER(
    nom="REST_SOUS_STRUC",
    op=77,
    sd_prod=rest_sous_struc_prod,
    fr=tr("Restituer dans la base physique des résultats obtenus par sous-structuration"),
    reentrant="n",
    regles=(
        UN_PARMI("RESU_GENE", "RESULTAT"),
        # ajout d'une regle de Ionel et Nicolas:
        #                UN_PARMI('NOM_CHAM','TOUT_CHAM'),
        #
        EXCLUS(
            "TOUT_ORDRE",
            "NUME_ORDRE",
            "INST",
            "LIST_INST",
            "TOUT_INST",
            "NUME_MODE",
            "FREQ",
            "LIST_FREQ",
        ),
        #  Doc U à revoir
        EXCLUS("NOEUD", "GROUP_NO"),
        PRESENT_PRESENT("RESULTAT", "SQUELETTE"),
        UN_PARMI("SQUELETTE", "SOUS_STRUC", "SECTEUR"),
    ),
    RESULTAT=SIMP(statut="f", typ=(evol_noli, dyna_trans, mode_meca)),
    RESU_GENE=SIMP(statut="f", typ=(tran_gene, mode_gene, mode_cycl, harm_gene)),
    NUME_DDL=SIMP(statut="f", typ=nume_ddl_sdaster),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    TOUT_INST=SIMP(statut="f", typ="TXM", into=("OUI",)),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("ABSOLU", "RELATIF")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    INTERPOL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "LIN")),
    TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
    b_nom_cham=BLOC(
        condition="""not exists("TOUT_CHAM")""",
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max=8,
            defaut="ACCE",
            into=(
                "DEPL",
                "VITE",
                "ACCE",
                "ACCE_ABSOLU",
                "EFGE_ELNO",
                "SIPO_ELNO",
                "SIGM_ELNO",
                "FORC_NODA",
            ),
        ),
    ),
    GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
    GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
    CYCLIQUE=FACT(
        statut="f",
        NB_SECTEUR=SIMP(statut="f", typ="I", max=1),
        NUME_DIAMETRE=SIMP(statut="f", typ="I", max=1),
        RESULTAT2=SIMP(statut="f", typ=(evol_elas, evol_noli, dyna_trans, evol_char, mode_meca)),
    ),
    SQUELETTE=SIMP(statut="f", typ=squelette),
    SOUS_STRUC=SIMP(statut="f", typ="TXM"),
    SECTEUR=SIMP(statut="f", typ="I"),
    TITRE=SIMP(statut="f", typ="TXM"),
)
