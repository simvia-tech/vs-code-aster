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

# person_in_charge: natacha.bereux at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def modi_repere_prod(RESULTAT, CHAM_GD, **args):
    if args.get("__all__"):
        return (None, resultat_sdaster, cham_gd_sdaster)

    if AsType(RESULTAT) is not None:
        return AsType(RESULTAT)
    if AsType(CHAM_GD) is not None:
        return AsType(CHAM_GD)


MODI_REPERE = OPER(
    nom="MODI_REPERE",
    op=191,
    sd_prod=modi_repere_prod,
    reentrant="f:RESULTAT",
    fr="Calcule les champs dans un nouveau repère.",
    #
    regles=(UN_PARMI("CHAM_GD", "RESULTAT"),),
    reuse=SIMP(statut="c", typ=CO),
    CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
    RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
    #
    #   Traitement de RESULTAT
    b_resultat=BLOC(
        condition="""exists("RESULTAT")""",
        fr="Changement de repère d'un champ extrait d'un résultat",
        regles=(
            EXCLUS(
                "TOUT_ORDRE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "LIST_ORDRE",
                "NUME_MODE",
                "NOEUD_CMP",
                "LIST_INST",
                "LIST_FREQ",
                "NOM_CAS",
            ),
        ),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CAS=SIMP(statut="f", typ="TXM"),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        MODI_CHAM=FACT(
            statut="o",
            max="**",
            TYPE_CHAM=SIMP(
                statut="o",
                typ="TXM",
                into=("VECT_2D", "VECT_3D", "TENS_2D", "TENS_3D", "COQUE_GENE", "1D_GENE"),
            ),
            b_vect=BLOC(
                condition="""(equal_to("TYPE_CHAM", "VECT_2D") or equal_to("TYPE_CHAM", "VECT_3D"))""",
                NOM_CHAM=SIMP(
                    statut="o",
                    typ="TXM",
                    max=1,
                    into=("DEPL", "VITE", "ACCE", "FORC_NODA", "REAC_NODA", "FLUX_NOEU"),
                ),
            ),
            b_1d=BLOC(
                condition="""(equal_to("TYPE_CHAM", "1D_GENE"))""",
                NOM_CHAM=SIMP(
                    statut="o",
                    typ="TXM",
                    max=1,
                    into=("EFGE_ELNO", "EFGE_ELGA", "SIEF_ELNO", "SIEF_ELGA"),
                ),
            ),
            b_cgene=BLOC(
                condition="""(equal_to("TYPE_CHAM", "COQUE_GENE"))""",
                NOM_CHAM=SIMP(
                    statut="o",
                    typ="TXM",
                    max=1,
                    into=(
                        "EFGE_ELNO",
                        "EFGE_ELGA",
                        "SIEF_ELGA",
                        "SIEF_ELNO",
                        "DEGE_ELNO",
                        "DEGE_ELGA",
                    ),
                ),
            ),
            b_tens=BLOC(
                condition="""(equal_to("TYPE_CHAM", "TENS_2D") or equal_to("TYPE_CHAM", "TENS_3D"))""",
                NOM_CHAM=SIMP(statut="o", typ="TXM", into=C_NOM_CHAM_INTO(), max=1),
            ),
        ),
    ),
    #
    REPERE=SIMP(
        statut="f",
        typ="TXM",  # defaut="UTILISATEUR",
        into=(
            "UTILISATEUR",
            "CYLINDRIQUE",
            "COQUE",
            "GLOBAL_UTIL",
            "COQUE_INTR_UTIL",
            "COQUE_UTIL_INTR",
            "COQUE_UTIL_CYL",
        ),
    ),
    b_cyl=BLOC(
        condition="""is_in("REPERE", ('CYLINDRIQUE', 'COQUE_UTIL_CYL'))""",
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE", "GROUP_NO", "NOEUD")),
            ORIGINE=SIMP(statut="f", typ="R", min=2, max=3),
            AXE_Z=SIMP(statut="f", typ="R", min=3, max=3),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),
    b_uti=BLOC(
        condition="""equal_to("REPERE", 'UTILISATEUR')""",
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(
                UN_PARMI("ANGL_NAUT", "VECT_X"),
                ENSEMBLE("VECT_X", "VECT_Y"),
                UN_PARMI("TOUT", "GROUP_MA", "MAILLE", "GROUP_NO", "NOEUD"),
            ),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=3),
            VECT_X=SIMP(statut="f", typ="R", min=3, max=3),
            VECT_Y=SIMP(statut="f", typ="R", min=3, max=3),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),
    b_coq=BLOC(
        condition="""equal_to("REPERE", 'COQUE')""",
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(
                UN_PARMI("ANGL_REP", "VECTEUR"),
                UN_PARMI("TOUT", "GROUP_MA", "MAILLE", "GROUP_NO", "NOEUD"),
            ),
            ANGL_REP=SIMP(statut="f", typ="R", min=2, max=2),
            VECTEUR=SIMP(statut="f", typ="R", min=3, max=3),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),
    b_autre=BLOC(
        condition="""is_in("REPERE", ('GLOBAL_UTIL', 'COQUE_INTR_UTIL', 'COQUE_UTIL_INTR'))""",
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE", "GROUP_NO", "NOEUD")),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),
    #
    #   Traitement de CHAM_GD and not reuse
    #
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
