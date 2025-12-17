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


POST_NEWMARK = MACRO(
    nom="POST_NEWMARK",
    op=OPS("code_aster.MacroCommands.post_newmark_ops.post_newmark_ops"),
    fr=tr("Calcul des déplacements résiduels des ouvrages en remblai par méthode de Newmark"),
    sd_prod=table_sdaster,
    reentrant="n",
    regles=(UN_PARMI("RAYON", "MAILLAGE_GLIS"), AU_MOINS_UN("RESULTAT", "RESULTAT_PESANTEUR")),
    MAILLAGE_GLIS=SIMP(statut="f", typ=maillage_sdaster, fr="Maillage de la zone de glissement"),
    RAYON=SIMP(statut="f", typ="R", fr="Rayon du cercle de glissement"),
    b_RAYON=BLOC(
        condition="""exists("RAYON")""",
        CENTRE_X=SIMP(statut="o", typ="R", fr="Position de la coordonée X du cercle de glissement"),
        CENTRE_Y=SIMP(statut="o", typ="R", fr="Position de la coordonée Y du cercle de glissement"),
        RAFF_CERCLE=SIMP(statut="f", typ="I", default=7, fr="Raffinement du maillage de cercle"),
    ),
    b_MAIL_GLIS=BLOC(
        condition="""exists("MAILLAGE_GLIS")""",
        GROUP_MA_GLIS=SIMP(
            statut="f", typ=grma, max="**", fr="GROUP_MA associé à la zone de glissement"
        ),
        GROUP_MA_LIGNE=SIMP(
            statut="f", typ=grma, max="**", fr="GROUP_MA associé à la ligne de glissement"
        ),
    ),
    POSITION=SIMP(statut="f", typ="TXM", into=("AMONT", "AVAL"), defaut="AVAL"),
    RESULTAT=SIMP(
        statut="f", typ=(dyna_trans, evol_noli), fr="Concept résultat du calcul dynamique"
    ),
    b_RESULTAT=BLOC(
        condition="""exists("RESULTAT")""",
        VERI_MASSE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
        b_VERI_MASS=BLOC(
            condition="""equal_to("VERI_MASSE", 'OUI')""",
            RESI_RELA=SIMP(
                statut="f",
                typ="R",
                default=0.05,
                val_min=0.0,
                fr="Tolérance d'arrêt des itérations",
            ),
            ITER_MAXI=SIMP(
                statut="f", typ="I", default=2, val_min=1, fr="Nombre maximal d'itérations"
            ),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        ),
    ),
    RESULTAT_PESANTEUR=SIMP(
        statut="f",
        typ=(evol_noli, evol_elas),
        fr="Champ des contraintes issu du résultat du calcul à la pesanteur",
    ),
    b_RESULTAT_PESANTEUR=BLOC(
        condition="""exists("RESULTAT_PESANTEUR")""",
        CHAM_PHI=SIMP(statut="o", typ=cham_no_sdaster, fr="Champ de phi en dégrées"),
        CHAM_COHESION=SIMP(statut="o", typ=cham_no_sdaster, fr="Champ de cohesion"),
        CHAM_FS=SIMP(statut="f", typ=CO, fr="Champ du facteur de sécurité local"),
    ),
    KY=SIMP(statut="f", typ="R", fr="Valeur de ky pour le calcul de l'accélération critique"),
    GROUP_MA_CALC=SIMP(statut="o", typ=grma, max="**", fr="GROUP_MA associé au modèle utilisé"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
