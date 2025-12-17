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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_FONCTION = MACRO(
    nom="IMPR_FONCTION",
    op=OPS("code_aster.MacroCommands.impr_fonction_ops.impr_fonction_ops"),
    sd_prod=None,
    fr=tr(
        "Imprime le contenu d'objets de type fonction ou liste de "
        "réels dans un fichier destiné à un traceur de courbe"
    ),
    FORMAT=SIMP(
        statut="f",
        typ="TXM",
        defaut="TABLEAU",
        into=("TABLEAU", "AGRAF", "XMGRACE", "LISS_ENVELOP"),
    ),
    b_pilote=BLOC(
        condition="""equal_to("FORMAT", 'XMGRACE')""",
        fr=tr("Mots-clés propres à XMGRACE"),
        PILOTE=SIMP(
            statut="f",
            typ="TXM",
            defaut="",
            into=(
                "",
                "POSTSCRIPT",
                "EPS",
                "MIF",
                "SVG",
                "PNM",
                "PNG",
                "JPEG",
                "PDF",
                "INTERACTIF",
                "INTERACTIF_BG",
            ),
            fr=tr(
                "Pilote de sortie, PNG/JPEG/PDF ne sont pas disponibles sur toutes les installations de xmgrace"
            ),
        ),
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            defaut=29,
            inout="out",
            fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
        ),
    ),
    b_agraf=BLOC(
        condition="""equal_to("FORMAT", 'AGRAF')""",
        fr=tr("Mots-clés propres à AGRAF"),
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            defaut=25,
            inout="out",
            fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
        ),
        UNITE_DIGR=SIMP(
            statut="f",
            typ=UnitType(),
            defaut=26,
            inout="out",
            fr=tr("Unité logique définissant le fichier dans lequel on écrit les directives Agraf"),
        ),
    ),
    # unite pour TABLEAU dans le bloc de mise en forme spécifique
    b_format1=BLOC(
        condition="""not equal_to("FORMAT", 'LISS_ENVELOP')""",
        COURBE=FACT(
            statut="o",
            max="**",
            fr=tr("Définition de la fonction à tracer"),
            regles=(UN_PARMI("FONCTION", "LIST_RESU", "FONC_X", "ABSCISSE"),),
            FONCTION=SIMP(
                statut="f",
                typ=(fonction_sdaster, formule, fonction_c, nappe_sdaster),
                fr=tr("Fonction réelle ou complexe"),
            ),
            LIST_RESU=SIMP(
                statut="f",
                typ=listr8_sdaster,
                fr=tr("Liste des ordonnees d'une fonction réelle définie par deux listes"),
            ),
            FONC_X=SIMP(
                statut="f",
                typ=(fonction_sdaster, formule),
                fr=tr("Fonction abscisses d'une fonction paramétrique"),
            ),
            ABSCISSE=SIMP(statut="f", typ="R", max="**", fr=tr("Valeurs des abscisses")),
            b_fonction=BLOC(
                condition="""exists("FONCTION")""", LIST_PARA=SIMP(statut="f", typ=listr8_sdaster)
            ),
            b_fonction_c=BLOC(
                condition="""is_type("FONCTION") in (fonction_c, formule_c)""",
                fr=tr("Fonction complexe définie par le mot-clé fonction"),
                PARTIE=SIMP(statut="f", typ="TXM", into=("REEL", "IMAG")),
            ),
            b_list_resu=BLOC(
                condition="""exists("LIST_RESU")""", LIST_PARA=SIMP(statut="o", typ=listr8_sdaster)
            ),
            b_fonc_x=BLOC(
                condition="""exists("FONC_X")""",
                FONC_Y=SIMP(
                    statut="o",
                    typ=(fonction_sdaster, formule),
                    fr=tr("Fonction ordonnées d une fonction paramétrique"),
                ),
                LIST_PARA=SIMP(statut="f", typ=listr8_sdaster),
            ),
            b_vale_resu=BLOC(
                condition="""exists("ABSCISSE")""",
                ORDONNEE=SIMP(statut="o", typ="R", max="**", fr=tr("Valeurs des ordonnées")),
            ),
            # mots-clés utilisant uniquement aux formats autres que TABLEAU
            # mais ce serait trop pénible de devoir les supprimer quand on change de format
            # donc on ne les met pas dans un bloc
            # "pseudo" bloc mise en forme :
            LEGENDE=SIMP(statut="f", typ="TXM", fr=tr("Légende associée à la fonction")),
            STYLE=SIMP(
                statut="f", typ="I", val_min=0, fr=tr("Style de la ligne représentant la fonction")
            ),
            COULEUR=SIMP(statut="f", typ="I", val_min=0, fr=tr("Couleur associée à la fonction")),
            MARQUEUR=SIMP(
                statut="f", typ="I", val_min=0, fr=tr("Type du marqueur associé à la fonction")
            ),
            FREQ_MARQUEUR=SIMP(
                statut="f",
                typ="I",
                defaut=0,
                fr=tr("Fréquence d impression du marqueur associé à la fonction"),
            ),
            # fin bloc mise en forme
            TRI=SIMP(
                statut="f",
                typ="TXM",
                defaut="N",
                fr=tr("Choix du tri effectué sur les abscisses ou sur les ordonnées"),
                into=("N", "X", "Y", "XY", "YX"),
            ),
        ),
    ),
    b_format2=BLOC(
        condition="""equal_to("FORMAT", 'LISS_ENVELOP')""",
        COURBE=FACT(
            statut="o",
            max="**",
            fr=tr("Définition de la fonction à tracer"),
            regles=(UN_PARMI("NAPPE", "NAPPE_LISSEE"),),
            NAPPE=SIMP(statut="f", typ=(nappe_sdaster), fr=tr("Nappe aster")),
            NAPPE_LISSEE=SIMP(
                statut="f",
                typ=(nappe_sdaster),
                fr=tr("Nappe aster issue de CALC_FONCTION/LISS_ENVELOP"),
            ),
        ),
    ),
    # Mise en page du tableau ou du graphique
    b_tableau=BLOC(
        condition="""equal_to("FORMAT", 'TABLEAU')""",
        fr=tr("Mots-clés propres au format Tableau"),
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            defaut=8,
            inout="out",
            fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
        ),
        TITRE=SIMP(statut="f", typ="TXM", fr=tr("Titre associé au graphique")),
        SOUS_TITRE=SIMP(statut="f", typ="TXM", fr=tr("Sous-titre du graphique")),
        SEPARATEUR=SIMP(
            statut="f",
            typ="TXM",
            defaut=" ",
            fr=tr("Séparateur des colonnes du tableau (ex : ' ', ';'...)"),
        ),
        COMMENTAIRE=SIMP(
            statut="f",
            typ="TXM",
            defaut="#",
            fr=tr("Caractère indiquant au traceur de fonction que la ligne peut etre ignorée"),
        ),
        COMM_PARA=SIMP(
            statut="f",
            typ="TXM",
            defaut="",
            fr=tr("Caractère utilisé pour commentariser la ligne des labels de colonnes"),
        ),
        DEBUT_LIGNE=SIMP(statut="f", typ="TXM", defaut="", fr=tr("Caractère de debut de ligne")),
        FIN_LIGNE=SIMP(statut="f", typ="TXM", defaut="\n", fr=tr("Caractère de fin de ligne")),
        FORMAT_R=SIMP(statut="f", typ="TXM", defaut="E12.5", fr=tr("Format des réels")),
    ),
    b_graphique=BLOC(
        condition="""not equal_to("FORMAT", 'TABLEAU')""",
        fr=tr("Mise en page du graphique"),
        TITRE=SIMP(statut="f", typ="TXM", fr=tr("Titre associé au graphique")),
        SOUS_TITRE=SIMP(statut="f", typ="TXM", fr=tr("Sous-titre du graphique")),
        BORNE_X=SIMP(
            statut="f", typ="R", min=2, max=2, fr=tr("Intervalles de variation des abscisses")
        ),
        BORNE_Y=SIMP(
            statut="f", typ="R", min=2, max=2, fr=tr("Intervalles de variation des ordonnées")
        ),
        ECHELLE_X=SIMP(
            statut="f",
            typ="TXM",
            defaut="LIN",
            into=("LIN", "LOG"),
            fr=tr("Type d'échelle pour les abscisses"),
        ),
        ECHELLE_Y=SIMP(
            statut="f",
            typ="TXM",
            defaut="LIN",
            into=("LIN", "LOG"),
            fr=tr("Type d'échelle pour les ordonnées"),
        ),
        GRILLE_X=SIMP(
            statut="f",
            typ="R",
            max=1,
            val_min=0.0,
            val_min_included=False,
            fr=tr("Pas du quadrillage vertical"),
        ),
        GRILLE_Y=SIMP(
            statut="f",
            typ="R",
            max=1,
            val_min=0.0,
            val_min_included=False,
            fr=tr("Pas du quadrillage horizontal"),
        ),
        LEGENDE_X=SIMP(statut="f", typ="TXM", fr=tr("Légende associée à l'axe des abscisses")),
        LEGENDE_Y=SIMP(statut="f", typ="TXM", fr=tr("Légende associée à l'axe des ordonnées")),
    ),
    b_liss_enveloppe=BLOC(
        condition="""equal_to("FORMAT", 'LISS_ENVELOP')""",
        fr=tr("Mots-clés propres au format Liss_Envelop"),
        UNITE=SIMP(
            statut="f",
            typ=UnitType(),
            defaut=25,
            inout="out",
            fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
