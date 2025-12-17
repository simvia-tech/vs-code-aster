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


def extr_mode_prod(FILTRE_MODE, **args):
    if args.get("__all__"):
        return (mode_meca, mode_meca_c, mode_gene)

    vale = FILTRE_MODE[0]["MODE"]
    if AsType(vale) == mode_meca:
        return mode_meca
    if AsType(vale) == mode_meca_c:
        return mode_meca_c
    if AsType(vale) == mode_gene:
        return mode_gene
    raise AsException("type de concept resultat non prevu")


EXTR_MODE = OPER(
    nom="EXTR_MODE",
    op=168,
    sd_prod=extr_mode_prod,
    reentrant="n",
    fr=tr("Extraire séléctivement des modes des structures de données modales"),
    FILTRE_MODE=FACT(
        statut="o",
        max="**",
        regles=(
            UN_PARMI(
                "TOUT_ORDRE", "NUME_ORDRE", "NUME_MODE", "NUME_MODE_EXCLU", "FREQ_MIN", "CRIT_EXTR"
            ),
        ),
        MODE=SIMP(statut="o", typ=(mode_meca, mode_meca_c, mode_gene)),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NUME_MODE_EXCLU=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        FREQ_MIN=SIMP(statut="f", typ="R"),
        CRIT_EXTR=SIMP(statut="f", typ="TXM", into=("MASS_EFFE_UN", "MASS_GENE", "MASS_EFFE")),
        b_freq_min=BLOC(
            condition="""exists("FREQ_MIN")""",
            FREQ_MAX=SIMP(statut="o", typ="R"),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        ),
        b_crit_extr=BLOC(
            condition="""exists("CRIT_EXTR")""",
            regles=(AU_MOINS_UN("SEUIL", "SEUIL_X", "SEUIL_Y", "SEUIL_Z"),),
            SEUIL=SIMP(statut="f", typ="R"),
            SEUIL_X=SIMP(statut="f", typ="R"),
            SEUIL_Y=SIMP(statut="f", typ="R"),
            SEUIL_Z=SIMP(statut="f", typ="R"),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    IMPRESSION=FACT(
        statut="f",
        CUMUL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        CRIT_EXTR=SIMP(
            statut="f",
            typ="TXM",
            defaut="MASS_EFFE_UN",
            into=("MASS_EFFE_UN", "MASS_GENE", "MASS_EFFE"),
        ),
    ),
)
