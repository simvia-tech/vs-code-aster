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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def dyna_visco_prod(self, TYPE_RESU, TYPE_MODE, **args):
    if args.get("__all__"):
        return ([dyna_harmo, mode_meca_c, mode_meca, ASSD], [None, mode_meca])

    if TYPE_RESU not in ["HARM", "MODE"]:
        # return a fictional type so that the dectection of syntax problem happens when reading the user commands file
        return ASSD

    if TYPE_RESU == "HARM":
        if "MODE_MECA" in args:
            MODE_MECA = args["MODE_MECA"]
            # in the case 'HARM', the type can be only mode_meca (not mode_meca_c)
            self.type_sdprod(MODE_MECA, mode_meca)
        return dyna_harmo
    elif TYPE_RESU == "MODE":
        if TYPE_MODE == "COMPLEXE":
            return mode_meca_c
        else:
            return mode_meca

    raise AsException("type de concept résultat non prevu")


DYNA_VISCO = MACRO(
    nom="DYNA_VISCO",
    op=OPS("code_aster.MacroCommands.dyna_visco_ops.dyna_visco_ops"),
    sd_prod=dyna_visco_prod,
    reentrant="n",
    fr="Calcul par projection sur modes réels des FRF avec dependance en fréquence de la matrice K",
    # INPUT GENERAL DATA
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    # ELASTIC MATERIALS WITH CONSTANT PROPERTIES
    MATER_ELAS=FACT(
        statut="f",
        max="**",
        regles=(
            AU_MOINS_UN("MATER", "E", "AMOR_HYST", "RHO", "NU"),
            PRESENT_ABSENT("MATER", "E", "AMOR_HYST", "RHO", "NU"),
            ENSEMBLE("E", "AMOR_HYST", "RHO", "NU"),
        ),
        MATER=SIMP(statut="f", typ=mater_sdaster),
        E=SIMP(statut="f", typ="R"),
        AMOR_HYST=SIMP(statut="f", typ="R"),
        RHO=SIMP(statut="f", typ="R"),
        NU=SIMP(statut="f", typ="R"),
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
    ),
    # VISCOELASTIC MATERIALS WITH FREQUENCY DEPENDANT PROPERTIES
    MATER_ELAS_FO=FACT(
        statut="o",
        max="**",
        E=SIMP(statut="o", typ=(fonction_sdaster, formule)),
        AMOR_HYST=SIMP(statut="o", typ=(fonction_sdaster, formule)),
        RHO=SIMP(statut="o", typ="R"),
        NU=SIMP(statut="o", typ="R"),
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
    ),
    TYPE_RESU=SIMP(statut="f", typ="TXM", defaut="HARM", into=("HARM", "MODE")),
    regles=(UN_PARMI("FREQ", "LIST_FREQ")),
    FREQ=SIMP(
        statut="f", typ="R", validators=AndVal((OrdList("croissant"), NoRepeat())), min=2, max="**"
    ),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    # BOUNDARY CONDITIONS AND POSSIBLE EXTERNAL FORCES
    EXCIT=FACT(
        statut="o",
        max="**",
        CHARGE=SIMP(statut="o", typ=char_meca, validators=NoRepeat(), max="**"),
    ),
    #               KEYWORDS FOR THE MODES COMPUTATION
    b_type_mode_mode=BLOC(
        condition="""equal_to("TYPE_RESU", 'MODE')""",
        TYPE_MODE=SIMP(
            statut="f", typ="TXM", defaut="REEL", into=("REEL", "BETA_REEL", "COMPLEXE")
        ),
    ),
    b_type_mode_harm=BLOC(
        condition="""not equal_to("TYPE_RESU", 'MODE')""",
        TYPE_MODE=SIMP(statut="f", typ="TXM", defaut="REEL", into=("REEL", "BETA_REEL")),
    ),
    RESI_RELA=SIMP(statut="f", typ="R", defaut=1.0e-3),
    #               KEYWORDS FOR THE FREQUENCY RESPONSE COMPUTATION
    b_harm=BLOC(
        condition="""equal_to("TYPE_RESU", 'HARM')""",
        fr="calcul harmonique",
        COEF_FREQ_MAX=SIMP(statut="o", typ="R", val_min=1.5),
        SOLVEUR=C_SOLVEUR("DYNA_LINE_HARM", "GENE"),
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            defaut="DEPL",
            into=("DEPL", "VITE", "ACCE"),
            max=3,
            validators=NoRepeat(),
        ),
        MODE_MECA=SIMP(statut="f", typ=CO),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
