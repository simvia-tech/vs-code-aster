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

# person_in_charge: sylvie.michel-ponnelle at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_CABLE_BP = MACRO(
    nom="DEFI_CABLE_BP",
    op=OPS("code_aster.MacroCommands.defi_cable_bp_ops.defi_cable_bp_ops"),
    sd_prod=cabl_precont,
    fr=tr(
        "Calculer les profils initiaux de tension le long des cables "
        "de précontrainte d'une structure en béton"
    ),
    reentrant="n",
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    CARA_ELEM=SIMP(statut="o", typ=cara_elem),
    GROUP_MA_BETON=SIMP(statut="o", typ=grma, max="**"),
    TYPE_ANCRAGE=SIMP(statut="o", typ="TXM", min=2, max=2, into=("ACTIF", "PASSIF")),
    TENSION_INIT=SIMP(statut="o", typ="R", val_min=0.0e0),
    RECUL_ANCRAGE=SIMP(statut="o", typ="R", val_min=0.0e0),
    ADHERENT=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    b_adherent=BLOC(
        condition="""(equal_to("ADHERENT", 'OUI'))""",
        regles=(
            UN_PARMI("DEFI_CABLE", "MODI_CABLE_ETCC", "MODI_CABLE_RUPT"),
            EXCLUS("R_J", "NBH_RELAX"),
        ),
        DEFI_CABLE=FACT(
            statut="f",
            max="**",
            regles=(
                PRESENT_ABSENT("TABL_CABLE", "GROUP_MA", "GROUP_NO_ANCRAGE"),
                PRESENT_PRESENT("GROUP_NO_ANCRAGE", "GROUP_MA"),
            ),
            GROUP_MA=SIMP(statut="f", typ=grma),
            GROUP_NO_ANCRAGE=SIMP(statut="f", typ=grno, validators=NoRepeat(), min=2, max=2),
            TABL_CABLE=SIMP(statut="f", typ=table_sdaster),
        ),
        MODI_CABLE_RUPT=FACT(
            statut="f",
            max="**",
            GROUP_MA=SIMP(statut="o", typ=grma),
            GROUP_NO_ANCRAGE=SIMP(statut="o", typ=grno, validators=NoRepeat(), min=2, max=2),
            TENSION=SIMP(statut="o", typ=table_sdaster),
        ),
        TYPE_RELAX=SIMP(
            statut="f",
            typ="TXM",
            into=("SANS", "BPEL", "ETCC_DIRECT", "ETCC_REPRISE"),
            defaut="SANS",
        ),
        b_relax_bpel=BLOC(
            condition="""equal_to("TYPE_RELAX", 'BPEL')""",
            R_J=SIMP(statut="o", typ="R", val_min=0.0e0),
        ),
        b_relax_etcc1=BLOC(
            condition="""equal_to("TYPE_RELAX", 'ETCC_DIRECT')""",
            NBH_RELAX=SIMP(statut="o", typ="R", val_min=0.0e0),
        ),
        b_relax_etcc2=BLOC(
            condition="""equal_to("TYPE_RELAX", 'ETCC_REPRISE')""",
            MODI_CABLE_ETCC=FACT(
                statut="f",
                max="**",
                GROUP_MA=SIMP(statut="o", typ=grma),
                GROUP_NO_ANCRAGE=SIMP(statut="o", typ=grno, validators=NoRepeat(), min=2, max=2),
                TENSION=SIMP(statut="o", typ=table_sdaster),
            ),
            NBH_RELAX=SIMP(statut="o", typ="R", val_min=0.0e0),
        ),
        #         PERT_ELAS       =SIMP(statut='f',typ='TXM',into=("OUI","NON"),defaut="NON"),
        #           b_pert_elas   =BLOC(condition = """equal_to("PERT_ELAS", 'OUI')""",
        #                  EP_BETON  = SIMP(statut='o',typ='R',val_min=0.E+0),
        #                  ESP_CABLE = SIMP(statut='o',typ='R',val_min=0.E+0)
        #                  ) ,
        CONE=FACT(
            statut="f",
            RAYON=SIMP(statut="o", typ="R", val_min=0.0e0),
            LONGUEUR=SIMP(statut="o", typ="R", val_min=0.0e0),
            PRESENT=SIMP(statut="o", typ="TXM", min=2, max=2, into=("OUI", "NON")),
        ),
    ),
    b_non_adherent=BLOC(
        condition="""(equal_to("ADHERENT", 'NON'))""",
        DEFI_CABLE=FACT(
            statut="o",
            max="**",
            GROUP_MA=SIMP(statut="o", typ=grma),
            GROUP_NO_ANCRAGE=SIMP(statut="o", typ=grno, validators=NoRepeat(), min=2, max=2),
        ),
        TYPE_RELAX=SIMP(statut="c", typ="TXM", into=("SANS",), defaut="SANS"),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
