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

# person_in_charge: adrien.guilloux at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

LISS_SPECTRE = MACRO(
    nom="LISS_SPECTRE",
    op=OPS("code_aster.MacroCommands.liss_spectre_ops.liss_spectre_ops"),
    reentrant="n",
    fr=tr("Lissage de spectre, post-traitement de séisme"),
    SPECTRE=FACT(
        statut="o",
        max="**",
        regles=(UN_PARMI("TABLE", "NAPPE"),),
        TABLE=SIMP(statut="f", typ=table_sdaster),
        NAPPE=SIMP(statut="f", typ=nappe_sdaster),
        ELARG=SIMP(statut="f", typ="R"),
        b_nappe=BLOC(
            condition="""exists("NAPPE")""",
            DIRECTION=SIMP(statut="o", typ="TXM", into=("X", "Y", "Z", "H")),
            NOM=SIMP(statut="o", typ="TXM"),
            BATIMENT=SIMP(statut="f", typ="TXM"),
            COMMENTAIRE=SIMP(statut="f", typ="TXM"),
        ),  # fin b_nappe
    ),
    OPTION=SIMP(statut="o", typ="TXM", into=("VERIFICATION", "CONCEPTION")),
    FREQ_MIN=SIMP(statut="f", typ="R"),
    FREQ_MAX=SIMP(statut="f", typ="R"),
    NB_FREQ_LISS=SIMP(
        statut="f", typ="I", max=2, val_min=1, defaut=10, fr=tr("Nb de points pour le lissage ")
    ),
    ZPA=SIMP(statut="f", typ="R"),
    # format du graphique
    BORNE_X=SIMP(
        statut="f", typ="R", min=2, max=2, fr=tr("Intervalles de variation des abscisses")
    ),
    BORNE_Y=SIMP(
        statut="f", typ="R", min=2, max=2, fr=tr("Intervalles de variation des ordonnées")
    ),
    ECHELLE_X=SIMP(
        statut="f",
        typ="TXM",
        defaut="LIN",
        into=("LIN", "LOG"),
        fr=tr("Type d'échelle pour les abscisses"),
    ),
    ECHELLE_Y=SIMP(
        statut="f",
        typ="TXM",
        defaut="LIN",
        into=("LIN", "LOG"),
        fr=tr("Type d'échelle pour les ordonnées"),
    ),
    LEGENDE_X=SIMP(statut="f", typ="TXM", fr=tr("Légende associée à l'axe des abscisses")),
    LEGENDE_Y=SIMP(statut="f", typ="TXM", fr=tr("Légende associée à l'axe des ordonnées")),
)
