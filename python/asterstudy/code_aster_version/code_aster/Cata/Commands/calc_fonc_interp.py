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


def calc_fonc_interp_prod(FONCTION, NOM_PARA_FONC, **args):
    if args.get("__all__"):
        return (nappe_sdaster, fonction_sdaster, fonction_c, formule)

    if AsType(FONCTION) == nappe_sdaster:
        return nappe_sdaster
    elif AsType(FONCTION) == fonction_sdaster:
        return fonction_sdaster
    elif AsType(FONCTION) == fonction_c:
        return fonction_c
    elif AsType(FONCTION) == formule_c:
        return fonction_c
    elif AsType(FONCTION) == formule:
        if NOM_PARA_FONC is not None:
            return nappe_sdaster
        return fonction_sdaster
    raise AsException("type de concept resultat non prevu")


CALC_FONC_INTERP = OPER(
    nom="CALC_FONC_INTERP",
    op=134,
    sd_prod=calc_fonc_interp_prod,
    docu="U4.32.01",
    reentrant="n",
    fr=tr("Définit une fonction (ou une nappe) à partir d'une fonction FORMULE à 1 ou 2 variables"),
    regles=(UN_PARMI("VALE_PARA", "LIST_PARA"),),
    FONCTION=SIMP(statut="o", typ=(formule, fonction_sdaster, nappe_sdaster, fonction_c)),
    VALE_PARA=SIMP(statut="f", typ="R", max="**"),
    LIST_PARA=SIMP(statut="f", typ=listr8_sdaster),
    NOM_RESU=SIMP(statut="f", typ="TXM"),
    NOM_PARA=SIMP(statut="f", typ="TXM"),
    INTERPOL=SIMP(statut="f", typ="TXM", max=2, into=("LIN", "LOG")),
    PROL_DROITE=SIMP(statut="f", typ="TXM", into=("EXCLU", "CONSTANT", "LINEAIRE")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", into=("EXCLU", "CONSTANT", "LINEAIRE")),
    NOM_PARA_FONC=SIMP(statut="f", typ="TXM"),
    b_eval_nappe=BLOC(
        condition="""exists("NOM_PARA_FONC")""",
        regles=(UN_PARMI("VALE_PARA_FONC", "LIST_PARA_FONC"),),
        VALE_PARA_FONC=SIMP(statut="f", typ="R", max="**"),
        LIST_PARA_FONC=SIMP(statut="f", typ=listr8_sdaster),
        INTERPOL_FONC=SIMP(statut="f", typ="TXM", max=2, into=("LIN", "LOG")),
        PROL_DROITE_FONC=SIMP(statut="f", typ="TXM", into=("EXCLU", "CONSTANT", "LINEAIRE")),
        PROL_GAUCHE_FONC=SIMP(statut="f", typ="TXM", into=("EXCLU", "CONSTANT", "LINEAIRE")),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
