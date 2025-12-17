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


def assemblage_prod(self, NUME_DDL, MATR_ASSE, VECT_ASSE, **args):
    if args.get("__all__"):
        return (
            [None],
            [None, nume_ddl_sdaster],
            [None, matr_asse_depl_r, matr_asse_pres_c, matr_asse_temp_r, matr_asse_depl_c],
            [None, cham_no_sdaster],
        )

    if (not MATR_ASSE) and (not VECT_ASSE):
        raise AsException("Aucun concept a assembler")
    if not NUME_DDL:
        raise AsException("Impossible de typer les concepts resultats")
    if NUME_DDL.is_typco():
        self.type_sdprod(NUME_DDL, nume_ddl_sdaster)

    if MATR_ASSE is not None:
        for m in MATR_ASSE:
            opti = m["OPTION"]
            if opti in (
                "RIGI_MECA",
                "RIGI_FLUI_STRU",
                "MASS_MECA",
                "MASS_FLUI_STRU",
                "RIGI_GEOM",
                "RIGI_ROTA",
                "AMOR_MECA",
                "IMPE_MECA",
                "ONDE_FLUI",
                "MASS_MECA_DIAG",
                "MECA_GYRO",
                "RIGI_GYRO",
            ):
                t = matr_asse_depl_r

            if opti in ("RIGI_ACOU", "MASS_ACOU", "AMOR_ACOU"):
                t = matr_asse_pres_c

            if opti in ("RIGI_THER", "RIGI_THER_CONV", "RIGI_THER_CONV_D"):
                t = matr_asse_temp_r

            if opti == "RIGI_MECA_HYST":
                t = matr_asse_depl_c

            self.type_sdprod(m["MATRICE"], t)

    if VECT_ASSE is not None:
        for v in VECT_ASSE:
            self.type_sdprod(v["VECTEUR"], cham_no_sdaster)

    return None


ASSEMBLAGE = MACRO(
    nom="ASSEMBLAGE",
    op=OPS("code_aster.MacroCommands.assemblage_ops.assemblage_ops"),
    sd_prod=assemblage_prod,
    regles=(AU_MOINS_UN("MATR_ASSE", "VECT_ASSE"),),
    fr=tr("Calcul des matrices et vecteurs assemblés "),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    INST=SIMP(statut="f", typ="R", defaut=0.0),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    CHARGE=SIMP(statut="f", typ=(char_meca, char_ther, char_acou), validators=NoRepeat(), max="**"),
    CHAR_CINE=SIMP(statut="f", typ=(char_cine_meca, char_cine_ther, char_cine_acou)),
    NUME_DDL=SIMP(statut="o", typ=(nume_ddl_sdaster, CO)),
    MATR_ASSE=FACT(
        statut="f",
        max="**",
        MATRICE=SIMP(statut="o", typ=CO),
        OPTION=SIMP(
            statut="o",
            typ="TXM",
            into=(
                "RIGI_MECA",
                "MASS_MECA",
                "MASS_MECA_DIAG",
                "AMOR_MECA",
                "RIGI_MECA_HYST",
                "IMPE_MECA",
                "ONDE_FLUI",
                "RIGI_FLUI_STRU",
                "MASS_FLUI_STRU",
                "RIGI_ROTA",
                "RIGI_GEOM",
                "MECA_GYRO",
                "RIGI_GYRO",
                "RIGI_THER",
                "RIGI_ACOU",
                "MASS_ACOU",
                "AMOR_ACOU",
            ),
        ),
        b_group_ma=BLOC(
            condition="""is_in("OPTION", ('RIGI_GYRO', 'MECA_GYRO', 'IMPE_MECA',
                                          'AMOR_MECA', 'MASS_MECA', 'RIGI_MECA',
                                          'MASS_MECA_DIAG','MASS_FLUI_STRU'))""",
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        ),
        b_rigi_meca=BLOC(
            condition="""equal_to("OPTION", 'RIGI_MECA')""",
            MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        ),
        b_rigi_geom=BLOC(
            condition="""equal_to("OPTION", 'RIGI_GEOM')""",
            SIEF_ELGA=SIMP(statut="o", typ=cham_elem),
            MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        ),
        b_rigi_ther=BLOC(
            condition="""equal_to("OPTION", 'RIGI_THER')""",
            MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        ),
        b_amor_meca=BLOC(
            condition="""equal_to("OPTION", 'AMOR_MECA')""",
            AMOR_FLUI=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
            TYPE_AMOR=SIMP(
                statut="f", typ="TXM", min=1, max=1, into=("TOUT", "ABSO"), defaut="TOUT"
            ),
        ),
        b_impe_meca=BLOC(
            condition="""equal_to("OPTION", 'IMPE_MECA')""",
            VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
        ),
        b_amor_acou=BLOC(
            condition="""equal_to("OPTION", 'AMOR_ACOU')""",
            VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
        ),
        #
    ),  # fin MATR_ASSE
    #
    VECT_ASSE=FACT(
        statut="f",
        max="**",
        VECTEUR=SIMP(statut="o", typ=CO),
        OPTION=SIMP(statut="o", typ="TXM", into=("CHAR_MECA", "CHAR_ACOU", "CHAR_THER")),
        b_char_meca=BLOC(
            condition="""equal_to("OPTION", 'CHAR_MECA')""",
            fr=tr("chargement mécanique"),
            CHARGE=SIMP(statut="f", typ=char_meca, validators=NoRepeat(), max="**"),
            MODE_FOURIER=SIMP(statut="f", typ="I", defaut=0),
        ),
        b_char_ther=BLOC(
            condition="""equal_to("OPTION", 'CHAR_THER')""",
            fr=tr("chargement thermique"),
            CHARGE=SIMP(statut="f", typ=char_ther, validators=NoRepeat(), max="**"),
        ),
        b_char_acou=BLOC(
            condition="""equal_to("OPTION", 'CHAR_ACOU')""",
            fr=tr("chargement acoustique"),
            CHARGE=SIMP(statut="f", typ=char_acou, validators=NoRepeat(), max="**"),
        ),
        #
    ),  # fin VECT_ASSE
    #
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
