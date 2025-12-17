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


def crea_resu_prod(TYPE_RESU, **args):
    if args.get("__all__"):
        return (
            evol_elas,
            evol_noli,
            evol_ther,
            mult_elas,
            mode_meca,
            mode_meca_c,
            dyna_trans,
            dyna_harmo,
            fourier_elas,
            fourier_ther,
            evol_varc,
            evol_char,
        )

    if TYPE_RESU == "EVOL_ELAS":
        return evol_elas
    if TYPE_RESU == "EVOL_NOLI":
        return evol_noli
    if TYPE_RESU == "EVOL_THER":
        return evol_ther
    if TYPE_RESU == "MULT_ELAS":
        return mult_elas
    if TYPE_RESU == "MODE_MECA":
        return mode_meca
    if TYPE_RESU == "MODE_MECA_C":
        return mode_meca_c
    if TYPE_RESU == "DYNA_TRANS":
        return dyna_trans
    if TYPE_RESU == "DYNA_HARMO":
        return dyna_harmo
    if TYPE_RESU == "FOURIER_ELAS":
        return fourier_elas
    if TYPE_RESU == "FOURIER_THER":
        return fourier_ther
    if TYPE_RESU == "EVOL_VARC":
        return evol_varc
    if TYPE_RESU == "EVOL_CHAR":
        return evol_char
    raise AsException("type de concept resultat non prevu")


CREA_RESU = OPER(
    nom="CREA_RESU",
    op=124,
    sd_prod=crea_resu_prod,
    reentrant="f:RESULTAT|RESU_FINAL",
    fr=tr("Creer ou enrichir une structure de donnees resultat a partir de champs aux noeuds"),
    reuse=SIMP(statut="c", typ=CO),
    OPERATION=SIMP(
        statut="o",
        typ="TXM",
        into=(
            "AFFE",
            "ASSE",
            "PERM_CHAM",
            "PROL_RTZ",
            "PREP_VARC",
            "KUCV",
            "CONV_CHAR",
            "CONV_RESU",
        ),
        fr=tr("choix de la fonction a activer"),
    ),
    TYPE_RESU=SIMP(
        statut="o",
        typ="TXM",
        into=(
            # pour bloc AFFE
            "MODE_MECA",
            "MODE_MECA_C",
            "MULT_ELAS",
            "EVOL_ELAS",
            "EVOL_NOLI",
            "DYNA_HARMO",
            "DYNA_TRANS",
            "FOURIER_ELAS",
            "FOURIER_THER",
            "EVOL_THER",
            "EVOL_VARC",
            "EVOL_CHAR"
            # pour bloc ASSE
            # "EVOL_THER "
            # pour bloc PERM_CHAM
            # "EVOL_NOLI"
            # pour bloc PROL_RTZ
            # "EVOL_THER"
            # pour bloc PREP_VARC
            # "EVOL_THER"
        ),
    ),
    b_affe_mult_elas=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'MULT_ELAS')""",
        RESULTAT=SIMP(statut="f", typ=mult_elas),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            NOM_CAS=SIMP(statut="f", typ="TXM"),
            CHARGE=SIMP(statut="f", typ=(char_meca), max="**"),
        ),
    ),  # fin bloc b_affe_mult_elas
    b_affe_evol_dyn=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and is_in('TYPE_RESU', ('EVOL_ELAS', 'EVOL_NOLI', 'EVOL_THER', 'EVOL_VARC', 'EVOL_CHAR', 'DYNA_TRANS'))""",
        RESULTAT=SIMP(
            statut="f", typ=(evol_elas, evol_noli, evol_ther, evol_varc, evol_char, dyna_trans)
        ),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            regles=(UN_PARMI("INST", "LIST_INST"),),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            NUME_INIT=SIMP(statut="f", typ="I", val_min=1),
            NUME_FIN=SIMP(statut="f", typ="I", val_min=1),
            PRECISION=SIMP(statut="f", typ="R", defaut=0.0),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        ),
    ),  # fin bloc b_affe_evol_dyn
    b_affe_fourier_elas=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'FOURIER_ELAS')""",
        RESULTAT=SIMP(statut="f", typ=fourier_elas),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            NUME_MODE=SIMP(statut="f", typ="I"),
            TYPE_MODE=SIMP(statut="f", typ="TXM", defaut="SYME", into=("SYME", "ANTI", "TOUS")),
            CHARGE=SIMP(statut="f", typ=(char_meca), max="**"),
        ),
    ),  # fin bloc b_affe_fourier_elas
    b_affe_fourier_ther=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'FOURIER_THER')""",
        RESULTAT=SIMP(statut="f", typ=fourier_ther),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            NUME_MODE=SIMP(statut="f", typ="I"),
            TYPE_MODE=SIMP(statut="f", typ="TXM", defaut="SYME", into=("SYME", "ANTI", "TOUS")),
        ),
    ),  # fin bloc b_affe_fourier_ther
    # Creation par affectation de champs :
    # -------------------------------------
    b_evol_char=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'EVOL_CHAR')""",
        NOM_CHAM=SIMP(
            statut="o",
            typ="TXM",
            validators=NoRepeat(),
            into=(
                "PRES",
                "FORC_NODA",
                "FSUR_2D",
                "FSUR_3D",
                "FVOL_2D",
                "FVOL_3D",
                "VITE_VENT",
                "T_EXT",
                "COEF_H",
                "FLUN",
            ),
        ),
    ),  # fin bloc b_evol_char
    b_cham_no=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and not equal_to("TYPE_RESU", 'EVOL_CHAR')""",
        NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
    ),  # fin bloc b_cham_no
    b_mode_meca=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and is_in('TYPE_RESU', ('MODE_MECA', 'MODE_MECA_C', 'DYNA_HARMO', 'DYNA_TRANS'))""",
        MATR_RIGI=SIMP(statut="f", typ=matr_asse_depl_r),
        MATR_MASS=SIMP(statut="f", typ=matr_asse_depl_r),
    ),  # fin bloc b_mode_meca
    b_evol_elas=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'EVOL_ELAS')""",
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
    ),  # fin bloc b_evol_elas
    b_evol_ther=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'EVOL_THER')""",
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_ther, char_cine_ther)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
    ),  # fin bloc b_evol_ther
    b_evol_noli=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'EVOL_NOLI')""",
        COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
        VERI_VARI=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TYPE_CHARGE=SIMP(
                statut="f",
                typ="TXM",
                defaut="FIXE_CSTE",
                into=("FIXE_CSTE", "FIXE_PILO", "SUIV", "DIDI"),
            ),
            DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MULT_APPUI=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            DIRECTION=SIMP(statut="f", typ="R", max="**"),
            GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        ),
    ),  # fin bloc b_evol_noli
    b_affe_mode_meca=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'MODE_MECA')""",
        RESULTAT=SIMP(statut="f", typ=mode_meca),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            NUME_MODE=SIMP(statut="o", typ="I"),
            FREQ=SIMP(statut="f", typ="R"),
            AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z")),
        ),
    ),  # fin bloc b_affe_mode_meca
    b_affe_mode_meca_c=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'MODE_MECA_C')""",
        RESULTAT=SIMP(statut="f", typ=mode_meca_c),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            NUME_MODE=SIMP(statut="o", typ="I"),
            FREQ=SIMP(statut="f", typ="R"),
            AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z")),
            AMOR_REDUIT=SIMP(statut="f", typ="R"),
        ),
    ),  # fin bloc b_affe_mode_meca_c
    b_affe_dyna_harmo=BLOC(
        condition="""equal_to("OPERATION", 'AFFE') and equal_to("TYPE_RESU", 'DYNA_HARMO')""",
        RESULTAT=SIMP(statut="f", typ=dyna_harmo),
        AFFE=FACT(
            statut="o",
            max="**",
            CHAM_GD=SIMP(statut="o", typ=(cham_gd_sdaster)),
            MODELE=SIMP(statut="f", typ=modele_sdaster),
            CHAM_MATER=SIMP(statut="f", typ=cham_mater),
            CARA_ELEM=SIMP(statut="f", typ=cara_elem),
            regles=(UN_PARMI("FREQ", "LIST_FREQ"),),
            FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            PRECISION=SIMP(statut="f", typ="R", defaut=0.0),
        ),
    ),  # fin b_affe_dyna_harmo
    # Creation par assemblage d'evol_ther :
    # -----------------------------------------
    b_asse=BLOC(
        condition="""equal_to("OPERATION", 'ASSE')""",
        ASSE=FACT(
            statut="o",
            max="**",
            RESULTAT=SIMP(statut="o", typ=evol_ther),
            TRANSLATION=SIMP(statut="f", typ="R", defaut=0.0),
        ),
    ),
    b_perm_cham=BLOC(
        condition="""equal_to("OPERATION", 'PERM_CHAM')""",
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            into=("DEPL", "SIEF_ELGA", "VARI_ELGA", "STRX_ELGA"),
            validators=NoRepeat(),
            max="**",
        ),
        RESU_INIT=SIMP(statut="o", typ=evol_noli),
        INST_INIT=SIMP(statut="f", typ="R"),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        MAILLAGE_INIT=SIMP(statut="o", typ=maillage_sdaster),
        RESU_FINAL=SIMP(statut="o", typ=evol_noli),
        MAILLAGE_FINAL=SIMP(statut="o", typ=maillage_sdaster),
        PERM_CHAM=FACT(
            statut="o",
            max="**",
            GROUP_MA_FINAL=SIMP(statut="o", typ=grma),
            GROUP_MA_INIT=SIMP(statut="o", typ=grma),
            TRAN=SIMP(statut="o", typ="R", min=3, max=3),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        ),
    ),
    b_prol_rtz=BLOC(
        condition="""equal_to("OPERATION", 'PROL_RTZ')""",
        PROL_RTZ=FACT(
            statut="o",
            regles=(EXCLUS("INST", "LIST_INST"),),
            MAILLAGE_FINAL=SIMP(statut="o", typ=maillage_sdaster),
            TABLE=SIMP(statut="o", typ=table_sdaster, fr=tr("Table issue de post_releve_t")),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            b_acce_reel=BLOC(
                condition="""(exists("INST"))or(exists("LIST_INST"))""",
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                b_prec_rela=BLOC(
                    condition="""(equal_to("CRITERE", 'RELATIF'))""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ),
                b_prec_abso=BLOC(
                    condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                    PRECISION=SIMP(statut="o", typ="R"),
                ),
            ),
            PROL_DROITE=SIMP(
                statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
            ),
            PROL_GAUCHE=SIMP(
                statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
            ),
            REPERE=SIMP(statut="o", typ="TXM", into=("CYLINDRIQUE",)),
            ORIGINE=SIMP(statut="o", typ="R", min=3, max=3),
            AXE_Z=SIMP(statut="o", typ="R", min=3, max=3),
        ),
    ),
    b_prep_varc=BLOC(
        condition="""equal_to("OPERATION", 'PREP_VARC')""",
        PREP_VARC=FACT(
            statut="o",
            max=1,
            # a) CHAM_GD    :   calculer la température dans les couches des
            #                   coques multicouche à partir d'un champ de fonctions
            #                   du temps, de l'espace : ( [EPAIS, INST )
            # b) EVOL_THER  :   calculer la température dans les couches des
            #                   coques multicouche à partir d'un EVOL_THER "coque"
            #                   contenant TEMP_MIL/TEMP_INF/TEMP_SUP
            regles=(UN_PARMI("CHAM_GD", "EVOL_THER"),),
            # carte de fonctions du temps et de l'épaisseur
            CHAM_GD=SIMP(statut="f", typ=(cham_gd_sdaster)),
            # evol_ther de type "coque" (TEMP_MIL/TEMP_INF/TEMP_SUP)
            EVOL_THER=SIMP(statut="f", typ=(evol_ther)),
            # modèle mécanique contenant les coques multicouche
            MODELE=SIMP(statut="o", typ=modele_sdaster),
            # CARA_ELEM pour connaitre EPAIS et COQU_NCOU
            CARA_ELEM=SIMP(statut="o", typ=cara_elem),
            #
            b_evol_ther=BLOC(
                condition="""exists('EVOL_THER')""",
                regles=(EXCLUS("LIST_INST", "INST"), EXCLUS("TOUT", "GROUP_MA", "MAILLE")),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
                #
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                b_prec=BLOC(
                    condition="""(exists("INST")) or (exists("LIST_INST"))""",
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
            b_cham_gd=BLOC(
                condition="""exists('CHAM_GD')""",
                regles=(UN_PARMI("INST", "LIST_INST"),),
                LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
                INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            ),
        ),
    ),
    b_prod_evol_char=BLOC(
        condition="""equal_to("OPERATION", 'KUCV') and is_in('TYPE_RESU', ('EVOL_CHAR', 'DYNA_TRANS'))""",
        KUCV=FACT(
            statut="o",
            max=1,
            RESU_INIT=SIMP(statut="o", typ=(dyna_trans, evol_noli)),
            regles=(UN_PARMI("INST", "LIST_INST"),),
            MATR_RIGI=SIMP(statut="f", typ=matr_asse_depl_r),
            MATR_AMOR=SIMP(statut="o", typ=matr_asse_depl_r),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        ),
    ),  # fin bloc b_prod_evol_char
    b_comb_evol_char=BLOC(
        condition="""equal_to("OPERATION", 'CONV_RESU') and is_in('TYPE_RESU', ('EVOL_CHAR', 'DYNA_TRANS'))""",
        CONV_RESU=FACT(
            statut="o",
            max=1,
            RESU_INIT=SIMP(statut="o", typ=(dyna_trans, evol_char, evol_noli)),
            NOM_CHAM_INIT=SIMP(
                statut="f", typ="TXM", into=("DEPL", "ACCE", "FORC_NODA", "REAC_NODA")
            ),
            DDL_EXCLUS=SIMP(statut="f", typ="TXM", into=("DX", "DY", "DZ", "DRX", "DRY", "DRZ")),
            regles=(
                UN_PARMI("MATR_RIGI", "NUME_DDL"),
                UN_PARMI("INST", "LIST_INST"),
                PRESENT_ABSENT("GROUP_NO_INTERF", "FONC_DX"),
            ),
            MATR_RIGI=SIMP(statut="f", typ=matr_asse_depl_r),
            NUME_DDL=SIMP(statut="f", typ=nume_ddl_sdaster),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            COEF=SIMP(statut="f", typ="R", defaut=1.0),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            GROUP_NO_INTERF=SIMP(statut="f", typ=grno, fr=tr("groupe des noeud des appuis")),
            b_group_no=BLOC(
                condition="""(exists("GROUP_NO_INTERF"))""",
                DIRECTION=SIMP(
                    statut="o", typ="R", min=3, max=3, fr=tr("direction de propagation")
                ),
                VITE_ONDE=SIMP(
                    statut="o",
                    typ="R",
                    val_min=0.0,
                    fr=tr("vitesse de propagation dans la direction"),
                ),
                COOR_REFE=SIMP(
                    statut="o", typ="R", min=3, max=3, fr=tr("coord de reference pour les phases")
                ),
            ),
            FONC_DX=SIMP(statut="f", typ=(nappe_sdaster, formule)),
            b_fonc_dx=BLOC(
                condition="""(exists("FONC_DX"))""",
                FONC_DY=SIMP(statut="f", typ=(nappe_sdaster, formule)),
                FONC_DZ=SIMP(statut="f", typ=(nappe_sdaster, formule)),
                FONC_DRX=SIMP(statut="f", typ=(nappe_sdaster, formule)),
                FONC_DRY=SIMP(statut="f", typ=(nappe_sdaster, formule)),
                FONC_DRZ=SIMP(statut="f", typ=(nappe_sdaster, formule)),
            ),
        ),
    ),  # fin bloc b_comb_evol_char
    b_char_evol_char=BLOC(
        condition="""equal_to("OPERATION", 'CONV_CHAR') and is_in('TYPE_RESU', ('EVOL_CHAR', 'DYNA_TRANS'))""",
        CONV_CHAR=FACT(
            statut="o",
            max=1,
            CHARGE=SIMP(statut="o", typ=(char_meca,), max="**"),
            MATR_RIGI=SIMP(statut="o", typ=matr_asse_depl_r),
            regles=(UN_PARMI("INST", "LIST_INST"),),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        ),
    ),  # fin bloc b_char_evol_char
)
