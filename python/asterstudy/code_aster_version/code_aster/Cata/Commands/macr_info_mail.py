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

MACR_INFO_MAIL = MACRO(
    nom="MACR_INFO_MAIL",
    op=OPS("code_aster.MacroCommands.macr_adap_mail_ops.macr_adap_mail_ops"),
    docu="U7.03.02",
    fr=tr("Donner des informations sur un maillage."),
    #
    # 1. Le niveau d'information
    #
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2, 3, 4)),
    #
    # 2. Le nom du maillage a analyser
    #
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster, fr=tr("Maillage à analyser.")),
    #
    # 3. Suivi d'une frontiere
    #
    MAILLAGE_FRONTIERE=SIMP(
        statut="f", typ=maillage_sdaster, fr=tr("Maillage de la frontiere à suivre")
    ),
    #
    b_frontiere=BLOC(
        condition=""" exists("MAILLAGE_FRONTIERE") """,
        fr=tr("Information complémentaire sur la frontière"),
        #
        GROUP_MA_FRONT=SIMP(
            statut="f",
            typ=grma,
            validators=NoRepeat(),
            max="**",
            fr=tr("Groupes de mailles définissant la frontière"),
        ),
        #
    ),
    #
    # 4. Les options ; par defaut, on controle tout, sauf l'interpénétration
    # 4.1. Nombre de noeuds et mailles
    #
    NOMBRE=SIMP(
        statut="f",
        typ="TXM",
        defaut="OUI",
        into=("OUI", "NON"),
        fr=tr("Nombre de noeuds et de mailles du maillage"),
    ),
    #
    # 4.2. Determination de la qualite des mailles du maillage
    #
    QUALITE=SIMP(
        statut="f",
        typ="TXM",
        defaut="OUI",
        into=("OUI", "NON"),
        fr=tr("Qualité des mailles du maillage."),
    ),
    #
    # 4.3. Connexite du maillage
    #
    CONNEXITE=SIMP(
        statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON"), fr=tr("Connexité du maillage.")
    ),
    #
    # 4.4. Taille des sous-domaines du maillage
    #
    TAILLE=SIMP(
        statut="f",
        typ="TXM",
        defaut="OUI",
        into=("OUI", "NON"),
        fr=tr("Tailles des sous-domaines du maillage."),
    ),
    #
    # 4.5. Controle de la non-interpénétration des mailles
    #
    INTERPENETRATION=SIMP(
        statut="f",
        typ="TXM",
        defaut="NON",
        into=("OUI", "NON"),
        fr=tr("Controle de la non interpénétration des mailles."),
    ),
    #
    # 4.6. Propriétés du maillage de calcul
    #
    PROP_CALCUL=SIMP(
        statut="f",
        typ="TXM",
        defaut="OUI",
        into=("OUI", "NON"),
        fr=tr("Propriétés du maillage de calcul."),
    ),
    #
    # 4.7. Determination des diametres des mailles du maillage
    #
    DIAMETRE=SIMP(
        statut="f",
        typ="TXM",
        defaut="OUI",
        into=("OUI", "NON"),
        fr=tr("Diamètre des mailles du maillage."),
    ),
    #
    # 5. Les options avancées
    # 5.1. Langue des messages issus de HOMARD
    #
    LANGUE=SIMP(
        statut="f",
        typ="TXM",
        defaut="FRANCAIS",
        into=("FRANCAIS", "FRENCH", "ANGLAIS", "ENGLISH"),
        fr=tr("Langue des messages issus de HOMARD."),
    ),
    #
    # 5.2. Gestion des mailles acceptees dans le maillage initial
    #       "HOMARD" : exclusivement les mailles pouvant etre decoupees (defaut)
    #       "IGNORE_PYRA" : elles sont ignorées
    #
    ELEMENTS_ACCEPTES=SIMP(
        statut="f",
        typ="TXM",
        defaut="HOMARD",
        into=("HOMARD", "IGNORE_PYRA"),
        fr=tr("Acceptation des mailles dans le maillage initial"),
    ),
    #
    # 5.3. Version de HOMARD
    #
    VERSION_HOMARD=SIMP(
        statut="f",
        typ="TXM",
        defaut="V11_10",
        into=("V11_10", "V11_N", "V11_N_PERSO"),
        fr=tr("Version de HOMARD"),
    ),
    #
    # 5.4. Exécutable pilotant HOMARD
    #
    LOGICIEL=SIMP(statut="f", typ="TXM", fr=tr("Logiciel pilotant HOMARD")),
    #
    # 5.5. Unite logique d'un fichier à ajouter a HOMARD.Configuration
    #
    b_unite=BLOC(
        condition="""is_in("VERSION_HOMARD", ('V11_N','V11_N_PERSO'))""",
        fr=tr("Fichier supplementaire."),
        #
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            inout="in",
            fr=tr("Unite logique a ajouter a HOMARD.Configuration"),
        ),
        #
    ),
    #
)
