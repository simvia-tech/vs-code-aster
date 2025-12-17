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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def crea_elem_ssd_prod(self, NUME_DDL, **args):
    if args.get("__all__"):
        return ([macr_elem_dyna], [None, nume_ddl_sdaster])

    if NUME_DDL:
        self.type_sdprod(NUME_DDL, nume_ddl_sdaster)
    return macr_elem_dyna


CREA_ELEM_SSD = MACRO(
    nom="CREA_ELEM_SSD",
    op=OPS("code_aster.MacroCommands.crea_elem_ssd_ops.crea_elem_ssd_ops"),
    sd_prod=crea_elem_ssd_prod,
    reentrant="n",
    fr=tr(
        "Creation de macro-element dynamique en enchainant les commandes : "
        "CALC_MATR_ELEM, NUME_DDL, ASSE_MATRICE, MODE_ITER_SIMULT, "
        "DEFI_INTERF_DYNA, DEFI_BASE_MODALE et MACR_ELEM_DYNA"
    ),
    # pour CAL_MATR_ELEM + NUME_DDL + ASSE_MATRICE + MODE_ITER_SIMULT + MODE_STATIQUE
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    NUME_DDL=SIMP(statut="f", typ=CO),
    CHARGE=SIMP(statut="f", typ=(char_meca, char_ther, char_acou), validators=NoRepeat(), max="**"),
    # pour DEFI_INTERF_DYNA
    INTERFACE=FACT(
        statut="o",
        max="**",
        regles=(ENSEMBLE("NOM", "TYPE"), UN_PARMI("NOEUD", "GROUP_NO")),
        NOM=SIMP(statut="o", typ="TXM"),
        TYPE=SIMP(statut="o", typ="TXM", into=("MNEAL", "CRAIGB", "CB_HARMO")),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        FREQ=SIMP(statut="f", typ="R", defaut=1.0),
        MASQUE=SIMP(statut="f", typ="TXM", max="**"),
    ),
    # pour DEFI_BASE_MODALE
    BASE_MODALE=FACT(
        statut="o",
        max=1,
        TYPE=SIMP(statut="o", typ="TXM", max=1, into=("CLASSIQUE", "RITZ")),
        b_ritz=BLOC(
            condition="""equal_to("TYPE", 'RITZ') """,
            fr=tr("Base de type Ritz"),
            TYPE_MODE=SIMP(
                statut="f", typ="TXM", into=("STATIQUE", "INTERFACE"), defaut="INTERFACE"
            ),
            b_intf=BLOC(
                condition="""equal_to("TYPE_MODE", 'INTERFACE') """,
                NMAX_MODE_INTF=SIMP(statut="f", typ="I", defaut=10, val_min=1),
            ),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    # -------------------------------------------------------------------
    # Catalogue commun SOLVEUR (pour MODE_ITER_SIMULT, MODE_STATIQUE, DEFI_BASE_MODALE)
    SOLVEUR=C_SOLVEUR("CREA_ELEM_SSD"),
    # -------------------------------------------------------------------
    # pour le calcul modal
    CALC_FREQ=FACT(
        statut="d",
        STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            defaut="PLUS_PETITE",
            into=("PLUS_PETITE", "BANDE", "CENTRE", "SANS"),
            fr=tr("Choix de l option et par consequent du shift du probleme modal"),
        ),
        b_plus_petite=BLOC(
            condition="""equal_to("OPTION", 'PLUS_PETITE')""",
            fr=tr("Recherche des plus petites valeurs propres"),
            NMAX_FREQ=SIMP(statut="f", typ="I", defaut=10, val_min=0),
        ),
        b_centre=BLOC(
            condition="""equal_to("OPTION", 'CENTRE')""",
            fr=tr("Recherche des valeurs propres les plus proches d une valeur donnee"),
            FREQ=SIMP(
                statut="o",
                typ="R",
                fr=tr("Frequence autour de laquelle on cherche les frequences propres"),
            ),
            AMOR_REDUIT=SIMP(statut="f", typ="R"),
            NMAX_FREQ=SIMP(statut="f", typ="I", defaut=10, val_min=0),
        ),
        b_bande=BLOC(
            condition="""(equal_to("OPTION", 'BANDE'))""",
            fr=tr("Recherche des valeurs propres dans une bande donnee"),
            NMAX_FREQ=SIMP(statut="f", typ="I", defaut=9999, val_min=0),
            FREQ=SIMP(
                statut="o",
                typ="R",
                min=2,
                validators=NoRepeat(),
                max="**",
                fr=tr("Valeurs des frequences delimitant les bandes de recherche"),
            ),
        ),
        APPROCHE=SIMP(
            statut="f",
            typ="TXM",
            defaut="REEL",
            into=("REEL", "IMAG", "COMPLEXE"),
            fr=tr("Choix du pseudo-produit scalaire pour la resolution du probleme quadratique"),
        ),
        DIM_SOUS_ESPACE=SIMP(statut="f", typ="I"),
    ),
)
