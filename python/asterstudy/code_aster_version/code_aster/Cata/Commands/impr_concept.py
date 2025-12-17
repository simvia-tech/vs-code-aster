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

# person_in_charge: nicolas.sellenet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_CONCEPT = PROC(
    nom="IMPR_CONCEPT",
    op=21,
    fr=tr("Imprimer un concept d'un calcul (champs de donnée) au format MED"),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="MED", into=("MED", "RESULTAT")),
    UNITE=SIMP(statut="f", typ=UnitType("med"), defaut=80, inout="out"),
    b_format_med=BLOC(
        condition="""equal_to("FORMAT", 'MED')""",
        # same keyword in IMPR_RESU, keep consistency
        VERSION_MED=SIMP(
            statut="f",
            typ="TXM",
            into=("3.3.1", "4.0.0", "4.1.0"),
            defaut="3.3.1",
            fr=tr("Choix de la version du fichier MED"),
        ),
    ),
    CONCEPT=FACT(
        statut="o",
        max="**",
        fr=tr(
            'Pour imprimer les champs de "données" à des fins de visualisation (controle des affectations).'
        ),
        regles=(UN_PARMI("CHAM_MATER", "CARA_ELEM", "CHARGE"),),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
        CHARGE=SIMP(statut="f", typ=char_meca),
        b_cara_elem=BLOC(
            condition="""exists("CARA_ELEM")""",
            fr=tr("impression des repères locaux."),
            REPERE_LOCAL=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "ELEM", "ELNO")),
            b_reploc=BLOC(
                condition="""not equal_to("REPERE_LOCAL", 'NON')""",
                fr=tr("impression des repères locaux."),
                MODELE=SIMP(statut="o", typ=modele_sdaster),
            ),
        ),  # end b_cara_elem
    ),  # end fkw_concept
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
