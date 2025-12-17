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

# person_in_charge: sylvie.michel-ponnelle at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_PRECONT = MACRO(
    nom="CALC_PRECONT",
    op=OPS("code_aster.MacroCommands.calc_precont_ops.calc_precont_ops"),
    sd_prod=evol_noli,
    fr=tr("Imposer la tension définie par le BPEL dans les cables"),
    reentrant="f:ETAT_INIT:EVOL_NOLI",
    reuse=SIMP(statut="c", typ=CO),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    CARA_ELEM=SIMP(statut="o", typ=cara_elem),
    CABLE_BP=SIMP(statut="o", typ=cabl_precont, validators=NoRepeat(), max="**"),
    CABLE_BP_INACTIF=SIMP(statut="f", typ=cabl_precont, validators=NoRepeat(), max="**"),
    INCREMENT=C_INCREMENT(),
    RECH_LINEAIRE=C_RECH_LINEAIRE(),
    CONVERGENCE=C_CONVERGENCE("MECA_NON_LINE"),
    ARCHIVAGE=C_ARCHIVAGE(),
    # -------------------------------------------------------------------
    ETAT_INIT=C_ETAT_INIT("MECA_NON_LINE", "f"),
    # -------------------------------------------------------------------
    METHODE=SIMP(statut="f", typ="TXM", defaut="NEWTON", into=("NEWTON", "IMPLEX")),
    b_meth_newton=BLOC(condition="""equal_to("METHODE", 'NEWTON')""", NEWTON=C_NEWTON()),
    ENERGIE=FACT(
        statut="f", max=1, CALCUL=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI")
    ),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("CALC_PRECONT"),
    # -------------------------------------------------------------------
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
    EXCIT=FACT(
        statut="o",
        max="**",
        CHARGE=SIMP(statut="o", typ=char_meca),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE", "DIDI")),
    ),
    COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
)
