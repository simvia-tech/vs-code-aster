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


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_gp_prod(self, TRANCHE_2D, GPMAX, **args):
    """Typage des sd_prod"""
    if args.get("__all__"):
        return ([table_sdaster], [None, cham_elem], [None, table_sdaster])

    if TRANCHE_2D:
        if TRANCHE_2D["ZONE_MAIL"] == "NON":
            if TRANCHE_2D.get("CHAMP_VISU"):
                self.type_sdprod(TRANCHE_2D["CHAMP_VISU"], cham_elem)
    if GPMAX is not None:
        self.type_sdprod(GPMAX, table_sdaster)
    return table_sdaster


CALC_GP = MACRO(
    nom="CALC_GP",
    op=OPS("code_aster.MacroCommands.calc_gp_ops.calc_gp_ops"),
    sd_prod=calc_gp_prod,
    #                   sd_prod=table_sdaster,
    reentrant="n",
    fr=tr("calcul du parametre de clivage energetique Gp en 2D et en 3D"),
    regles=UN_PARMI("TRANCHE_2D", "TRANCHE_3D"),
    RESULTAT=SIMP(
        statut="o", typ=resultat_sdaster, fr=tr("Resultat d'une commande globale STAT_NON_LINE")
    ),
    LIST_INST=SIMP(statut="o", typ=(listr8_sdaster)),
    PRECISION=SIMP(
        statut="f", typ="R", validators=NoRepeat(), val_min=0.0, val_max=1e-3, defaut=1e-6
    ),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="ABSOLU", into=("RELATIF", "ABSOLU")),
    TRANCHE_2D=FACT(
        statut="f",
        max=1,
        ZONE_MAIL=SIMP(statut="o", typ="TXM", into=("NON", "OUI")),
        b_cop=BLOC(
            condition="""equal_to("ZONE_MAIL", 'OUI')""",
            fr=tr("Les copeaux sont mailles"),
            GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
            TAILLE=SIMP(statut="o", typ=listr8_sdaster),
        ),
        b_ss_cop=BLOC(
            condition="""equal_to("ZONE_MAIL", 'NON')""",
            fr=tr("Les copeaux ne sont pas mailles"),
            CENTRE=SIMP(statut="o", typ="R", max=2),
            RAYON=SIMP(statut="o", typ="R", max=1),
            ANGLE=SIMP(statut="o", typ="R", max=1),
            TAILLE=SIMP(statut="o", typ="R", max=1),
            NB_ZONE=SIMP(statut="o", typ="I"),
            CHAMP_VISU=SIMP(statut="f", typ=CO),
        ),
    ),
    TRANCHE_3D=FACT(
        statut="f", max="**", GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**")
    ),
    b_tranche_2d=BLOC(
        condition="""exists("TRANCHE_2D")""",
        SYME=SIMP(
            statut="o", typ="TXM", into=("NON", "OUI"), fr=tr("multiplication par 2 si SYME=OUI")
        ),
    ),
    b_tranche_3d=BLOC(
        condition="""exists("TRANCHE_3D")""", FOND_FISS=SIMP(statut="o", typ=fond_fissure, max=1)
    ),
    GPMAX=SIMP(statut="f", typ=CO),
)
