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

IMPR_RESU = PROC(
    nom="IMPR_RESU",
    op=39,
    fr=tr("Imprimer un maillage et/ou les résultats d'un calcul (différents formats)"),
    FORMAT=SIMP(
        statut="f", typ="TXM", defaut="MED", into=("RESULTAT", "IDEAS", "ASTER", "MED", "GMSH")
    ),
    PROC0=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
    b_modele=BLOC(
        condition="""not equal_to("FORMAT", 'MED')""",
        fr=tr("Modèle"),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
    ),
    b_format_resultat=BLOC(
        condition="""equal_to("FORMAT", 'RESULTAT')""",
        fr=tr("unité logique d'impression au format RESULTAT"),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="out"),
    ),
    b_format_ideas=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS')""",
        fr=tr("unité logique d'impression et version IDEAS"),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=30, inout="out"),
        VERSION=SIMP(statut="f", typ="I", defaut=5, into=(4, 5)),
    ),
    b_format_aster=BLOC(
        condition="""equal_to("FORMAT", 'ASTER')""",
        fr=tr("unité logique d'impression au format ASTER"),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=26, inout="out"),
    ),
    b_format_med=BLOC(
        condition="""equal_to("FORMAT", 'MED')""",
        fr=tr("unité logique d'impression au format MED"),
        UNITE=SIMP(statut="f", typ=UnitType("med"), defaut=80, inout="out"),
        # same keyword in IMPR_CONCEPT, keep consistency
        VERSION_MED=SIMP(
            statut="f",
            typ="TXM",
            into=("3.3.1", "4.0.0", "4.1.0"),
            defaut="3.3.1",
            fr=tr("Choix de la version du fichier MED"),
        ),
        FICHIER_UNIQUE=SIMP(
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
            fr=tr("Paramètre permettant d'imprimer les résultats dans un fichier unique"),
        ),
    ),
    b_format_gmsh=BLOC(
        condition="""equal_to("FORMAT", 'GMSH')""",
        fr=tr("unité logique d'impression et version GMSH"),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=37, inout="out"),
        VERSION=SIMP(statut="f", typ="R", defaut=1.2, into=(1.0, 1.2)),
    ),
    b_fmt_med=BLOC(
        condition="""equal_to("FORMAT", 'MED')""",
        RESU=FACT(
            statut="o",
            max="**",
            regles=(
                AU_MOINS_UN("CHAM_GD", "RESULTAT", "MAILLAGE"),
                EXCLUS("CHAM_GD", "RESULTAT"),
                EXCLUS("TOUT_CMP", "NOM_CMP"),
            ),
            MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            b_visu_sp=BLOC(
                condition="""(not exists("CARA_ELEM"))""",
                VISU_SP=SIMP(statut="f", typ="TXM", into=("NON",)),
            ),
            CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
            RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
            INFO_MAILLAGE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            b_partie=BLOC(
                condition="""(is_type("RESULTAT") in (dyna_harmo, acou_harmo) or is_type("CHAM_GD") != carte_sdaster)""",
                PARTIE=SIMP(statut="f", typ="TXM", into=("REEL", "IMAG", "MODULE", "PHASE")),
            ),
            IMPR_NOM_VARI=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            b_extrac=BLOC(
                condition="""exists("RESULTAT")""",
                fr=tr("extraction d un champ de grandeur"),
                regles=(
                    EXCLUS("TOUT_CHAM", "NOM_CHAM"),
                    EXCLUS(
                        "TOUT_ORDRE",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "LIST_INST",
                        "LIST_FREQ",
                        "LIST_ORDRE",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NOM_CHAM=SIMP(
                    statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                ANGLE=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                b_acce_reel=BLOC(
                    condition="""(exists("ANGLE"))or(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            ###
            b_param=BLOC(
                condition="""(exists("RESULTAT"))""",
                NOM_PARA=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
            ),
            ###
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            ###
            b_med=BLOC(
                condition="""(exists("CHAM_GD") or exists("RESULTAT"))""",
                fr=tr("renommage du champ"),
                regles=(EXCLUS("NOM_CHAM_MED", "NOM_RESU_MED"),),
                NOM_CHAM_MED=SIMP(
                    statut="f", typ="TXM", validators=AndVal((LongStr(1, 64), NoRepeat())), max="**"
                ),
                NOM_RESU_MED=SIMP(statut="f", typ="TXM", validators=LongStr(1, 8)),
            ),
            ###
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        ),  # end fkw_resu
    ),  # end b_fmt_med
    b_fmt_resultat=BLOC(
        condition="""equal_to("FORMAT", 'RESULTAT')""",
        RESU=FACT(
            statut="f",
            max="**",
            regles=(
                AU_MOINS_UN("CHAM_GD", "RESULTAT", "MAILLAGE"),
                EXCLUS("CHAM_GD", "RESULTAT"),
                EXCLUS("TOUT_PARA", "NOM_PARA"),
                EXCLUS("TOUT_CMP", "NOM_CMP"),
            ),
            MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
            RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
            PARTIE=SIMP(statut="f", typ="TXM", into=("REEL", "IMAG", "MODULE", "PHASE")),
            b_extrac=BLOC(
                condition="""exists("RESULTAT")""",
                fr=tr("extraction d un champ de grandeur"),
                regles=(
                    EXCLUS("TOUT_CHAM", "NOM_CHAM"),
                    EXCLUS(
                        "TOUT_ORDRE",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "LIST_INST",
                        "LIST_FREQ",
                        "LIST_ORDRE",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NOM_CHAM=SIMP(
                    statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                ANGLE=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                b_acce_reel=BLOC(
                    condition="""(exists("ANGLE"))or(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            TOUT_PARA=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
            NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
            FORM_TABL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON", "EXCEL")),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            b_topologie=BLOC(
                condition="""(exists("CHAM_GD") or exists("RESULTAT"))""",
                fr=tr("sélection des entités topologiques"),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
                MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            ),
            VALE_MAX=SIMP(statut="f", typ="TXM", into=("OUI",)),
            VALE_MIN=SIMP(statut="f", typ="TXM", into=("OUI",)),
            BORNE_SUP=SIMP(statut="f", typ="R"),
            BORNE_INF=SIMP(statut="f", typ="R"),
            IMPR_COOR=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            FORMAT_R=SIMP(statut="f", typ="TXM", defaut="1PE21.14"),
            SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        ),  # end fkw_resu
    ),  # end b_fmt_resultat
    b_fmt_gmsh=BLOC(
        condition="""equal_to("FORMAT", 'GMSH')""",
        RESU=FACT(
            statut="f",
            max="**",
            regles=(AU_MOINS_UN("CHAM_GD", "RESULTAT", "MAILLAGE"), EXCLUS("CHAM_GD", "RESULTAT")),
            MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
            RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
            PARTIE=SIMP(statut="f", typ="TXM", into=("REEL", "IMAG")),
            b_extrac=BLOC(
                condition="""exists("RESULTAT")""",
                fr=tr("extraction d un champ de grandeur"),
                regles=(
                    EXCLUS("TOUT_CHAM", "NOM_CHAM"),
                    EXCLUS(
                        "TOUT_ORDRE",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "LIST_INST",
                        "LIST_FREQ",
                        "LIST_ORDRE",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NOM_CHAM=SIMP(
                    statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                ANGLE=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                b_acce_reel=BLOC(
                    condition="""(exists("ANGLE"))or(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            TYPE_CHAM=SIMP(
                statut="f",
                typ="TXM",
                defaut="SCALAIRE",
                into=("VECT_2D", "VECT_3D", "SCALAIRE", "TENS_2D", "TENS_3D"),
            ),
            b_scal=BLOC(
                condition="""equal_to("TYPE_CHAM", 'SCALAIRE')""",
                NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            ),
            b_vect_2d=BLOC(
                condition="""equal_to("TYPE_CHAM", 'VECT_2D')""",
                NOM_CMP=SIMP(statut="o", typ="TXM", min=2, max=2),
            ),
            b_vect_3d=BLOC(
                condition="""equal_to("TYPE_CHAM", 'VECT_3D')""",
                NOM_CMP=SIMP(statut="o", typ="TXM", min=3, max=3),
            ),
            b_tens_2d=BLOC(
                condition="""equal_to("TYPE_CHAM", 'TENS_2D')""",
                NOM_CMP=SIMP(statut="o", typ="TXM", min=4, max=4),
            ),
            b_tens_3d=BLOC(
                condition="""equal_to("TYPE_CHAM", 'TENS_3D')""",
                NOM_CMP=SIMP(statut="o", typ="TXM", min=6, max=6),
            ),
            SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        ),  # end fkw_resu
    ),  # end b_fmt_gmsh
    b_fmt_ideas=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS')""",
        RESU=FACT(
            statut="f",
            max="**",
            regles=(
                AU_MOINS_UN("CHAM_GD", "RESULTAT", "MAILLAGE"),
                EXCLUS("CHAM_GD", "RESULTAT"),
                EXCLUS("TOUT_CMP", "NOM_CMP"),
            ),
            MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
            RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
            b_extrac=BLOC(
                condition="""exists("RESULTAT")""",
                fr=tr("extraction d un champ de grandeur"),
                regles=(
                    EXCLUS("TOUT_CHAM", "NOM_CHAM"),
                    EXCLUS(
                        "TOUT_ORDRE",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "LIST_INST",
                        "LIST_FREQ",
                        "LIST_ORDRE",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NOM_CHAM=SIMP(
                    statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                ANGLE=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                b_acce_reel=BLOC(
                    condition="""(exists("ANGLE"))or(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            b_topologie=BLOC(
                condition="""(exists("CHAM_GD") or exists("RESULTAT"))""",
                fr=tr("sélection des entités topologiques"),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
                MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            ),
            SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        ),  # end fkw_resu
    ),  # end b_fmt_ideas
    b_fmt_aster=BLOC(
        condition="""equal_to("FORMAT", 'ASTER')""",
        RESU=FACT(
            statut="f",
            max="**",
            regles=(AU_MOINS_UN("CHAM_GD", "RESULTAT", "MAILLAGE"), EXCLUS("CHAM_GD", "RESULTAT")),
            MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, squelette)),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
            RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
            b_extrac=BLOC(
                condition="""exists("RESULTAT")""",
                fr=tr("extraction d un champ de grandeur"),
                regles=(
                    EXCLUS("TOUT_CHAM", "NOM_CHAM"),
                    EXCLUS(
                        "TOUT_ORDRE",
                        "NUME_ORDRE",
                        "INST",
                        "FREQ",
                        "NUME_MODE",
                        "NOEUD_CMP",
                        "LIST_INST",
                        "LIST_FREQ",
                        "LIST_ORDRE",
                        "NOM_CAS",
                        "ANGLE",
                    ),
                ),
                TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NOM_CHAM=SIMP(
                    statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
                ),
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                NOM_CAS=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
                ANGLE=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                b_acce_reel=BLOC(
                    condition="""(exists("ANGLE"))or(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            FORMAT_R=SIMP(statut="f", typ="TXM", defaut="1PE21.14"),
            SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        ),  # end fkw_resu
    ),  # end b_fmt_aster
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    translation={"IMPR_RESU": "Set output results", "UNITE": "Result file location"},
)
