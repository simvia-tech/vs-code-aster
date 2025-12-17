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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_vect_elem_prod(self, OPTION, **args):
    if args.get("__all__"):
        return (vect_elem_depl_r, vect_elem_temp_r, vect_elem_pres_c)

    if OPTION == "CHAR_MECA":
        return vect_elem_depl_r
    if OPTION == "CHAR_THER":
        return vect_elem_temp_r
    if OPTION == "CHAR_ACOU":
        return vect_elem_pres_c
    raise AsException("type de concept resultat non prevu")


CALC_VECT_ELEM = MACRO(
    nom="CALC_VECT_ELEM",
    op=OPS("code_aster.MacroCommands.calc_vect_elem_ops.calc_vect_elem_ops"),
    sd_prod=calc_vect_elem_prod,
    reentrant="n",
    fr=tr("Calcul des seconds membres élémentaires"),
    OPTION=SIMP(statut="o", typ="TXM", into=("CHAR_MECA", "CHAR_THER", "CHAR_ACOU")),
    b_char_meca=BLOC(
        condition="""equal_to("OPTION", 'CHAR_MECA')""",
        regles=(AU_MOINS_UN("CHARGE", "MODELE"),),
        CHARGE=SIMP(statut="f", typ=char_meca, validators=NoRepeat(), max="**"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        b_charge=BLOC(
            condition="""exists("CHARGE")""",
            fr=tr("modèle ne contenant pas de sous-structure"),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            INST=SIMP(statut="f", typ="R", defaut=0.0e0),
            MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        ),
        b_modele=BLOC(
            condition="""(exists("MODELE"))""",
            fr=tr("modèle contenant une sous-structure"),
            SOUS_STRUC=FACT(
                statut="o",
                min=0o1,
                regles=(UN_PARMI("TOUT", "SUPER_MAILLE"),),
                CAS_CHARGE=SIMP(statut="o", typ="TXM"),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                SUPER_MAILLE=SIMP(statut="f", typ=ma, validators=NoRepeat(), max="**"),
            ),
        ),
    ),
    b_char_ther=BLOC(
        condition="""equal_to("OPTION", 'CHAR_THER')""",
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        CHARGE=SIMP(statut="o", typ=char_ther, validators=NoRepeat(), max="**"),
        INST=SIMP(statut="f", typ="R", defaut=0.0e0),
    ),
    b_char_acou=BLOC(
        condition="""equal_to("OPTION", 'CHAR_ACOU')""",
        CHAM_MATER=SIMP(statut="o", typ=cham_mater),
        CHARGE=SIMP(statut="o", typ=char_acou, validators=NoRepeat(), max="**"),
    ),
)
