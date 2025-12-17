# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2024 - EDF R&D - www.code-aster.org
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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def defi_group_prod(MAILLAGE, GRILLE, **args):
    if args.get("__all__"):
        return (maillage_sdaster, squelette, grille_sdaster, maillage_p)

    if MAILLAGE is not None:
        if AsType(MAILLAGE) == maillage_sdaster:
            return maillage_sdaster
        if AsType(MAILLAGE) == maillage_p:
            return maillage_p
        if AsType(MAILLAGE) == squelette:
            return squelette
    if GRILLE is not None:
        return grille_sdaster
    raise AsException("type de concept resultat non prevu")


DEFI_GROUP = OPER(
    nom="DEFI_GROUP",
    op=104,
    sd_prod=defi_group_prod,
    fr=tr("Définition de nouveaux groupes de noeuds et/ou de mailles dans un concept maillage"),
    reentrant="o:MAILLAGE|GRILLE",
    regles=(
        AU_MOINS_UN("CREA_GROUP_MA", "CREA_GROUP_NO", "DETR_GROUP_NO", "DETR_GROUP_MA"),
        UN_PARMI("MAILLAGE", "GRILLE"),
    ),
    reuse=SIMP(statut="c", typ=CO),
    MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
    GRILLE=SIMP(statut="f", typ=(grille_sdaster)),
    DETR_GROUP_MA=FACT(
        statut="f", max="**", NOM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**")
    ),
    DETR_GROUP_NO=FACT(
        statut="f", max="**", NOM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**")
    ),
    CREA_GROUP_MA=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE", "INTERSEC", "UNION", "DIFFE", "OPTION"),),
        NOM=SIMP(statut="o", typ="TXM"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        INTERSEC=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        UNION=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        DIFFE=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TYPE_MAILLE=SIMP(
            statut="f",
            typ="TXM",
            defaut="TOUT",
            into=(
                "TOUT",
                "1D",
                "2D",
                "3D",
                "POI1",
                "SEG2",
                "SEG3",
                "SEG4",
                "TRIA3",
                "TRIA6",
                "TRIA7",
                "QUAD4",
                "QUAD8",
                "QUAD9",
                "TETRA4",
                "TETRA10",
                "PENTA6",
                "PENTA15",
                "PENTA18",
                "HEXA8",
                "HEXA20",
                "HEXA27",
                "PYRAM5",
                "PYRAM13",
            ),
            max=1,
        ),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            into=("FACE_NORMALE", "SPHERE", "CYLINDRE", "BANDE", "APPUI", "FISS_XFEM"),
        ),
        b_group_ma=BLOC(
            condition="""exists("GROUP_MA")""",
            regles=(EXCLUS("POSITION", "NUME_INIT"),),
            NUME_INIT=SIMP(statut="f", typ="I"),
            POSITION=SIMP(statut="f", typ="TXM", into=("INIT", "FIN", "MILIEU")),
            b_nume_init=BLOC(
                condition="""exists("NUME_INIT")""", NUME_FIN=SIMP(statut="f", typ="I")
            ),
        ),
        b_face_normale=BLOC(
            condition="""equal_to("OPTION", 'FACE_NORMALE')""",
            regles=(UN_PARMI("ANGL_NAUT", "VECT_NORMALE"),),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=2),
            VECT_NORMALE=SIMP(statut="f", typ="R", max=3),
            ANGL_PREC=SIMP(statut="f", typ="R", defaut=0.5),
            VERI_SIGNE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        ),
        b_sphere=BLOC(
            condition="""equal_to("OPTION", 'SPHERE')""",
            regles=(UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno),
            RAYON=SIMP(statut="o", typ="R"),
            CRIT_NOEUD=SIMP(
                statut="f",
                typ="TXM",
                defaut="AU_MOINS_UN",
                into=("TOUS", "AU_MOINS_UN", "MAJORITE"),
            ),
        ),
        b_cylindre=BLOC(
            condition="""equal_to("OPTION", 'CYLINDRE')""",
            regles=(
                UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),
                UN_PARMI("ANGL_NAUT", "VECT_NORMALE"),
            ),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno),
            RAYON=SIMP(statut="o", typ="R"),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=2),
            VECT_NORMALE=SIMP(statut="f", typ="R", max=3),
            CRIT_NOEUD=SIMP(
                statut="f",
                typ="TXM",
                defaut="AU_MOINS_UN",
                into=("TOUS", "AU_MOINS_UN", "MAJORITE"),
            ),
        ),
        b_bande=BLOC(
            condition="""equal_to("OPTION", 'BANDE')""",
            regles=(
                UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),
                UN_PARMI("ANGL_NAUT", "VECT_NORMALE"),
            ),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no, max=1),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno, max=1),
            DIST=SIMP(statut="o", typ="R"),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=2),
            VECT_NORMALE=SIMP(statut="f", typ="R", max=3),
            CRIT_NOEUD=SIMP(
                statut="f",
                typ="TXM",
                defaut="AU_MOINS_UN",
                into=("TOUS", "AU_MOINS_UN", "MAJORITE"),
            ),
        ),
        b_appui=BLOC(
            condition="""equal_to("OPTION", 'APPUI')""",
            regles=(UN_PARMI("NOEUD", "GROUP_NO"),),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            TYPE_APPUI=SIMP(
                statut="o", typ="TXM", max=1, into=("AU_MOINS_UN", "TOUT", "SOMMET", "MAJORITE")
            ),
        ),
        b_fiss_xfem=BLOC(
            condition="""equal_to("OPTION", 'FISS_XFEM')""",
            TYPE_GROUP=SIMP(
                statut="f",
                typ="TXM",
                max=1,
                defaut="XFEM",
                into=("HEAVISIDE", "CRACKTIP", "MIXTE", "FISSUREE", "XFEM"),
            ),
            FISSURE=SIMP(statut="o", typ=fiss_xfem, min=1, max="**"),
        ),
    ),
    CREA_GROUP_NO=FACT(
        statut="f",
        max="**",
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            into=(
                "ENV_SPHERE",
                "ENV_CYLINDRE",
                "PLAN",
                "SEGM_DROI_ORDO",
                "NOEUD_ORDO",
                "TUNNEL",
                "INCLUSION",
                "FISS_XFEM",
                "INTERVALLE_VALE",
                "RELA_CINE_BP",
            ),
        ),
        b_option=BLOC(
            condition="""not exists("OPTION")""",
            regles=(
                UN_PARMI(
                    "TOUT_GROUP_MA", "GROUP_MA", "GROUP_NO", "NOEUD", "INTERSEC", "UNION", "DIFFE"
                ),
            ),
            TOUT_GROUP_MA=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
            INTERSEC=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            UNION=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            DIFFE=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            b_nom_group_ma=BLOC(
                condition="""exists("GROUP_MA")""",
                NOM=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                CRIT_NOEUD=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="TOUS",
                    into=("TOUS", "SOMMET", "MILIEU", "CENTRE"),
                ),
            ),
            b_group_no=BLOC(
                condition="""exists("GROUP_NO")""",
                regles=(EXCLUS("POSITION", "NUME_INIT"),),
                NUME_INIT=SIMP(statut="f", typ="I"),
                POSITION=SIMP(statut="f", typ="TXM", into=("INIT", "FIN", "MILIEU")),
                b_nume_init=BLOC(
                    condition="""exists("NUME_INIT")""", NUME_FIN=SIMP(statut="f", typ="I")
                ),
            ),
            b_nom=BLOC(
                condition="""not exists("GROUP_MA") and not exists("TOUT_GROUP_MA")""",
                NOM=SIMP(statut="o", typ="TXM"),
            ),
        ),
        b_env_sphere=BLOC(
            condition="""equal_to("OPTION", 'ENV_SPHERE')""",
            regles=(UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),),
            NOM=SIMP(statut="o", typ="TXM"),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no, max=1),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno, max=1),
            RAYON=SIMP(statut="o", typ="R"),
            PRECISION=SIMP(statut="o", typ="R"),
        ),
        b_env_cylindre=BLOC(
            condition="""equal_to("OPTION", 'ENV_CYLINDRE')""",
            regles=(
                UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),
                UN_PARMI("ANGL_NAUT", "VECT_NORMALE"),
            ),
            NOM=SIMP(statut="o", typ="TXM"),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no, max=1),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno, max=1),
            RAYON=SIMP(statut="o", typ="R"),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=3),
            VECT_NORMALE=SIMP(statut="f", typ="R", max=3),
            PRECISION=SIMP(statut="o", typ="R"),
        ),
        b_env_plan=BLOC(
            condition="""equal_to("OPTION", 'PLAN')""",
            regles=(
                UN_PARMI("POINT", "NOEUD_CENTRE", "GROUP_NO_CENTRE"),
                UN_PARMI("ANGL_NAUT", "VECT_NORMALE"),
            ),
            NOM=SIMP(statut="o", typ="TXM"),
            POINT=SIMP(statut="f", typ="R", max=3),
            NOEUD_CENTRE=SIMP(statut="c", typ=no, max=1),
            GROUP_NO_CENTRE=SIMP(statut="f", typ=grno, max=1),
            ANGL_NAUT=SIMP(statut="f", typ="R", max=3),
            VECT_NORMALE=SIMP(statut="f", typ="R", max=3),
            PRECISION=SIMP(statut="o", typ="R"),
        ),
        b_segm_droi_ordo=BLOC(
            condition="""equal_to("OPTION", 'SEGM_DROI_ORDO')""",
            NOM=SIMP(statut="o", typ="TXM"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            GROUP_NO_ORIG=SIMP(statut="o", typ=grno),
            GROUP_NO_EXTR=SIMP(statut="o", typ=grno),
            PRECISION=SIMP(statut="o", typ="R"),
            CRITERE=SIMP(statut="o", typ="TXM", into=("ABSOLU", "RELATIF")),
        ),
        b_noeud_ordo=BLOC(
            condition="""equal_to("OPTION", 'NOEUD_ORDO')""",
            NOM=SIMP(statut="o", typ="TXM"),
            GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
            # si le groupe de mailles forme une ligne ouverte, on peut choisir le sens de parcours en choissant l'origine.
            # sinon, le code choisit une origine parmi les deux.
            # si le groupe de mailles forme une ligne fermée, on peut choisir l'origine et l'extrémité (= origine).
            GROUP_NO_ORIG=SIMP(statut="f", typ=grno),
            GROUP_NO_EXTR=SIMP(statut="f", typ=grno),
            # si le groupe de mailles forme une ligne fermée, on peut choisir le sens de parcours :
            VECT_ORIE=SIMP(statut="f", typ="R", max=3),
            # si la ligne est fermee et que l'on ne donne pas xxx_ORIG, on peut demander au code de choisir
            # un noeud origine quelconque.
            ORIGINE=SIMP(statut="f", typ="TXM", into=("SANS",)),
        ),
        b_tunnel=BLOC(
            condition="""equal_to("OPTION", 'TUNNEL')""",
            regles=(AU_MOINS_UN("TOUT", "GROUP_MA", "MAILLE"),),
            NOM=SIMP(statut="o", typ="TXM"),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_MA_AXE=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_NO_ORIG=SIMP(statut="f", typ=grno),
            RAYON=SIMP(statut="o", typ="R"),
            LONGUEUR=SIMP(statut="f", typ="R"),
        ),
        b_inclusion=BLOC(
            condition="""equal_to("OPTION", 'INCLUSION')""",
            fr=tr(
                "crée le groupe des noeuds des mailles de GROUP_MA inclus géométriquement"
                "dans les mailles de GROUP_MA_INCL"
            ),
            NOM=SIMP(statut="o", typ="TXM"),
            CAS_FIGURE=SIMP(statut="o", typ="TXM", into=("2D", "3D", "2.5D")),
            DISTANCE_MAX=SIMP(statut="f", typ="R"),
            GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
            GROUP_MA_INCL=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
            MAILLAGE_INCL=SIMP(statut="f", typ=maillage_sdaster),
        ),
        b_fiss_xfem=BLOC(
            condition="""equal_to("OPTION", 'FISS_XFEM')""",
            NOM=SIMP(statut="o", typ="TXM"),
            TYPE_GROUP=SIMP(
                statut="o",
                typ="TXM",
                max=1,
                into=("HEAVISIDE", "CRACKTIP", "MIXTE", "XFEM", "ZONE_MAJ", "TORE"),
            ),
            FISSURE=SIMP(statut="o", typ=fiss_xfem, min=1, max="**"),
            b_rayon=BLOC(
                condition="""equal_to("TYPE_GROUP", 'TORE')""",
                RAYON_TORE=SIMP(statut="o", typ="R", max=1, val_min=0.0),
            ),
        ),
        b_intervalle_vale=BLOC(
            condition="""equal_to("OPTION", 'INTERVALLE_VALE')""",
            NOM=SIMP(statut="o", typ="TXM"),
            CHAM_GD=SIMP(statut="o", typ=cham_no_sdaster),
            NOM_CMP=SIMP(statut="o", typ="TXM", max=1),
            VALE=SIMP(statut="o", typ="R", min=2, max=2),
        ),
        b_rela_cine_bp=BLOC(
            condition="""equal_to("OPTION", 'RELA_CINE_BP')""",
            CABLE_BP=SIMP(statut="o", typ=cabl_precont),
            PREF_GRNO=SIMP(statut="f", typ="TXM", defaut="RCBP"),
        ),
    ),
    ALARME=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
