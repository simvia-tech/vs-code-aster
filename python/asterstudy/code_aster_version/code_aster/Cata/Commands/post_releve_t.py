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

# person_in_charge: natacha.bereux at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_RELEVE_T = OPER(
    nom="POST_RELEVE_T",
    op=51,
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr(
        "Extraire des valeurs de composantes de champs de grandeurs pour y effectuer des calculs (moyenne,invariants,..)"
        " ou pour les exprimer dans d'autres repères"
    ),
    docu="U4.81.21",
    ACTION=FACT(
        statut="o",
        max="**",
        regles=(UN_PARMI("RESULTAT", "CHAM_GD"),),
        OPERATION=SIMP(
            statut="o",
            typ="TXM",
            into=("EXTRACTION", "MOYENNE", "MOYENNE_ARITH", "EXTREMA"),
            validators=NoRepeat(),
            max=2,
        ),
        INTITULE=SIMP(statut="o", typ="TXM"),
        CHAM_GD=SIMP(statut="f", typ=(cham_no_sdaster, cham_elem)),
        RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
        b_extrac=BLOC(
            condition="""exists("RESULTAT")""",
            fr=tr("extraction des résultats"),
            regles=(
                EXCLUS(
                    "TOUT_ORDRE",
                    "NUME_ORDRE",
                    "LIST_ORDRE",
                    "NUME_MODE",
                    "LIST_MODE",
                    "INST",
                    "LIST_INST",
                    "FREQ",
                    "LIST_FREQ",
                    "NOEUD_CMP",
                    "NOM_CAS",
                ),
            ),
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
            NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
            LIST_MODE=SIMP(statut="f", typ=listis_sdaster),
            NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
            NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
            FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
        b_extrema=BLOC(
            condition="""equal_to('OPERATION', 'EXTREMA')""",
            fr=tr("recherche de MIN MAX"),
            regles=(EXCLUS("TOUT_CMP", "NOM_CMP"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
        ),
        b_MOYENNE_ARITH=BLOC(
            condition="""is_in('OPERATION', 'MOYENNE_ARITH')""",
            fr=tr("moyenne sur des groupes"),
            regles=(EXCLUS("TOUT_CMP", "NOM_CMP"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
        ),
        b_autre=BLOC(
            condition="""not is_in('OPERATION', ('EXTREMA', 'MOYENNE_ARITH'))""",
            fr=tr("extraction et moyenne"),
            regles=(
                AU_MOINS_UN("GROUP_NO", "NOEUD"),
                UN_PARMI("TOUT_CMP", "NOM_CMP", "INVARIANT", "ELEM_PRINCIPAUX", "RESULTANTE"),
                PRESENT_PRESENT("TRAC_DIR", "DIRECTION"),
                ENSEMBLE("MOMENT", "POINT"),
                PRESENT_PRESENT("MOMENT", "RESULTANTE"),
                PRESENT_ABSENT("TOUT_CMP", "TRAC_DIR", "TRAC_NOR"),
                EXCLUS("TRAC_DIR", "TRAC_NOR"),
                PRESENT_PRESENT("ORIGINE", "AXE_Z"),
            ),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            INVARIANT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            ELEM_PRINCIPAUX=SIMP(statut="f", typ="TXM", into=("OUI",)),
            RESULTANTE=SIMP(
                statut="f", typ="TXM", max="**", into=("DX", "DY", "DZ", "NXX", "NYY", "NXY")
            ),
            MOMENT=SIMP(
                statut="f", typ="TXM", max="**", into=("DRX", "DRY", "DRZ", "MXX", "MYY", "MXY")
            ),
            POINT=SIMP(statut="f", typ="R", max="**"),
            REPERE=SIMP(
                statut="f",
                typ="TXM",
                defaut="GLOBAL",
                into=("GLOBAL", "LOCAL", "POLAIRE", "UTILISATEUR", "CYLINDRIQUE"),
            ),
            ANGL_NAUT=SIMP(statut="f", typ="R", min=3, max=3),
            ORIGINE=SIMP(statut="f", typ="R", min=3, max=3),
            AXE_Z=SIMP(statut="f", typ="R", min=3, max=3),
            TRAC_NOR=SIMP(statut="f", typ="TXM", into=("OUI",)),
            TRAC_DIR=SIMP(statut="f", typ="TXM", into=("OUI",)),
            DIRECTION=SIMP(statut="f", typ="R", max="**"),
            VECT_Y=SIMP(statut="f", typ="R", max="**"),
            MOYE_NOEUD=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        ),
        FORMAT_C=SIMP(statut="f", typ="TXM", defaut="MODULE", into=("MODULE", "REEL", "IMAG")),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
