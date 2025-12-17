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

# person_in_charge: mickael.abbas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

from .affe_char_meca import compat_syntax

AFFE_CHAR_MECA_C = OPER(
    nom="AFFE_CHAR_MECA_C",
    op=7,
    sd_prod=char_meca,
    fr=tr("Affectation de charges et conditions aux limites mécaniques complexes"),
    reentrant="n",
    compat_syntax=compat_syntax,
    regles=(AU_MOINS_UN("DDL_IMPO", "FORCE_POUTRE", "LIAISON_DDL"),),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    DOUBLE_LAGRANGE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
    DDL_IMPO=FACT(
        statut="f",
        max="**",
        fr=tr(
            "Impose à des noeuds une ou plusieurs valeurs de déplacement (ou de certaines grandeurs asscociées)"
        ),
        regles=(
            AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO", "NOEUD"),
            AU_MOINS_UN(
                "DX", "DY", "DZ", "DRX", "DRY", "DRZ", "GRX", "PRES", "PHI", "BLOCAGE", "GLIS"
            ),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        BLOCAGE=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            into=("DEPLACEMENT", "ROTATION"),
            min=1,
            max=2,
        ),
        DX=SIMP(statut="f", typ="C"),
        DY=SIMP(statut="f", typ="C"),
        DZ=SIMP(statut="f", typ="C"),
        DRX=SIMP(statut="f", typ="C"),
        DRY=SIMP(statut="f", typ="C"),
        DRZ=SIMP(statut="f", typ="C"),
        GRX=SIMP(statut="f", typ="C"),
        PRES=SIMP(statut="f", typ="C"),
        PHI=SIMP(statut="f", typ="C"),
        GLIS=SIMP(statut="f", typ="C"),
    ),
    FORCE_POUTRE=FACT(
        statut="f",
        max="**",
        fr=tr("Applique des forces linéiques sur des éléments de type poutre"),
        regles=(
            AU_MOINS_UN("TOUT", "GROUP_MA"),
            PRESENT_ABSENT("TOUT", "GROUP_MA"),
            AU_MOINS_UN("FX", "FY", "FZ", "N", "VY", "VZ"),
            PRESENT_ABSENT("FX", "N", "VY", "VZ"),
            PRESENT_ABSENT("FY", "N", "VY", "VZ"),
            PRESENT_ABSENT("FZ", "N", "VY", "VZ"),
            PRESENT_ABSENT("N", "FX", "FY", "FZ"),
            PRESENT_ABSENT("VY", "FX", "FY", "FZ"),
            PRESENT_ABSENT("VZ", "FX", "FY", "FZ"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FORCE", into=("VENT", "FORCE")),
        FX=SIMP(statut="f", typ="C"),
        FY=SIMP(statut="f", typ="C"),
        FZ=SIMP(statut="f", typ="C"),
        N=SIMP(statut="f", typ="C"),
        VY=SIMP(statut="f", typ="C"),
        VZ=SIMP(statut="f", typ="C"),
    ),
    LIAISON_DDL=FACT(
        statut="f",
        max="**",
        fr=tr("Définit une relation linéaire entre les DDLs de deux ou plusieurs noeuds"),
        regles=(UN_PARMI("GROUP_NO", "NOEUD"),),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        DDL=SIMP(statut="o", typ="TXM", into=C_NOM_DDL_INTO("MECANIQUE"), max="**"),
        COEF_MULT=SIMP(statut="o", typ="R", max="**"),
        COEF_IMPO=SIMP(statut="o", typ="C"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
