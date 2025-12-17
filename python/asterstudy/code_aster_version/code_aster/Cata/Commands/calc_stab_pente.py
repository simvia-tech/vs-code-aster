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


def calc_stab_pente_prod(self, CHAM_DEFO, **args):
    """Return result type of CALC_STAB_PENTE."""
    if args.get("__all__"):
        return ([table_sdaster], [None, evol_noli])

    if CHAM_DEFO:
        self.type_sdprod(CHAM_DEFO, evol_noli)

    return table_sdaster


CALC_STAB_PENTE = MACRO(
    nom="CALC_STAB_PENTE",
    op=OPS("code_aster.MacroCommands.calc_stab_pente_ops.calc_stab_pente_ops"),
    sd_prod=calc_stab_pente_prod,
    reentrant="n",
    docu="U4.xx.xx",
    fr=tr("Calculer le facteur de sécurité d'une slope par méthode de réduction de la résistance"),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    METHODE_STAB=SIMP(
        statut="f",
        typ="TXM",
        defaut="SRM",
        into=("SRM", "LEM"),
        fr=tr("Méthode de calcul de stabilité des pentes"),
    ),
    # Méthode SRM
    b_srm=BLOC(
        condition="""equal_to("METHODE_STAB", "SRM")""",
        MODELE=SIMP(statut="o", typ=modele_sdaster),
        # Définition de la zone où s'applique la SRM
        regles=UN_PARMI("TOUT", "GROUP_MA"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        # Configuration du calcul non-linéaire
        EXCIT=FACT(
            statut="f",
            max="**",
            CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TYPE_CHARGE=SIMP(
                statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE", "SUIV", "DIDI")
            ),
        ),
        INCREMENT=C_INCREMENT(),
        CONVERGENCE=C_CONVERGENCE("MECA_NON_LINE"),
        COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
        # Configuration de la recherche du FS
        FS=FACT(
            statut="f",
            max=1,
            FS_INIT=SIMP(statut="f", typ="R", defaut=1.0, fr=tr("Facteur de sécurité initial")),
            INCR_INIT=SIMP(statut="f", typ="R", defaut=0.1, fr=tr("Incrément initial de FS")),
            RESI_MAXI=SIMP(
                statut="f",
                typ="R",
                defaut=0.01,
                fr=tr("Résidue du FS après le dernier raffinement"),
            ),
            ITER_MAXI=SIMP(statut="f", typ="I", defaut=100, fr=tr("Nombre d'itération maximal")),
            METHODE=SIMP(
                statut="f",
                typ="TXM",
                into=("EXPONENTIELLE", "LINEAIRE"),
                defaut="EXPONENTIELLE",
                fr=tr("Loi de variation de l'incrément du FS"),
            ),
            b_lineaire=BLOC(
                condition="""equal_to("METHODE", "LINEAIRE")""",
                ITER_RAFF_LINE=SIMP(statut="o", typ="I", fr=tr("Nombre de raffinement souhaité")),
            ),
        ),
    ),
    # Méthode LEM
    b_lem=BLOC(
        condition="""equal_to("METHODE_STAB", "LEM")""",
        METHODE_LEM=SIMP(
            statut="f",
            typ="TXM",
            defaut="BISHOP",
            into=("BISHOP", "FELLENIUS", "SPENCER", "MORGENSTERN_PRICE"),
            ft=tr("Méthode de calcul LEM"),
        ),
        CRITERE=SIMP(
            statut="f",
            typ="TXM",
            defaut="MOHR_COULOMB",
            into=("MOHR_COULOMB", "DRUCK_PRAGER"),
            fr=tr("Critère de rupture"),
        ),
        GROUP_MA=SIMP(
            statut="o",
            typ=grma,
            validators=NoRepeat(),
            max=1,
            fr=tr("Groupe des éléments 1D représentant le profil de la pente"),
        ),
        NB_TRANCHE=SIMP(statut="f", typ="I", defaut=10, fr=tr("Nombre des tranches")),
        # Paramètres raffinement du maillage
        RAFF_MAIL=FACT(
            statut="d",
            max=1,
            NB_RAFF_MAXI=SIMP(
                statut="f", typ="I", defaut=4, fr=tr("Nombre maximum de raffinement du maillage")
            ),
            RAFF_CRIT_STAB=SIMP(statut="f", typ="R", defaut=1e-3, fr=tr("Residu maximal du FS")),
        ),
        X1_MINI=SIMP(statut="o", typ="R", fr=tr("Limite inférieure de la bande gauche")),
        X1_MAXI=SIMP(statut="o", typ="R", fr=tr("Limite supérieure de la bande gauche")),
        X2_MINI=SIMP(statut="o", typ="R", fr=tr("Limite inférieure de la bande gauche")),
        X2_MAXI=SIMP(statut="o", typ="R", fr=tr("Limite supérieure de la bande gauche")),
        # Cas de surface circulaire
        b_circ=BLOC(
            condition="""(equal_to("METHODE_LEM", "BISHOP"))or(equal_to("METHODE_LEM", "FELLENIUS"))""",
            NB_POINT_1=SIMP(
                statut="f",
                typ="I",
                defaut=5,
                fr=tr("Nombre des points à tester dans la bande gauche"),
            ),
            NB_POINT_2=SIMP(
                statut="f",
                typ="I",
                defaut=5,
                fr=tr("Nombre des points à tester dans la bande droite"),
            ),
            Y_MINI=SIMP(statut="f", typ="R", fr=tr("Limite inférieure de la droite tangentielle")),
            Y_MAXI=SIMP(statut="f", typ="R", fr=tr("Limite supérieure de la droite tangentielle")),
        ),
        # Cas de surface non-circulaire
        b_noncirc=BLOC(
            condition="""(equal_to("METHODE_LEM", "MORGENSTERN_PRICE")or(equal_to("METHODE_LEM", "SPENCER")))""",
            ALGO_EFWA=FACT(
                statut="d",
                max=1,
                ETAT_INIT=SIMP(
                    statut="f",
                    typ=table_sdaster,
                    fr=tr("Table des résultat issu de CALC_STAB_PENTE"),
                ),
                ITER_MAXI=SIMP(
                    statut="f", typ="I", defaut=1e4, fr=tr("Nombre maximum d'itération EFWA")
                ),
                A=SIMP(statut="o", typ="R"),
                N=SIMP(statut="f", typ="I", defaut=5),
                M=SIMP(statut="f", typ="I", defaut=40),
                MG=SIMP(statut="f", typ="I", defaut=5),
                SA=SIMP(statut="f", typ="R", defaut=0.04),
                SB=SIMP(statut="f", typ="R", defaut=0.8),
                NB_STAB_MAXI=SIMP(statut="f", typ="I", defaut=10),
                CRIT_STAB=SIMP(statut="f", typ="R", defaut=1e-3),
                MARGE_PENTE=SIMP(
                    statut="f",
                    typ="R",
                    defaut=0.1,
                    fr=tr("Marge évitant que la surface soit trop proche du profil de la pente"),
                ),
            ),
        ),
    ),
    CHAM_DEFO=SIMP(
        statut="f", typ=CO, fr=tr("Résultat évol_noli visualisant la surface de rupture")
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
