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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MECA_NON_LINE = MACRO(
    nom="MECA_NON_LINE",
    op=OPS("code_aster.MacroCommands.meca_non_line_ops.meca_non_line_ops"),
    sd_prod=evol_noli,
    fr=tr(
        "Calcul de l'évolution mécanique ou thermo-hydro-mécanique couplée, en quasi-statique,"
        " d'une structure en non linéaire"
    ),
    reentrant="f:RESULTAT",
    reuse=SIMP(statut="c", typ=CO),
    # -------------------------------------------------------------------
    RESULTAT=SIMP(
        statut="f", typ=evol_noli, fr=tr("Objet qui sera enrichi des nouveaux instants calculés")
    ),
    # -------------------------------------------------------------------
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    # -------------------------------------------------------------------
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    # -------------------------------------------------------------------
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    # -------------------------------------------------------------------
    EXCIT=FACT(
        statut="f",
        max="**",
        CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
    ),
    # -------------------------------------------------------------------
    CONTACT=C_CONTACT(),
    # -------------------------------------------------------------------
    COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
    # -------------------------------------------------------------------
    ETAT_INIT=C_ETAT_INIT("MECA_NON_LINE", "f"),
    # -------------------------------------------------------------------
    RECH_LINEAIRE=C_RECH_LINEAIRE(),
    # -------------------------------------------------------------------
    INCREMENT=C_INCREMENT(),
    # -------------------------------------------------------------------
    METHODE=SIMP(statut="f", typ="TXM", defaut="NEWTON", into=("NEWTON", "SNES")),
    b_meth_newton=BLOC(
        condition="""equal_to("METHODE", 'NEWTON') or equal_to("METHODE", 'SNES') """,
        NEWTON=C_NEWTON("MECA_NON_LINE"),
    ),
    # -------------------------------------------------------------------
    CONVERGENCE=C_CONVERGENCE("MECA_NON_LINE"),
    # -------------------------------------------------------------------
    ARCHIVAGE=C_ARCHIVAGE(),
    # -------------------------------------------------------------------
    b_newton_solveur=BLOC(
        condition="""equal_to("METHODE", 'NEWTON')""", SOLVEUR=C_SOLVEUR("STAT_NON_LINE")
    ),
    b_snes_solveur=BLOC(
        condition="""equal_to("METHODE", 'SNES')""", SOLVEUR=C_SOLVEUR("STAT_NON_LINE_SNES")
    ),
    # -------------------------------------------------------------------
    SCHEMA_TEMPS=FACT(
        statut="f",
        SCHEMA=SIMP(statut="o", min=1, max=1, typ="TXM", into=("NEWMARK",)),
        COEF_MASS_SHIFT=SIMP(statut="f", typ="R", defaut=0.0e0),
        # b_tchamwa=BLOC(
        #     condition="""equal_to("SCHEMA", 'TCHAMWA')""",
        #     PHI=SIMP(statut="f", typ="R", defaut=1.05),
        # ),
        b_newmark=BLOC(
            condition="""equal_to("SCHEMA", 'NEWMARK')""",
            BETA=SIMP(statut="f", typ="R", defaut=0.25),
            GAMMA=SIMP(statut="f", typ="R", defaut=0.5),
        ),
        # b_hht=BLOC(
        #     condition="""equal_to("SCHEMA", 'HHT')""",
        #     ALPHA=SIMP(statut="f", typ="R", defaut=-0.1),
        #     MODI_EQUI=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        # ),
        # b_explicit=BLOC(
        #     condition="""equal_to("SCHEMA", 'TCHAMWA') or equal_to("SCHEMA", 'DIFF_CENT')""",
        #     STOP_CFL=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        #     FORMULATION=SIMP(statut="o", typ="TXM", into=("ACCELERATION",)),
        # ),
        b_implicit=BLOC(
            condition="""not equal_to("SCHEMA", 'TCHAMWA') and not equal_to("SCHEMA", 'DIFF_CENT')""",
            FORMULATION=SIMP(statut="o", max=1, typ="TXM", into=("DEPLACEMENT",)),
        ),
    ),
    # -------------------------------------------------------------------
    INFO=SIMP(statut="f", typ="I", into=(1, 2, 3, 4)),
)
