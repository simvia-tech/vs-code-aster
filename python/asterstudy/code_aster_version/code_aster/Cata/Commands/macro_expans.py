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


def macro_expans_prod(
    self, MODELE_MESURE, RESU_NX=None, RESU_EX=None, RESU_ET=None, RESU_RD=None, **args
):
    if args.get("__all__"):
        return ([None], [None, mode_meca], [None, mode_meca, dyna_harmo])

    RESU_EXP = MODELE_MESURE["MESURE"]
    if RESU_NX is not None:
        self.type_sdprod(RESU_NX, mode_meca)
    for res in (RESU_EX, RESU_ET, RESU_RD):
        if res is not None and res.is_typco():
            if AsType(RESU_EXP) == mode_meca:
                self.type_sdprod(res, mode_meca)
            else:
                self.type_sdprod(res, dyna_harmo)
    return None


MACRO_EXPANS = MACRO(
    nom="MACRO_EXPANS",
    op=OPS("code_aster.MacroCommands.macro_expans_ops.macro_expans_ops"),
    sd_prod=macro_expans_prod,
    reentrant="n",
    fr=tr(
        "Outil d'expansion de resultats exprimentaux sur une base definie sur un modele numerique"
    ),
    MODELE_CALCUL=FACT(
        statut="o",
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        BASE=SIMP(statut="o", typ=(mode_meca,)),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
    ),
    MODELE_MESURE=FACT(
        statut="o",
        MODELE=SIMP(statut="o", typ=(modele_sdaster)),
        MESURE=SIMP(statut="o", typ=(dyna_trans, dyna_harmo, mode_meca, mode_meca_c)),
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            defaut="DEPL",
            into=("DEPL", "VITE", "ACCE", "SIEF_NOEU", "EPSI_NOEU"),
        ),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
    ),
    NUME_DDL=SIMP(statut="f", typ=nume_ddl_sdaster),
    RESU_NX=SIMP(statut="f", typ=(mode_meca, dyna_harmo, CO)),
    RESU_EX=SIMP(statut="f", typ=(mode_meca, dyna_harmo, CO)),
    RESU_ET=SIMP(statut="f", typ=(mode_meca, dyna_harmo, CO)),
    RESU_RD=SIMP(statut="f", typ=(mode_meca, dyna_harmo, CO)),
    RESOLUTION=FACT(
        statut="f",
        METHODE=SIMP(statut="f", typ="TXM", defaut="LU", into=("LU", "SVD")),
        b_svd=BLOC(
            condition="""equal_to("METHODE", 'SVD')""", EPS=SIMP(statut="f", typ="R", defaut=0.0)
        ),
        REGUL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "NORM_MIN", "TIK_RELA")),
        b_regul=BLOC(
            condition="""not equal_to("REGUL", 'NON')""",
            regles=(PRESENT_ABSENT("COEF_PONDER", "COEF_PONDER_F"),),
            COEF_PONDER=SIMP(statut="f", typ="R", max="**"),
            COEF_PONDER_F=SIMP(
                statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max="**"
            ),
        ),
    ),
)
