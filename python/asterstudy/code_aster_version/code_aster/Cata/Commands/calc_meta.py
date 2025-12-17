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

# person_in_charge: sofiane.hendili at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_META = OPER(
    nom="CALC_META",
    op=194,
    sd_prod=evol_ther,
    reentrant="o:RESULTAT",
    fr=tr("Calcule l'évolution métallurgique à partir du résultat d'un calcul thermique"),
    regles=(PRESENT_ABSENT("TOUT", "GROUP_MA"),),
    reuse=SIMP(statut="c", typ=CO),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    RESULTAT=SIMP(statut="o", typ=evol_ther),
    OPTION=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max="**",
        into=C_NOM_CHAM_INTO(phenomene="METALLURGIE"),
    ),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    GROUP_MA=SIMP(
        statut="f",
        typ=grma,
        validators=NoRepeat(),
        max="**",
        fr=tr("le calcul ne sera effectué que sur ces mailles là"),
    ),
    b_meta=BLOC(
        condition="""is_in('OPTION', ('META_ELNO','META_NOEU'))""",
        ETAT_INIT=FACT(
            statut="o",
            regles=(UN_PARMI("EVOL_THER", "META_INIT_ELNO"),),
            EVOL_THER=SIMP(statut="f", typ=evol_ther),
            META_INIT_ELNO=SIMP(statut="f", typ=carte_sdaster),
            b_etat=BLOC(
                condition="""exists("EVOL_THER")""",
                regles=(UN_PARMI("NUME_INIT", "INST_INIT"),),
                NUME_INIT=SIMP(statut="f", typ="I"),
                INST_INIT=SIMP(statut="f", typ="R"),
                b_inst=BLOC(
                    condition="""exists("INST_INIT")""",
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
        ),
        COMPORTEMENT=FACT(
            statut="o",
            max=1,
            RELATION=SIMP(statut="o", typ="TXM", into=("ACIER", "ZIRC")),
            b_acier=BLOC(
                condition="""equal_to("RELATION", 'ACIER')""",
                LOI_META=SIMP(statut="f", typ="TXM", defaut="WAECKEL", into=("WAECKEL",)),
            ),
            b_zirc=BLOC(
                condition="""equal_to("RELATION", 'ZIRC')""",
                LOI_META=SIMP(statut="f", typ="TXM", defaut="EDGAR", into=("EDGAR",)),
            ),
            regles=(PRESENT_ABSENT("TOUT", "GROUP_MA", "MAILLE"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        ),
    ),
)
