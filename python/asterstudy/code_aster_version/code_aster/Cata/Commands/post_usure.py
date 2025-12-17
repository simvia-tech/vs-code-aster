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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_USURE = OPER(
    nom="POST_USURE",
    op=153,
    sd_prod=table_sdaster,
    reentrant="f:TABL_USURE",
    fr=tr("Calcul des volumes d'usure et des profondeurs d'usure d'après la puissance d'usure"),
    regles=(
        UN_PARMI("TUBE_NEUF", "RESU_GENE", "PUIS_USURE"),
        UN_PARMI("TUBE_NEUF", "LOI_USURE"),
        PRESENT_ABSENT("TUBE_NEUF", "ETAT_INIT", "INST_FIN"),
        PRESENT_ABSENT("TUBE_NEUF", "RAYON_MOBILE", "RAYON_OBST", "LARGEUR_OBST", "CONTACT"),
        PRESENT_ABSENT("TUBE_NEUF", "ANGL_INCLI", "ANGL_ISTHME", "ANGL_IMPACT"),
        PRESENT_PRESENT("ANGL_INCLI", "CONTACT"),
        PRESENT_PRESENT("ANGL_ISTHME", "CONTACT"),
        PRESENT_PRESENT("ANGL_IMPACT", "CONTACT"),
    ),
    reuse=SIMP(statut="c", typ=CO),
    TUBE_NEUF=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ETAT_INIT=FACT(
        statut="f",
        TABL_USURE=SIMP(statut="f", typ=table_sdaster),
        INST_INIT=SIMP(statut="f", typ="R"),
    ),
    RESU_GENE=SIMP(statut="f", typ=tran_gene),
    INST_FIN=SIMP(statut="f", typ="R"),
    PUIS_USURE=SIMP(statut="f", typ="R"),
    LOI_USURE=SIMP(statut="f", typ="TXM", into=("ARCHARD", "KWU_EPRI", "EDF_MZ")),
    b_resu_gene=BLOC(
        condition="""exists("RESU_GENE")""",
        regles=UN_PARMI("NOEUD", "GROUP_NO"),
        NOEUD=SIMP(statut="c", typ=no),
        GROUP_NO=SIMP(statut="f", typ=grno),
    ),
    b_archard=BLOC(
        condition="""equal_to("LOI_USURE", 'ARCHARD')""",
        regles=(
            UN_PARMI("MOBILE", "MATER_USURE", "SECTEUR"),
            EXCLUS("MATER_USURE", "OBSTACLE"),
            EXCLUS("MOBILE", "USURE_OBST"),
        ),
        MOBILE=FACT(statut="f", COEF_USURE=SIMP(statut="o", typ="R")),
        OBSTACLE=FACT(statut="f", COEF_USURE=SIMP(statut="o", typ="R")),
        SECTEUR=FACT(
            statut="f",
            max="**",
            COEF_USUR_MOBILE=SIMP(statut="f", typ="R"),
            COEF_USUR_OBST=SIMP(statut="f", typ="R"),
            ANGL_INIT=SIMP(statut="f", typ="R"),
            ANGL_FIN=SIMP(statut="f", typ="R"),
        ),
        MATER_USURE=SIMP(statut="f", typ="TXM"),
        USURE_OBST=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),
    b_kwu_epri=BLOC(
        condition="""equal_to("LOI_USURE", 'KWU_EPRI')""",
        regles=(
            UN_PARMI("MOBILE", "MATER_USURE"),
            EXCLUS("MATER_USURE", "OBSTACLE"),
            EXCLUS("MOBILE", "USURE_OBST"),
        ),
        MOBILE=FACT(
            statut="f",
            COEF_FNOR=SIMP(statut="f", typ="R"),
            COEF_VTAN=SIMP(statut="f", typ="R"),
            COEF_USURE=SIMP(statut="f", typ="R"),
            COEF_K=SIMP(statut="f", typ="R", defaut=5.0e0),
            COEF_C=SIMP(statut="f", typ="R", defaut=10.0e0),
        ),
        OBSTACLE=FACT(
            statut="f",
            COEF_FNOR=SIMP(statut="f", typ="R"),
            COEF_VTAN=SIMP(statut="f", typ="R"),
            COEF_USURE=SIMP(statut="o", typ="R"),
            COEF_K=SIMP(statut="f", typ="R", defaut=5.0e0),
            COEF_C=SIMP(statut="f", typ="R", defaut=10.0e0),
        ),
        MATER_USURE=SIMP(statut="f", typ="TXM"),
        USURE_OBST=SIMP(statut="f", typ="TXM", into=("OUI",)),
        FNOR_MAXI=SIMP(statut="f", typ="R"),
        VTAN_MAXI=SIMP(statut="f", typ="R"),
    ),
    b_edf_mz=BLOC(
        condition="""equal_to("LOI_USURE", 'EDF_MZ')""",
        regles=(
            UN_PARMI("MOBILE", "MATER_USURE"),
            EXCLUS("MATER_USURE", "OBSTACLE"),
            EXCLUS("MOBILE", "USURE_OBST"),
        ),
        MOBILE=FACT(
            statut="f",
            COEF_USURE=SIMP(statut="f", typ="R", defaut=1.0e-13),
            COEF_B=SIMP(statut="f", typ="R", defaut=1.2e0),
            COEF_N=SIMP(statut="f", typ="R", defaut=2.44e-8),
            COEF_S=SIMP(statut="f", typ="R", defaut=1.14e-16),
        ),
        OBSTACLE=FACT(
            statut="f",
            COEF_USURE=SIMP(statut="f", typ="R", defaut=1.0e-13),
            COEF_B=SIMP(statut="f", typ="R", defaut=1.2e0),
            COEF_N=SIMP(statut="f", typ="R", defaut=2.44e-8),
            COEF_S=SIMP(statut="f", typ="R", defaut=1.14e-16),
        ),
        MATER_USURE=SIMP(statut="f", typ="TXM"),
        USURE_OBST=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),
    CONTACT=SIMP(
        statut="f",
        typ="TXM",
        into=(
            "TUBE_BAV",
            "TUBE_ALESAGE",
            "TUBE_4_ENCO",
            "GRAPPE_ALESAGE",
            "TUBE_3_ENCO",
            "TUBE_TUBE",
            "GRAPPE_1_ENCO",
            "GRAPPE_2_ENCO",
        ),
    ),
    RAYON_MOBILE=SIMP(statut="f", typ="R"),
    RAYON_OBST=SIMP(statut="f", typ="R"),
    LARGEUR_OBST=SIMP(statut="f", typ="R"),
    ANGL_INCLI=SIMP(statut="f", typ="R"),
    ANGL_ISTHME=SIMP(statut="f", typ="R"),
    ANGL_IMPACT=SIMP(statut="f", typ="R"),
    b_not_tube_neuf=BLOC(
        condition="""not exists("TUBE_NEUF")""",
        regles=(UN_PARMI("INST", "LIST_INST"),),
        INST_INIT=SIMP(statut="f", typ="R", defaut=-1.0e0),
        NB_BLOC=SIMP(statut="f", typ="I", defaut=1),
        COEF_INST=SIMP(statut="f", typ="R", defaut=1.0e0),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    ),
    b_tube_neuf=BLOC(
        condition="""exists("TUBE_NEUF")""",
        INST=SIMP(statut="f", typ="R", validators=NoRepeat()),
        TABL_USURE=SIMP(statut="o", typ=table_sdaster),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
