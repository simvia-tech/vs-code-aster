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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def rest_cond_tran_prod(RESULTAT, TYPE_RESU, **args):
    if args.get("__all__"):
        return (dyna_trans, evol_noli)

    if AsType(RESULTAT) == dyna_trans:
        return dyna_trans
    if AsType(RESULTAT) == evol_noli and TYPE_RESU == "DYNA_TRANS":
        return dyna_trans
    if AsType(RESULTAT) == evol_noli and TYPE_RESU == "EVOL_NOLI":
        return evol_noli

    raise AsException("type de concept resultat non prevu")


REST_COND_TRAN = OPER(
    nom="REST_COND_TRAN",
    op=78,
    sd_prod=rest_cond_tran_prod,
    fr=tr(
        "Restituer dans la base physique des résultats issus d'un calcul"
        "non-lineaire avec projection modale ou d'un calcul transitoire linear"
        "avec condensation dynamique"
    ),
    reentrant="f:RESU_FINAL|RESULTAT",
    regles=(
        EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "INST", "LIST_INST", "TOUT_INST"),
        EXCLUS("MACR_ELEM_DYNA", "BASE_MODALE"),
    ),
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(statut="f", typ=(evol_noli, dyna_trans)),
    TYPE_RESU=SIMP(statut="f", typ="TXM", defaut="DYNA_TRANS", into=("DYNA_TRANS", "EVOL_NOLI")),
    BASE_MODALE=SIMP(statut="f", typ=mode_meca),
    #         NUME_DDL        =SIMP(statut='f',typ=nume_ddl_sdaster ),
    MACR_ELEM_DYNA=SIMP(statut="f", typ=macr_elem_dyna),
    TOUT_INST=SIMP(statut="f", typ="TXM", into=("OUI",)),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
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
            max=3,
            defaut="ACCE",
            into=("DEPL", "VITE", "ACCE"),
        ),
    ),
    b_base_moda=BLOC(
        condition="""exists("BASE_MODALE")""",
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    ),
    RESU_FINAL=SIMP(statut="f", typ=(evol_noli, dyna_trans)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
