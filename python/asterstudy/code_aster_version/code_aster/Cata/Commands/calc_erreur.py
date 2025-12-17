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

# person_in_charge: josselin.delmas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_erreur_prod(RESULTAT, **args):
    if args.get("__all__"):
        return (resultat_sdaster,)

    if AsType(RESULTAT) is not None:
        return AsType(RESULTAT)
    raise AsException("type de concept resultat non prevu")


CALC_ERREUR = OPER(
    nom="CALC_ERREUR",
    op=42,
    sd_prod=calc_erreur_prod,
    reentrant="f:RESULTAT",
    fr=tr("Compléter ou créer un résultat en calculant des champs d'erreur"),
    reuse=SIMP(statut="c", typ=CO),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster, fr=tr("Résultat d'une commande globale")),
    regles=(
        EXCLUS(
            "TOUT_ORDRE",
            "NUME_ORDRE",
            "INST",
            "FREQ",
            "NUME_MODE",
            "NOEUD_CMP",
            "LIST_INST",
            "LIST_FREQ",
            "LIST_ORDRE",
            "NOM_CAS",
        ),
    ),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    NOM_CAS=SIMP(statut="f", typ="TXM"),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI"),
    # -----------------------------------------------------------------------
    # pour conserver la compatibilité mais ne sert à rien
    # -----------------------------------------------------------------------
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    EXCIT=FACT(
        statut="f",
        max="**",
        fr=tr("Charges contenant les températures, les efforts répartis pour les poutres..."),
        CHARGE=SIMP(statut="o", typ=(char_meca, char_cine_meca)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    # -----------------------------------------------------------------------
    OPTION=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max="**",
        into=C_NOM_CHAM_INTO(phenomene="ERREUR"),
    ),
    b_erre_qi=BLOC(
        condition="""is_in('OPTION', ('QIRE_ELEM','QIZ1_ELEM','QIZ2_ELEM','QIRE_ELNO','QIRE_NOEU'))""",
        RESU_DUAL=SIMP(statut="o", typ=resultat_sdaster, fr=tr("Résultat du problème dual")),
    ),
    b_sing=BLOC(
        condition="""is_in('OPTION', 'SING_ELEM')""",
        PREC_ERR=SIMP(
            statut="o",
            typ="R",
            val_min=0.0,
            fr=tr("Précision demandée pour calculer la carte de taille des éléments"),
        ),
        TYPE_ESTI=SIMP(
            statut="f",
            typ="TXM",
            into=("ERME_ELEM", "ERZ1_ELEM", "ERZ2_ELEM", "QIRE_ELEM", "QIZ1_ELEM", "QIZ2_ELEM"),
            fr=tr("Choix de l'estimateur d'erreur"),
        ),
    ),
    # -------------------------------------------------------------------
    #    Catalogue commun SOLVEUR (utilisé actuellement pour estimateur d'erreur ZZ1)
    SOLVEUR=C_SOLVEUR("CALC_ERREUR"),
    # -------------------------------------------------------------------
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
