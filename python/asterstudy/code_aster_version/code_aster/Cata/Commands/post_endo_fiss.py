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

# person_in_charge: marina.bottoni at edf.fr

# ---------------------------------------------------------------------------
#                  POST_ENDO_FISS
# RECHERCHE DU TRAJET DE FISSURATION SUR UN
#  CHAMP SCALAIRE 2D


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def post_endo_fiss_prod(self, TABLE, **args):
    if args.get("__all__"):
        return ([maillage_sdaster], [table_sdaster])
    self.type_sdprod(TABLE, table_sdaster)
    return maillage_sdaster


POST_ENDO_FISS = MACRO(
    nom="POST_ENDO_FISS",
    op=OPS("code_aster.MacroCommands.post_endo_fiss_ops.post_endo_fiss_ops"),
    sd_prod=post_endo_fiss_prod,
    reentrant="n",
    fr=tr("Individuation du trace d'une fissure a partir d'un champ scalaire pertinant"),
    TABLE=SIMP(statut="o", typ=CO),
    regles=(UN_PARMI("RESULTAT", "CHAM_GD"),),
    OUVERTURE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
    b_resultat=BLOC(
        condition="""exists("RESULTAT")""",
        regles=(UN_PARMI("NUME_ORDRE", "INST"),),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat()),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat()),
    ),
    # b_champ    = BLOC(condition = """exists("CHAM_GD")""",),
    CHAM_GD=SIMP(statut="f", typ=(cham_gd_sdaster)),
    RESULTAT=SIMP(statut="f", typ=(evol_noli)),
    NOM_CMP=SIMP(statut="o", typ="TXM"),
    NOM_CHAM=SIMP(statut="o", typ="TXM", fr=tr("nom du champ a post-traiter")),
    RECHERCHE=FACT(
        statut="o",
        min=1,
        max="**",
        regles=(PRESENT_ABSENT("TOUT", "GROUP_MA"),),
        LONG_ORTH=SIMP(statut="o", typ="R"),
        NB_POINT=SIMP(statut="f", typ="I", defaut=500),
        PAS=SIMP(statut="o", typ="R"),
        LONG_REG=SIMP(statut="o", typ="R"),
        BORNE_MIN=SIMP(statut="f", typ="R", defaut=0.5),
        ANGL_MAX=SIMP(statut="f", typ="R", defaut=120.0),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat()),
        BORNE_MAX=SIMP(statut="f", typ="R"),
    ),
)
