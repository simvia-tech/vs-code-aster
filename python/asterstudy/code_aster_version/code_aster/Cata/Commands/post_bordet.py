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

# person_in_charge: david.haboussa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_BORDET = MACRO(
    nom="POST_BORDET",
    op=OPS("code_aster.MacroCommands.post_bordet_ops.post_bordet_ops"),
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr("calcul de la probabilite de clivage via le modele de Bordet"),
    regles=(UN_PARMI("TOUT", "GROUP_MA"), UN_PARMI("INST", "NUME_ORDRE")),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    GROUP_MA=SIMP(
        statut="f",
        typ=grma,
        validators=NoRepeat(),
        max="**",
        fr=tr("le calcul ne sera effectué que sur ces mailles"),
    ),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat()),
    PRECISION=SIMP(
        statut="f", typ="R", validators=NoRepeat(), val_min=0.0, val_max=1e-3, defaut=1e-6
    ),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="ABSOLU", into=("RELATIF", "ABSOLU")),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat()),
    PROBA_NUCL=SIMP(
        statut="f",
        typ="TXM",
        into=("NON", "OUI"),
        defaut="NON",
        fr=tr("prise en compte du facteur exponentiel"),
    ),
    b_nucl=BLOC(
        condition="""equal_to("PROBA_NUCL", 'OUI')""",
        PARAM=FACT(
            statut="o",
            M=SIMP(statut="o", typ="R", val_min=0.0e0),
            SIGM_REFE=SIMP(statut="o", typ=fonction_sdaster),
            VOLU_REFE=SIMP(statut="o", typ="R", val_min=0.0e0),
            SIG_CRIT=SIMP(statut="o", typ="R", val_min=0.0e0),
            SEUIL_REFE=SIMP(statut="o", typ="R", val_min=0.0e0),
            SEUIL_CALC=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster)),
            DEF_PLAS_REFE=SIMP(statut="o", typ="R"),
        ),
    ),
    b_prop=BLOC(
        condition="""equal_to("PROBA_NUCL", 'NON')""",
        PARAM=FACT(
            statut="o",
            M=SIMP(statut="o", typ="R", val_min=0.0e0),
            SIGM_REFE=SIMP(statut="o", typ=fonction_sdaster),
            VOLU_REFE=SIMP(statut="o", typ="R", val_min=0.0e0),
            SIG_CRIT=SIMP(statut="o", typ="R", val_min=0.0e0),
            SEUIL_REFE=SIMP(statut="o", typ="R", val_min=0.0e0),
            SEUIL_CALC=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster)),
        ),
    ),
    RESULTAT=SIMP(
        statut="o", typ=resultat_sdaster, fr=tr("Resultat d'une commande globale STAT_NON_LINE")
    ),
    TEMP=SIMP(statut="o", typ=(fonction_sdaster,)),
    COEF_MULT=SIMP(statut="f", typ="R", defaut=1.0),
)
