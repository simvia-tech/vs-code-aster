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

# person_in_charge: mohamed-amine.hassini at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_MODE_ROTATION = MACRO(
    nom="CALC_MODE_ROTATION",
    op=OPS("code_aster.MacroCommands.calc_mode_rotation_ops.calc_mode_rotation_ops"),
    sd_prod=table_container,
    reentrant="n",
    fr=tr("calculer les fréquences et modes d'un système en fonction des " "vitesses de rotation"),
    MATR_RIGI=SIMP(statut="o", typ=matr_asse_depl_r),
    MATR_MASS=SIMP(statut="o", typ=matr_asse_depl_r),
    MATR_AMOR=SIMP(statut="f", typ=matr_asse_depl_r),
    MATR_GYRO=SIMP(statut="f", typ=matr_asse_depl_r),
    VITE_ROTA=SIMP(statut="f", typ="R", max="**"),
    METHODE=SIMP(statut="f", typ="TXM", defaut="QZ", into=("QZ", "SORENSEN")),
    CALC_FREQ=FACT(
        statut="d",
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            defaut="PLUS_PETITE",
            into=("PLUS_PETITE", "CENTRE"),
            fr=tr("Choix de l option et par conséquent du shift du problème modal"),
        ),
        b_plus_petite=BLOC(
            condition="""equal_to("OPTION", 'PLUS_PETITE')""",
            fr=tr("Recherche des plus petites valeurs propres"),
            NMAX_FREQ=SIMP(statut="f", typ="I", defaut=10, val_min=0),
            SEUIL_FREQ=SIMP(statut="f", typ="R", defaut=1.0e-2),
        ),
        b_centre=BLOC(
            condition="""equal_to("OPTION", 'CENTRE')""",
            fr=tr("Recherche des valeurs propres les plus proches d une valeur donnée"),
            FREQ=SIMP(
                statut="o",
                typ="R",
                fr=tr("Fréquence autour de laquelle on cherche les fréquences propres"),
            ),
            AMOR_REDUIT=SIMP(statut="f", typ="R"),
            NMAX_FREQ=SIMP(statut="f", typ="I", defaut=10, val_min=0),
            SEUIL_FREQ=SIMP(statut="f", typ="R", defaut=1.0e-2),
        ),
    ),
    VERI_MODE=FACT(
        statut="d",
        STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        SEUIL=SIMP(statut="f", typ="R", defaut=1.0e-6),
        PREC_SHIFT=SIMP(statut="f", typ="R", defaut=5.0e-3),
        STURM=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
)
