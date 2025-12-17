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

# person_in_charge: j-pierre.lefebvre at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *
from ..Language.SyntaxUtils import deprecate


def compat_syntax(keywords):
    """Ignore obsolete keywords.

    Arguments:
        keywords (dict): Keywords arguments of user's keywords, changed
            in place.
    """
    if keywords.pop("PAR_LOT", None):
        deprecate("POURSUITE/PAR_LOT", case=2, level=7)
    if keywords.pop("FORMAT_HDF", None):
        deprecate("POURSUITE/FORMAT_HDF", case=2, level=7)
    if keywords.get("DEBUG", {}):
        if keywords["DEBUG"].pop("HIST_ETAPE", None):
            deprecate("POURSUITE/DEBUG/HIST_ETAPE", case=2, level=7)


POURSUITE = MACRO(
    nom="POURSUITE",
    op=None,
    compat_syntax=compat_syntax,
    repetable="n",
    fr=tr("Poursuite d'une étude à partir de la sauvegarde de sa base globale"),
    IMPR_MACRO=SIMP(
        fr=tr("affichage des sous-commandes produites par les macros dans le fichier mess"),
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="NON",
    ),
    BASE=FACT(
        fr=tr("définition des paramètres associés aux bases JEVEUX"),
        statut="f",
        min=1,
        max=2,
        FICHIER=SIMP(fr=tr("nom de la base"), statut="o", typ="TXM"),
        TITRE=SIMP(statut="f", typ="TXM"),
        CAS=SIMP(statut="f", typ="TXM"),
        NMAX_ENRE=SIMP(fr=tr("nombre maximum d enregistrements"), statut="f", typ="I"),
        LONG_ENRE=SIMP(fr=tr("longueur des enregistrements"), statut="f", typ="I"),
        LONG_REPE=SIMP(fr=tr("longueur du répertoire"), statut="f", typ="I"),
    ),
    # Le mot cle CATALOGUE n'est jamais utilise en POURSUITE mais sa presence est necessaire au bon fonctionnement
    # de la commande, le code source etant commun aux commandes DEBUT et POURSUITE.
    #
    CATALOGUE=FACT(
        statut="f",
        min=1,
        max=10,
        FICHIER=SIMP(statut="o", typ="TXM"),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="in"),
    ),
    ERREUR=FACT(
        fr=tr("comportement en cas d'erreur"),
        statut="f",
        min=1,
        max=1,
        ERREUR_F=SIMP(statut="f", typ="TXM", into=("ABORT", "EXCEPTION")),
        ALARME=SIMP(statut="f", typ="TXM", into=("ALARME", "EXCEPTION")),
    ),
    DEBUG=FACT(
        fr=tr("option de déboggage reservée aux développeurs"),
        statut="d",
        min=1,
        max=1,
        JXVERI=SIMP(
            fr=tr("vérifie l intégrité de la segmentation mémoire"),
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
        ),
        SDVERI=SIMP(
            fr=tr("vérifie la conformité des SD produites par les commandes"),
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
        ),
        JEVEUX=SIMP(
            fr=tr("force les déchargement sur disque"),
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
        ),
        ENVIMA=SIMP(
            fr=tr("imprime les valeurs définies dans ENVIMA"), statut="f", typ="TXM", into=("TEST",)
        ),
        VERI_BASE=SIMP(
            fr=tr("exécute un test de vérification sur les bases"),
            statut="f",
            typ="TXM",
            into=("GLOBALE", "VOLATILE"),
        ),
        VERI_BASE_NB=SIMP(
            fr=tr("pourcentage de la taille de base à écrire"), statut="f", typ="I", defaut=125
        ),
    ),
    MESURE_TEMPS=FACT(
        fr=tr("Pour choisir les mesures de temps consommé dans les commandes"),
        statut="d",
        min=1,
        max=1,
        NIVE_DETAIL=SIMP(
            fr=tr("niveau de détail des impressions"),
            statut="f",
            typ="I",
            into=(0, 1, 2, 3),
            defaut=1,
        ),
        # 0 : rien
        # 1 : impression en fin de commande des mesures principales
        # 2 : impression en fin de commande des mesures principales et secondaires
        # 3 : impression des mesures principales et secondaires pour chaque pas de temps
        MOYENNE=SIMP(
            fr=tr("affichage des moyennes et écart-types en parallèle"),
            statut="f",
            typ="TXM",
            into=("OUI", "NON"),
            defaut="NON",
        ),
    ),
    MEMOIRE=FACT(
        fr=tr("mode de gestion mémoire utilisé"),
        statut="d",
        min=1,
        max=1,
        TAILLE_BLOC=SIMP(statut="f", typ="R", defaut=800.0),
        TAILLE_GROUP_ELEM=SIMP(statut="f", typ="I", defaut=1000),
    ),
    RESERVE_CPU=FACT(
        fr=tr("reserve de temps pour terminer une execution"),
        statut="d",
        max=1,
        regles=(EXCLUS("VALE", "POURCENTAGE"),),
        VALE=SIMP(statut="f", typ="I", val_min=0),
        #                            valeur par défaut fixée à 10. dans le FORTRAN si CODE présent
        POURCENTAGE=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0),
        #                           valeur par défaut fixée à 10% dans le FORTRAN
        BORNE=SIMP(statut="f", typ="I", val_min=0, defaut=900),
    ),
    #          valeur en pourcentage du temps maximum bornée à 900 secondes
    CODE=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="NON",
        fr=tr("paramètre réservé aux cas-tests"),
    ),
    IGNORE_ALARM=SIMP(
        statut="f",
        typ="TXM",
        max="**",
        fr=tr("Alarmes que l'utilisateur souhaite délibérément ignorer"),
    ),
    LANG=SIMP(
        statut="f",
        typ="TXM",
        fr=tr("Permet de choisir la langue utilisée pour les messages (si disponible)"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
