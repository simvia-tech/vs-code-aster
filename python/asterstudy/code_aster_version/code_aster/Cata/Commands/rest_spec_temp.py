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


def rest_spec_temp_prod(RESU_GENE, RESULTAT, **args):
    if args.get("__all__"):
        return (dyna_trans, tran_gene, dyna_harmo, harm_gene)
    if AsType(RESULTAT) == dyna_harmo:
        return dyna_trans
    if AsType(RESU_GENE) == harm_gene:
        return tran_gene
    if AsType(RESULTAT) == dyna_trans:
        return dyna_harmo
    if AsType(RESU_GENE) == tran_gene:
        return harm_gene
    raise AsException("type de concept resultat non prevu")


REST_SPEC_TEMP = OPER(
    nom="REST_SPEC_TEMP",
    op=181,
    sd_prod=rest_spec_temp_prod,
    fr=tr("Transformee de Fourier d un resultat"),
    reentrant="n",
    regles=UN_PARMI("RESU_GENE", "RESULTAT"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    RESU_GENE=SIMP(statut="f", typ=(harm_gene, tran_gene)),
    RESULTAT=SIMP(statut="f", typ=(dyna_harmo, dyna_trans)),
    METHODE=SIMP(statut="f", typ="TXM", defaut="PROL_ZERO", into=("PROL_ZERO", "TRONCATURE")),
    SYMETRIE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NOM_CHAM=SIMP(
        statut="f", typ="TXM", validators=NoRepeat(), max=3, into=("DEPL", "VITE", "ACCE")
    ),
    ACCELERATION_MPI=SIMP(statut="c", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    prol_puissance_sup=BLOC(
        condition="""equal_to("METHODE",'PROL_ZERO' )""", N_PUIS=SIMP(statut="o", typ="I")
    ),
)
