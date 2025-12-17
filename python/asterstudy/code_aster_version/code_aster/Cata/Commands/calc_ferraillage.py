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


def calc_ferraillage_prod(RESULTAT, **args):
    if args.get("__all__"):
        return (evol_elas, evol_noli, dyna_trans, mult_elas)

    if AsType(RESULTAT) is not None:
        return AsType(RESULTAT)
    raise AsException("type de concept resultat non prevu")


CALC_FERRAILLAGE = OPER(
    nom="CALC_FERRAILLAGE",
    op=175,
    sd_prod=calc_ferraillage_prod,
    reentrant="o:RESULTAT",
    fr=tr("calcul de cartes de densité de ferraillage "),
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli, dyna_trans, mult_elas)),
    CARA_ELEM=SIMP(statut="o", typ=cara_elem),
    #
    # ====
    # Sélection des numéros d'ordre pour lesquels on fait le calcul :
    # ====
    #
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    #    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    #    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    b_acce_reel=BLOC(
        condition="""(exists("FREQ"))or(exists("LIST_FREQ"))or(exists("INST"))or(exists("LIST_INST"))""",
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    #
    # ====
    # Définition des grandeurs caractéristiques
    # ====
    #
    TYPE_COMB=SIMP(statut="o", typ="TXM", into=("ELU", "ELS", "ELS_QP")),
    CODIFICATION=SIMP(statut="f", typ="TXM", defaut="EC2", into=("BAEL91", "EC2")),
    METHODE_2D=SIMP(
        statut="f",
        typ="TXM",
        defaut="CAPRA-MAURY",
        into=("CAPRA-MAURY", "SANDWICH"),
        fr=tr("Choix de l'algorithme de calcul 2D"),
    ),
    PAS_THETA=SIMP(
        statut="f",
        typ="R",
        defaut=5,
        fr=(
            "Angle d'itération en degrés pour la recherche de la configuration d'équilibre pour le calcul 2D - Pour CapraMaury, il s'agit de l'orientation des facettes ; pour Sandwich, il s'agit de l'inclinaison des bielles de compression"
        ),
    ),
    PAS_EPAI=SIMP(
        statut="f",
        typ="R",
        defaut=0.01,
        fr=(
            "Pas d'itération en pourcentage de la hauteur de la section, pour la recherche de la configuration optimale"
        ),
    ),
    PAS_SIGM=SIMP(
        statut="f",
        typ="R",
        defaut=0.1,
        fr=(
            "SANDWICH : Pas d'itération pour la recherche du ratio optimal des contraintes principales de compression dans le béton"
        ),
    ),
    COND_109=SIMP(
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
        defaut="OUI",
        fr=(
            "SANDWICH : Prise en compte de la clause §6.109-Éléments de membrane de l’EN-1992-2 pour le calcul de la résistance des bielles de compression du béton"
        ),
    ),
    UNITE_CONTRAINTE=SIMP(
        statut="o", typ="TXM", into=("MPa", "Pa"), fr=tr("Unité des contraintes du problème")
    ),
    UNITE_DIMENSION=SIMP(
        statut="o", typ="TXM", into=("mm", "m"), fr=tr("Unité des dimensions du problème")
    ),
    b_BAEL91=BLOC(
        condition=""" equal_to("CODIFICATION", 'BAEL91')""",
        fr=tr("utilisation du BAEL91"),
        #          mot clé facteur répétable pour assigner les caractéristiques locales par zones topologiques (GROUP_MA)
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("TOUT", "GROUP_MA"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            TYPE_STRUCTURE=SIMP(
                statut="o", typ="TXM", into=("1D", "2D"), fr=tr("Type de Structure 1D ou 2D")
            ),
            FERR_SYME=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr("Ferraillage symétrique?"),
            ),
            SEUIL_SYME=SIMP(
                statut="f",
                typ="R",
                fr=tr("Seuil de tolérance pour le calcul d'un ferraillage symétrique"),
            ),
            FERR_COMP=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr("Ferraillage de compression possible?"),
            ),
            EPURE_CISA=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr(
                    "Prise en compte de l'effort de traction supplémentaire du à l'effort tranchant et à la torsion?"
                ),
            ),
            FERR_MIN=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("NON", "OUI", "CODE"),
                fr=tr("Prise en compte d'un ferraillage minimal?"),
            ),
            RHO_LONGI_MIN=SIMP(
                statut="f", typ="R", fr=tr("Ratio de ferraillage longitudinal minimal en %")
            ),
            RHO_TRNSV_MIN=SIMP(
                statut="f", typ="R", fr=tr("Ratio de ferraillage transversal minimal en %")
            ),
            c_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr("définition des enrobages de la section 2D"),
                C_INF=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures pour la section 2D"),
                ),
                C_SUP=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures pour la section 2D"),
                ),
            ),
            c_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr("définition des enrobages de la section 1D"),
                C_INF_Y=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures suivant l'axe Y de la section 1D"),
                ),
                C_SUP_Y=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures suivant l'axe Y de la section 1D"),
                ),
                C_INF_Z=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures suivant l'axe Z de la section 1D"),
                ),
                C_SUP_Z=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures suivant l'axe Z de la section 1D"),
                ),
            ),
            N=SIMP(
                statut="f", typ="R", fr=tr("Coefficient d'équivalence acier/béton (ELS,ELS_QP)")
            ),
            FE=SIMP(statut="f", typ="R", fr=tr("Contrainte admissible dans l'acier")),
            FCJ=SIMP(statut="f", typ="R", fr=tr("Contrainte admissible dans le béton")),
            SIGS_ELS=SIMP(
                statut="f",
                typ="R",
                fr=tr("Contrainte ultime de dimensionnement des aciers à l'ELS"),
            ),
            sigc_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr(
                    "définition des contraintes ultimes de dimensionnement du béton de la section 2D"
                ),
                SIGC_INF_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure pour la section 2D (ELS)"
                    ),
                ),
                SIGC_SUP_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure pour la section 2D (ELS)"
                    ),
                ),
            ),
            sigc_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr(
                    "définition des contraintes ultimes de dimensionnement du béton de la section 1D"
                ),
                SIGC_INF_Y_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure suivant l'axe Y de la section 1D (ELS)"
                    ),
                ),
                SIGC_SUP_Y_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure suivant l'axe Y de la section 1D (ELS)"
                    ),
                ),
                SIGC_INF_Z_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure suivant l'axe Z de la section 1D (ELS)"
                    ),
                ),
                SIGC_SUP_Z_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure suivant l'axe Z de la section 1D (ELS)"
                    ),
                ),
            ),
            wmax_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr("définition des ouvertures des fissures maximales de la section 2D"),
                WMAX_INF=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure de la section 2D (ELS_QP)"
                    ),
                ),
                WMAX_SUP=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure de la section 2D (ELS_QP)"
                    ),
                ),
            ),
            wmax_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr("définition des ouvertures des fissures maximales de la section 1D"),
                WMAX_INF_Y=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure suivant l'axe Y de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_SUP_Y=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure suivant l'axe Y de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_INF_Z=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure suivant l'axe Z de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_SUP_Z=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure suivant l'axe Z de la section 1D (ELS_QP)"
                    ),
                ),
            ),
            SIGC_ELS_QP=SIMP(
                statut="f", typ="R", fr=tr("Contrainte ultime de dimensionnement du béton (ELS_QP)")
            ),
            KT=SIMP(statut="f", typ="R", fr=tr("Coefficient de durée de chargement (ELS_QP)")),
            PHI_INF_X=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe X (ELS_QP)"),
            ),
            PHI_SUP_X=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe X (ELS_QP)"),
            ),
            PHI_INF_Y=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe Y (ELS_QP)"),
            ),
            PHI_SUP_Y=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe Y (ELS_QP)"),
            ),
            PHI_INF_Z=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe Z (ELS_QP)"),
            ),
            PHI_SUP_Z=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe Z (ELS_QP)"),
            ),
            EYS=SIMP(statut="f", typ="R", fr=tr("Module d'Young de l'acier")),
            TYPE_DIAGRAMME=SIMP(
                statut="f",
                typ="TXM",
                defaut="B2",
                into=("B1", "B2"),
                fr=tr(
                    "Type du diagramme Contrainte-Deformation à utiliser: B1 (Incliné) ou B2 (Horizontal)"
                ),
            ),
            RHO_ACIER=SIMP(statut="f", typ="R", defaut=-1, fr=tr("Densité volumique des aciers")),
            b_iconst=BLOC(
                condition=""" greater_than("RHO_ACIER", 0)""",
                fr=tr("Calcul du critère de difficulté de bétonnage si RHO_ACIER > 0"),
                ALPHA_REINF=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de densité d'acier par mètre cube de béton"
                    ),
                ),
                ALPHA_SHEAR=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de densité d'acier d'effort tranchant"
                    ),
                ),
                ALPHA_STIRRUPS=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de longueur des épingles d'acier effort tranchant"
                    ),
                ),
                RHO_CRIT=SIMP(
                    statut="f", typ="R", defaut=150, fr=tr("Densité volumique d'armature critique")
                ),
                DNSTRA_CRIT=SIMP(
                    statut="f",
                    typ="R",
                    defaut=0.006,
                    fr=tr("Ferraillage d'effort tranchant critique"),
                ),
                L_CRIT=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr("Longueur critique des epingle d'aciers d'effort tranchant"),
                ),
            ),
            GAMMA_S=SIMP(
                statut="f",
                typ="R",
                fr=tr("Coefficient de sécurité sur la résistance de calcul des aciers à l'ELU"),
            ),
            GAMMA_C=SIMP(
                statut="f",
                typ="R",
                fr=tr("Coefficient de sécurité sur la résistance de calcul du béton à l'ELU"),
            ),
            ALPHA_CC=SIMP(
                statut="f",
                typ="R",
                defaut=0.85,
                fr=tr(
                    "Coefficient de sécurité sur la résistance de calcul du béton en compression (ELU)"
                ),
            ),
        ),
    ),
    b_EC2=BLOC(
        condition=""" equal_to("CODIFICATION", 'EC2')""",
        fr=tr("utilisation de l'eurocode 2"),
        #          mot clé facteur répétable pour assigner les caractéristiques locales par zones topologiques (GROUP_MA)
        AFFE=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("TOUT", "GROUP_MA"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            TYPE_STRUCTURE=SIMP(
                statut="o", typ="TXM", into=("1D", "2D"), fr=tr("Type de Structure 1D ou 2D")
            ),
            FERR_SYME=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr("Ferraillage symétrique?"),
            ),
            SEUIL_SYME=SIMP(
                statut="f",
                typ="R",
                fr=tr("Seuil de tolérance pour le calcul d'un ferraillage symétrique"),
            ),
            FERR_COMP=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr("Ferraillage de compression possible?"),
            ),
            EPURE_CISA=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr(
                    "Prise en compte de l'effort de traction supplémentaire du à l'effort tranchant et à la torsion?"
                ),
            ),
            FERR_MIN=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("NON", "OUI", "CODE"),
                fr=tr("Prise en compte d'un ferraillage minimal?"),
            ),
            RHO_LONGI_MIN=SIMP(
                statut="f", typ="R", fr=tr("Ratio de ferraillage longitudinal minimal en %")
            ),
            RHO_TRNSV_MIN=SIMP(
                statut="f", typ="R", fr=tr("Ratio de ferraillage transversal minimal en %")
            ),
            c_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr("définition des enrobages de la section 2D"),
                C_INF=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures pour la section 2D"),
                ),
                C_SUP=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures pour la section 2D"),
                ),
            ),
            c_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr("définition des enrobages de la section 1D"),
                C_INF_Y=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures suivant l'axe Y de la section 1D"),
                ),
                C_SUP_Y=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures suivant l'axe Y de la section 1D"),
                ),
                C_INF_Z=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures inférieures suivant l'axe Z de la section 1D"),
                ),
                C_SUP_Z=SIMP(
                    statut="o",
                    typ="R",
                    fr=tr("Enrobage des armatures supérieures suivant l'axe Z de la section 1D"),
                ),
            ),
            ALPHA_E=SIMP(
                statut="f", typ="R", fr=tr("Coefficient d'équivalence acier/béton (ELS, ELS_QP)")
            ),
            FYK=SIMP(
                statut="f", typ="R", fr=tr("Limite d'élasticité caractéristique dans l'acier")
            ),
            FCK=SIMP(
                statut="f",
                typ="R",
                fr=tr("Résistance caractéristique du béton en compression à 28 jours"),
            ),
            SIGS_ELS=SIMP(
                statut="f", typ="R", fr=tr("Contrainte ultime de dimensionnement des aciers (ELS)")
            ),
            sigc_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr(
                    "définition des contraintes ultimes de dimensionnement du béton de la section 2D"
                ),
                SIGC_INF_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure pour la section 2D (ELS)"
                    ),
                ),
                SIGC_SUP_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure pour la section 2D (ELS)"
                    ),
                ),
            ),
            sigc_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr(
                    "définition des contraintes ultimes de dimensionnement du béton de la section 1D"
                ),
                SIGC_INF_Y_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure suivant l'axe Y de la section 1D (ELS)"
                    ),
                ),
                SIGC_SUP_Y_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure suivant l'axe Y de la section 1D (ELS)"
                    ),
                ),
                SIGC_INF_Z_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre inférieure suivant l'axe Z de la section 1D (ELS)"
                    ),
                ),
                SIGC_SUP_Z_ELS=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Contrainte ultime de dimensionnement du béton en fibre supérieure suivant l'axe Z de la section 1D (ELS)"
                    ),
                ),
            ),
            wmax_2D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '2D')""",
                fr=tr("définition des ouvertures des fissures maximales de la section 2D"),
                WMAX_INF=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure de la section 2D (ELS_QP)"
                    ),
                ),
                WMAX_SUP=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure de la section 2D (ELS_QP)"
                    ),
                ),
            ),
            wmax_1D=BLOC(
                condition=""" equal_to("TYPE_STRUCTURE", '1D')""",
                fr=tr("définition des ouvertures des fissures maximales de la section 1D"),
                WMAX_INF_Y=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure suivant l'axe Y de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_SUP_Y=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure suivant l'axe Y de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_INF_Z=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face inférieure suivant l'axe Z de la section 1D (ELS_QP)"
                    ),
                ),
                WMAX_SUP_Z=SIMP(
                    statut="f",
                    typ="R",
                    fr=tr(
                        "Ouverture maximale des fissures en face supérieure suivant l'axe Z de la section 1D (ELS_QP)"
                    ),
                ),
            ),
            SIGC_ELS_QP=SIMP(
                statut="f", typ="R", fr=tr("Contrainte ultime de dimensionnement du béton (ELS_QP)")
            ),
            KT=SIMP(statut="f", typ="R", fr=tr("Coefficient de durée de chargement (ELS_QP)")),
            PHI_INF_X=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe X (ELS_QP)"),
            ),
            PHI_SUP_X=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe X (ELS_QP)"),
            ),
            PHI_INF_Y=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe Y (ELS_QP)"),
            ),
            PHI_SUP_Y=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe Y (ELS_QP)"),
            ),
            PHI_INF_Z=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures inférieures suivant l'axe Z (ELS_QP)"),
            ),
            PHI_SUP_Z=SIMP(
                statut="f",
                typ="R",
                fr=tr("Diamètre approximatif des armatures supérieures suivant l'axe Z (ELS_QP)"),
            ),
            UTIL_COMPR=SIMP(
                statut="f",
                typ="TXM",
                defaut="NON",
                into=("OUI", "NON"),
                fr=tr("Prise en compte de la compression pour les aciers transversaux"),
            ),
            CLASSE_ACIER=SIMP(
                statut="f",
                typ="TXM",
                defaut="B",
                into=("A", "B", "C"),
                fr=tr("Classe de ductilité des aciers"),
            ),
            EYS=SIMP(statut="f", typ="R", fr=tr("Module d'Young de l'acier")),
            TYPE_DIAGRAMME=SIMP(
                statut="f",
                typ="TXM",
                defaut="B2",
                into=("B1", "B2"),
                fr=tr(
                    "Type du diagramme Contrainte-Deformation à utiliser: B1 (Incliné) ou B2 (Horizontal)"
                ),
            ),
            RHO_ACIER=SIMP(statut="f", typ="R", defaut=-1, fr=tr("Densité volumique des aciers")),
            b_iconst=BLOC(
                condition=""" greater_than("RHO_ACIER", 0)""",
                fr=tr("Calcul du critère de difficulté de bétonnage si RHO_ACIER > 0"),
                ALPHA_REINF=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de densité d'acier par mètre cube de béton"
                    ),
                ),
                ALPHA_SHEAR=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de densité d'acier d'effort tranchant"
                    ),
                ),
                ALPHA_STIRRUPS=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr(
                        "Coefficient de pondération du ratio de longueur des épingles d'acier effort tranchant"
                    ),
                ),
                RHO_CRIT=SIMP(
                    statut="f", typ="R", defaut=150, fr=tr("Densité volumique d'armature critique")
                ),
                DNSTRA_CRIT=SIMP(
                    statut="f",
                    typ="R",
                    defaut=0.006,
                    fr=tr("Ferraillage d'effort tranchant critique"),
                ),
                L_CRIT=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1,
                    fr=tr("Longueur critique des epingle d'aciers d'effort tranchant"),
                ),
            ),
            GAMMA_S=SIMP(
                statut="f",
                typ="R",
                fr=tr("Coefficient de sécurité sur la résistance de calcul des aciers à l'ELU"),
            ),
            GAMMA_C=SIMP(
                statut="f",
                typ="R",
                fr=tr("Coefficient de sécurité sur la résistance de calcul du béton à l'ELU"),
            ),
            ALPHA_CC=SIMP(
                statut="f",
                typ="R",
                defaut=0.85,
                fr=tr(
                    "Coefficient de sécurité sur la résistance de calcul du béton en compression (ELU)"
                ),
            ),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)

##############################################################################################################
# Remarques :
# -----------
#     l'épaisseur des coques sera récupérée automatiquemen tvia le cara_elem sous-jacent au résultat

#     Le résultat produit est un champ constant par éléments associé à la grandeur FER2_R
#     qui comporte les composantes :
#        DNSXI    densité d'acier de flexion suivant X, peau inf
#        DNSXS    densité d'acier de flexion suivant X, peau sup
#        DNSYI    densité d'acier de flexion suivant Y, peau inf
#        DNSYS    densité d'acier de flexion suivant Y, peau sup
#        DNST     densité d'acier d'effort tranchant
#        DNSVOL   densité volumique totalte d'acier
#        CONSTRUC critère de constructibilité

#     Arrêt en erreur si:
#        - EFGE_ELNO n'a pas été précédemment calculé et n'est donc pas présent dans la structure de données RESULTAT
