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

# person_in_charge: sebastien.fayolle at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_GLRC = OPER(
    nom="DEFI_GLRC",
    op=57,
    sd_prod=mater_sdaster,
    reentrant="f:BETON|NAPPE|CABLE_PREC|LINER:MATER",
    fr=tr(
        "Déterminer les caractéristiques homogenéisées du béton armé à partir des propriétés du béton et des  "
        " armatures"
    ),
    reuse=SIMP(statut="c", typ=mater_sdaster),
    RELATION=SIMP(statut="f", typ="TXM", defaut="GLRC_DAMAGE", into=("GLRC_DM", "GLRC_DAMAGE")),
    ALPHA=SIMP(statut="f", typ="R", val_min=0.0e0, fr="Coef. dilatation thermique"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    b_glrc_dm=BLOC(
        condition="""equal_to("RELATION", 'GLRC_DM')""",
        fr=tr("Paramètres de la loi GLRC_DM"),
        BETON=FACT(
            statut="o",
            max=1,
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            EPAIS=SIMP(statut="o", typ="R", val_min=0.0e0),
        ),
        NAPPE=FACT(
            statut="o",
            max=1,
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            OMY=SIMP(statut="o", typ="R", val_min=0.0e0),
            OMX=SIMP(statut="o", typ="R", val_min=0.0e0),
            RY=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
            RX=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
        ),
        RHO=SIMP(statut="f", typ="R", val_min=0.0e0),
        AMOR_ALPHA=SIMP(statut="f", typ="R", val_min=0.0e0),
        AMOR_BETA=SIMP(statut="f", typ="R", val_min=0.0e0),
        AMOR_HYST=SIMP(statut="f", typ="R", val_min=0.0e0),
        PENTE=FACT(
            statut="o",
            max=1,
            TRACTION=SIMP(
                statut="f",
                typ="TXM",
                defaut="RIGI_ACIER",
                into=("PLAS_ACIER", "UTIL", "RIGI_ACIER"),
            ),
            b_trac_util=BLOC(
                condition="""equal_to("TRACTION", 'UTIL')""",
                EPSI_MEMB=SIMP(statut="f", typ="R", defaut=0.0e0),
            ),
            FLEXION=SIMP(
                statut="f",
                typ="TXM",
                defaut="RIGI_INIT",
                into=("UTIL", "RIGI_INIT", "RIGI_ACIER", "PLAS_ACIER"),
            ),
            b_flex_util=BLOC(
                condition="""equal_to("FLEXION", 'UTIL')""", KAPPA_FLEX=SIMP(statut="o", typ="R")
            ),
        ),
        CISAIL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    ),
    b_glrc_damage=BLOC(
        condition="""equal_to("RELATION", 'GLRC_DAMAGE')""",
        fr=tr("Paramètres de la loi GLRC_DAMAGE"),
        CISAIL_NL=FACT(
            statut="f",
            max=1,
            BTD1=SIMP(statut="o", typ="R"),
            BTD2=SIMP(statut="o", typ="R"),
            TSD=SIMP(statut="o", typ="R"),
        ),
        BETON=FACT(
            statut="o",
            max=1,
            regles=(
                ENSEMBLE("MP1X", "MP1Y", "MP2X", "MP2Y"),
                ENSEMBLE("MP1X_FO", "MP1Y_FO", "MP2X_FO", "MP2Y_FO"),
                PRESENT_ABSENT("MP1X", "MP1X_FO", "MP1Y_FO", "MP2X_FO", "MP2Y_FO"),
                ENSEMBLE("OMT", "EAT"),
                ENSEMBLE("BT1", "BT2"),
            ),
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            EPAIS=SIMP(statut="o", typ="R", val_min=0.0e0),
            GAMMA=SIMP(statut="o", typ="R", val_min=0.0e0, val_max=1.0e0),
            QP1=SIMP(statut="o", typ="R", val_min=0.0e0, val_max=1.0e0),
            QP2=SIMP(statut="o", typ="R", val_min=0.0e0, val_max=1.0e0),
            C1N1=SIMP(statut="o", typ="R", val_min=0.0e0),
            C1N2=SIMP(statut="o", typ="R", val_min=0.0e0),
            C1N3=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2N1=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2N2=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2N3=SIMP(statut="o", typ="R", val_min=0.0e0),
            C1M1=SIMP(statut="o", typ="R", val_min=0.0e0),
            C1M2=SIMP(statut="o", typ="R", val_min=0.0e0),
            C1M3=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2M1=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2M2=SIMP(statut="o", typ="R", val_min=0.0e0),
            C2M3=SIMP(statut="o", typ="R", val_min=0.0e0),
            OMT=SIMP(statut="f", typ="R", val_min=0.0e0),
            EAT=SIMP(statut="f", typ="R", val_min=0.0e0),
            BT1=SIMP(statut="f", typ="R", val_min=0.0e0),
            BT2=SIMP(statut="f", typ="R", val_min=0.0e0),
            MP1X=SIMP(statut="f", typ="R"),
            MP2X=SIMP(statut="f", typ="R"),
            MP1Y=SIMP(statut="f", typ="R"),
            MP2Y=SIMP(statut="f", typ="R"),
            MP1X_FO=SIMP(statut="f", typ=fonction_sdaster),
            MP2X_FO=SIMP(statut="f", typ=fonction_sdaster),
            MP1Y_FO=SIMP(statut="f", typ=fonction_sdaster),
            MP2Y_FO=SIMP(statut="f", typ=fonction_sdaster),
        ),
        NAPPE=FACT(
            statut="o",
            max=10,
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            OMX=SIMP(statut="o", typ="R", val_min=0.0e0),
            OMY=SIMP(statut="o", typ="R", val_min=0.0e0),
            RX=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
            RY=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
        ),
        CABLE_PREC=FACT(
            statut="f",
            max=1,
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            OMX=SIMP(statut="o", typ="R", val_min=0.0e0),
            OMY=SIMP(statut="o", typ="R", val_min=0.0e0),
            RX=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
            RY=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
            PREX=SIMP(statut="o", typ="R"),
            PREY=SIMP(statut="o", typ="R"),
        ),
        LINER=FACT(
            statut="f",
            max=10,
            MATER=SIMP(statut="o", typ=(mater_sdaster)),
            OML=SIMP(statut="o", typ="R", val_min=0.0e0),
            RLR=SIMP(statut="o", typ="R", val_min=-1.0e0, val_max=1.0e0),
        ),
    ),
)
