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


def lire_resu_prod(TYPE_RESU, **args):
    if args.get("__all__"):
        return (
            evol_char,
            evol_ther,
            evol_elas,
            evol_noli,
            dyna_trans,
            dyna_harmo,
            mode_meca,
            mode_empi,
            mode_meca_c,
            evol_varc,
        )

    if TYPE_RESU == "EVOL_CHAR":
        return evol_char
    if TYPE_RESU == "EVOL_THER":
        return evol_ther
    if TYPE_RESU == "EVOL_ELAS":
        return evol_elas
    if TYPE_RESU == "EVOL_NOLI":
        return evol_noli
    if TYPE_RESU == "DYNA_TRANS":
        return dyna_trans
    if TYPE_RESU == "DYNA_HARMO":
        return dyna_harmo
    if TYPE_RESU == "MODE_MECA":
        return mode_meca
    if TYPE_RESU == "MODE_EMPI":
        return mode_empi
    if TYPE_RESU == "MODE_MECA_C":
        return mode_meca_c
    if TYPE_RESU == "EVOL_VARC":
        return evol_varc
    raise AsException("type de concept resultat non prevu")


def lire_resu_type(RESULTAT, **args):
    if args.get("__all__"):
        return (
            evol_char,
            evol_ther,
            evol_elas,
            evol_noli,
            dyna_trans,
            dyna_harmo,
            mode_meca,
            mode_empi,
            mode_meca_c,
            evol_varc,
        )

    return AsType(RESULTAT)


# pour éviter d'écrire 3 fois cette liste :
def l_nom_cham_pas_elga():
    return list(set(C_NOM_CHAM_INTO()) - set(C_NOM_CHAM_INTO("ELGA")))


LIRE_RESU = OPER(
    nom="LIRE_RESU",
    op=150,
    sd_prod=lire_resu_prod,
    reentrant="f:RESULTAT",
    fr=tr(
        "Lire dans un fichier, soit format IDEAS, soit au format MED,"
        " des champs et les stocker dans une SD résultat"
    ),
    regles=(
        UN_PARMI("MAILLAGE", "MODELE"),
        UN_PARMI(
            "TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "INST", "LIST_INST", "FREQ", "LIST_FREQ"
        ),
    ),
    # 0) mots cles generaux :
    # ----------------------
    TYPE_RESU=SIMP(
        statut="o",
        typ="TXM",
        into=(
            "EVOL_THER",
            "EVOL_ELAS",
            "EVOL_NOLI",
            "MODE_MECA",
            "MODE_MECA_C",
            "DYNA_TRANS",
            "DYNA_HARMO",
            "EVOL_CHAR",
            "EVOL_VARC",
            "MODE_EMPI",
        ),
    ),
    FORMAT=SIMP(statut="o", typ="TXM", into=("IDEAS", "IDEAS_DS58", "MED")),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
    # Re-use
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(
        statut="f",
        typ=(
            evol_ther,
            evol_elas,
            evol_noli,
            mode_meca,
            mode_meca_c,
            dyna_trans,
            dyna_harmo,
            evol_char,
            mode_empi,
        ),
    ),
    # General parameters
    MAILLAGE=SIMP(statut="f", typ=maillage_sdaster),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    # Select storing
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    b_acce_reel=BLOC(
        condition="""(exists("INST"))or(exists("LIST_INST"))or(exists("FREQ"))or(exists("LIST_FREQ"))""",
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    # For transient cases: loads
    b_evol_elas=BLOC(
        condition="""equal_to("TYPE_RESU", 'EVOL_ELAS')""",
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
        ),
    ),
    b_evol_ther=BLOC(
        condition="""equal_to("TYPE_RESU", 'EVOL_THER')""",
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_ther, char_cine_ther)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        ),
    ),
    # For non-linear cases: loads and behaviour
    b_evol_noli=BLOC(
        condition="""equal_to("TYPE_RESU", 'EVOL_NOLI')""",
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
    ),
    # For dynamic modes
    b_mode_meca=BLOC(
        condition="""(equal_to("TYPE_RESU", 'MODE_MECA')or(equal_to("TYPE_RESU", 'MODE_MECA_C')))""",
        MATR_RIGI=SIMP(statut="f", typ=matr_asse_depl_r, max=1),
        MATR_MASS=SIMP(statut="f", typ=matr_asse_depl_r, max=1),
    ),
    # For empiric modes
    b_mode_empi=BLOC(
        condition="""equal_to("TYPE_RESU", 'MODE_EMPI')""",
        NUME_PLAN=SIMP(statut="f", typ="I", defaut=0),
    ),
    # 1-1 ideas dataset-58 :
    # ----------------------
    b_data58=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS_DS58')""",
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=19, inout="in"),
    ),
    b_data58b=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS_DS58') and is_in("TYPE_RESU", ('DYNA_TRANS', 'DYNA_HARMO'))""",
        NOM_CHAM=SIMP(
            statut="o",
            typ="TXM",
            validators=NoRepeat(),
            into=("DEPL", "VITE", "ACCE", "EPSI_NOEU", "SIEF_NOEU"),
            max="**",
        ),
        REDEFI_ORIENT=FACT(
            statut="f",
            max="**",
            regles=(PRESENT_PRESENT("CODE_DIR", "DIRECTION", "NOEUD"),),
            CODE_DIR=SIMP(statut="f", typ="I", into=(1, 2, 3)),
            DIRECTION=SIMP(statut="f", typ="R", min=3, max=3),
            NOEUD=SIMP(statut="f", typ=no, validators=NoRepeat(), max="**"),
        ),
    ),
    # 1-2 ideas  :
    # ---------
    b_ideas=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS')""",
        NB_VARI=SIMP(statut="f", typ="I"),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=19, inout="in"),
        NOM_CHAM=SIMP(
            statut="o", typ="TXM", validators=NoRepeat(), max="**", into=l_nom_cham_pas_elga()
        ),
        FORMAT_IDEAS=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("POSI_INST", "POSI_FREQ"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=l_nom_cham_pas_elga()),
            NUME_DATASET=SIMP(statut="f", typ="I", into=(55, 57, 2414)),
            RECORD_3=SIMP(statut="f", typ="I", max=10),
            RECORD_6=SIMP(statut="f", typ="I", max=10),
            RECORD_9=SIMP(statut="f", typ="I", max=10),
            POSI_ORDRE=SIMP(statut="o", typ="I", min=2, max=2),
            POSI_NUME_MODE=SIMP(statut="f", typ="I", min=2, max=2),
            POSI_MASS_GENE=SIMP(statut="f", typ="I", min=2, max=2),
            POSI_AMOR_GENE=SIMP(statut="f", typ="I", min=2, max=2),
            POSI_INST=SIMP(statut="f", typ="I", min=2, max=2),
            POSI_FREQ=SIMP(statut="f", typ="I", min=2, max=2),
            NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
        ),
    ),
    # 1-4 med :
    # ---------
    b_med=BLOC(
        condition="""equal_to("FORMAT", 'MED')""",
        fr=tr("Nom du champ dans le fichier MED"),
        UNITE=SIMP(
            statut="f",
            typ=UnitType("med"),
            defaut=81,
            inout="in",
            fr=tr("Le fichier est : fort.n."),
        ),
        FORMAT_MED=FACT(
            statut="o",
            max="**",
            regles=(ENSEMBLE("NOM_CMP", "NOM_CMP_MED"), UN_PARMI("NOM_CHAM_MED", "NOM_RESU")),
            NOM_CHAM=SIMP(
                statut="o", typ="TXM", max=1, validators=NoRepeat(), into=C_NOM_CHAM_INTO()
            ),
            NOM_CHAM_MED=SIMP(
                statut="f", typ="TXM", max=1, fr=tr("Nom du champ dans le fichier MED.")
            ),
            NOM_RESU=SIMP(
                statut="f", typ="TXM", max=1, fr=tr("Prefixe du nom de champ dans le fichier MED.")
            ),
            NOM_CMP=SIMP(statut="f", typ="TXM", max="**", fr=tr("Nom des composantes dans ASTER.")),
            NOM_CMP_MED=SIMP(
                statut="f", typ="TXM", max="**", fr=tr("Nom des composantes dans MED.")
            ),
        ),
        PROL_ZERO=SIMP(
            statut="f",
            typ="TXM",
            defaut="OUI",
            into=("OUI", "NON"),
            fr=tr("Affecte des valeurs nulles la ou le champ n'est pas defini (sinon il y a NaN)"),
        ),
    ),
)
