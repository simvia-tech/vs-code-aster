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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_MODELE_GENE = OPER(
    nom="DEFI_MODELE_GENE",
    op=126,
    sd_prod=modele_gene,
    reentrant="n",
    fr=tr(
        "Créer la structure globale à partir des sous-structures en sous-structuration dynamique"
    ),
    SOUS_STRUC=FACT(
        statut="o",
        max="**",
        NOM=SIMP(statut="o", typ="TXM"),
        MACR_ELEM_DYNA=SIMP(statut="o", typ=macr_elem_dyna),
        ANGL_NAUT=SIMP(statut="o", typ="R", max=3),
        TRANS=SIMP(statut="o", typ="R", max=3),
    ),
    LIAISON=FACT(
        statut="o",
        max="**",
        SOUS_STRUC_1=SIMP(statut="o", typ="TXM"),
        INTERFACE_1=SIMP(statut="o", typ="TXM"),
        SOUS_STRUC_2=SIMP(statut="o", typ="TXM"),
        INTERFACE_2=SIMP(statut="o", typ="TXM"),
        regles=(EXCLUS("GROUP_MA_MAIT_1", "GROUP_MA_MAIT_2"),),
        GROUP_MA_MAIT_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_MA_MAIT_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        OPTION=SIMP(statut="f", typ="TXM", defaut="CLASSIQUE", into=("REDUIT", "CLASSIQUE")),
    ),
    VERIF=FACT(
        statut="f",
        max="**",
        #  dans la doc U stop_erreur est obligatoire
        STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
