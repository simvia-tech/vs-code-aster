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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_table_prod(self, TABLE, ACTION, TYPE_TABLE, **kargs):
    """Typage du concept produit."""
    if kargs.get("__all__"):
        return (table_sdaster, table_container, table_fonction)

    if TYPE_TABLE is None:
        l_typ = [AsType(TABLE)]
        for mcf in ACTION:
            if mcf.get("TABLE") is not None:
                l_typ.append(AsType(mcf["TABLE"]))
        # une table_fonction étant une table
        if table_fonction in l_typ:
            return table_fonction
        elif table_container in l_typ:
            return table_container
        else:
            return table_sdaster
    else:
        if TYPE_TABLE == "TABLE_FONCTION":
            return table_fonction
        elif TYPE_TABLE == "TABLE_CONTAINER":
            return table_container
        else:
            return table_sdaster


CALC_TABLE = MACRO(
    nom="CALC_TABLE",
    op=OPS("code_aster.MacroCommands.calc_table_ops.calc_table_ops"),
    sd_prod=calc_table_prod,
    fr=tr("Opérations sur une table"),
    reentrant="f:TABLE",
    reuse=SIMP(statut="c", typ=CO),
    TABLE=SIMP(statut="o", typ=table_sdaster),
    ACTION=FACT(
        statut="o",
        max="**",
        fr=tr("Suite des opérations à effectuer sur la table"),
        OPERATION=SIMP(
            statut="o",
            typ="TXM",
            into=(
                "FILTRE",
                "EXTR",
                "RENOMME",
                "TRI",
                "COMB",
                "AJOUT_LIGNE",
                "OPER",
                "SUPPRIME",
                "UNIQUE",
                "AJOUT_COLONNE",
                "STATISTIQUES",
                "CALCUL",
            ),
        ),
        b_filtre=BLOC(
            condition="""equal_to("OPERATION", 'FILTRE')""",
            fr=tr("Sélectionne les lignes de la table vérifiant un critère"),
            NOM_PARA=SIMP(statut="o", typ="TXM"),
            CRIT_COMP=SIMP(
                statut="f",
                typ="TXM",
                defaut="EQ",
                into=(
                    "EQ",
                    "NE",
                    "GT",
                    "LT",
                    "GE",
                    "LE",
                    "REGEXP",
                    "VIDE",
                    "NON_VIDE",
                    "MAXI",
                    "MAXI_ABS",
                    "MINI",
                    "MINI_ABS",
                ),
            ),
            b_vale=BLOC(
                condition="""(is_in("CRIT_COMP", ('EQ','NE','GT','LT','GE','LE')))""",
                regles=(UN_PARMI("VALE", "VALE_I", "VALE_K", "VALE_C"),),
                VALE=SIMP(statut="f", typ="R", max="**"),
                VALE_I=SIMP(statut="f", typ="I", max="**"),
                VALE_C=SIMP(statut="f", typ="C", max="**"),
                VALE_K=SIMP(statut="f", typ="TXM", max="**"),
            ),
            b_regexp=BLOC(
                condition="""equal_to("CRIT_COMP", 'REGEXP')""", VALE_K=SIMP(statut="o", typ="TXM")
            ),
            b_crit=BLOC(
                condition="""is_in("CRIT_COMP", ('EQ','NE'))""",
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
            ),
        ),
        b_extr=BLOC(
            condition="""equal_to("OPERATION", 'EXTR')""",
            fr=tr("Extrait une ou plusieurs colonnes de la table"),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max="**",
                fr=tr("Noms des colonnes à extraire"),
            ),
        ),
        b_suppr=BLOC(
            condition="""equal_to("OPERATION", 'SUPPRIME')""",
            fr=tr("Supprime une ou plusieurs colonnes de la table"),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max="**",
                fr=tr("Noms des colonnes à supprimer"),
            ),
        ),
        b_supdbl=BLOC(
            condition="""equal_to("OPERATION", 'UNIQUE')""",
            fr=tr("Supprime les lignes si les valeurs des paramètres " "ont déjà été vues."),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max="**",
                fr=tr("Noms des paramètres à tester pour supprimer les lignes"),
            ),
            FORMAT_R=SIMP(statut="f", typ="TXM"),
        ),
        b_renomme=BLOC(
            condition="""equal_to("OPERATION", 'RENOMME')""",
            fr=tr("Renomme un ou plusieurs paramètres de la table"),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                min=2,
                max=2,
                fr=tr("Couple (ancien nom du paramètre, nouveau nom du paramètre)"),
            ),
        ),
        b_tri=BLOC(
            condition="""equal_to("OPERATION", 'TRI')""",
            fr=tr("Ordonne les lignes de la table selon les valeurs d'un ou plusieurs paramètres"),
            NOM_PARA=SIMP(statut="o", typ="TXM", validators=NoRepeat(), max="**"),
            ORDRE=SIMP(
                statut="f", typ="TXM", defaut="CROISSANT", into=("CROISSANT", "DECROISSANT")
            ),
        ),
        b_comb=BLOC(
            condition="""equal_to("OPERATION", 'COMB')""",
            fr=tr("Combine deux tables ayant éventuellement des paramètres communs"),
            TABLE=SIMP(
                statut="o",
                typ=table_sdaster,
                fr=tr("Table dont les colonnes vont venir surcharger la table initiale"),
            ),
            NOM_PARA=SIMP(
                statut="f",
                typ="TXM",
                max="**",
                fr=tr(
                    "Noms des paramètres dont les valeurs doivent etre identiques dans les deux tables "
                    "pour que les colonnes soient combinées"
                ),
            ),
            RESTREINT=SIMP(
                statut="f",
                typ="TXM",
                into=("OUI", "NON"),
                defaut="NON",
                fr=tr("Restreint la fusion uniquement aux lignes où les NOM_PARA sont communs"),
            ),
            FORMAT_R=SIMP(statut="f", typ="TXM"),
        ),
        b_ajout_lig=BLOC(
            condition="""equal_to("OPERATION", 'AJOUT_LIGNE')""",
            fr=tr("Ajoute une ligne à la table initiale"),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                max="**",
                fr=tr("Noms des paramètres dont les valeurs sont fournies sous VALE"),
            ),
            VALE=SIMP(statut="o", typ=not_checked, max="**", fr=tr("Valeurs des paramètres")),
        ),
        b_ajout_col=BLOC(
            condition="""equal_to("OPERATION", 'AJOUT_COLONNE')""",
            regles=(UN_PARMI("VALE", "VALE_COLONNE"),),
            fr=tr("Ajoute une colonne constante à la table initiale"),
            NOM_PARA=SIMP(
                statut="o", typ="TXM", max="**", fr=tr("Noms des paramètres des colonnes à ajouter")
            ),
            VALE=SIMP(
                statut="f", typ=not_checked, max="**", fr=tr("Valeur constante pour chaque colonne")
            ),
            VALE_COLONNE=SIMP(
                statut="f",
                typ=not_checked,
                max="**",
                fr=tr("Valeur de la colonne pour chaque ligne"),
            ),
        ),
        b_oper=BLOC(
            condition="""equal_to("OPERATION", 'OPER')""",
            fr=tr(
                "Applique une formule dans laquelle les variables sont les paramètres de la table"
            ),
            FORMULE=SIMP(
                statut="o", typ=formule, fr=tr("Formule à appliquer aux colonnes de la table")
            ),
            NOM_PARA=SIMP(statut="o", typ="TXM", fr=tr("Nom de la nouvelle colonne")),
            NOM_COLONNE=SIMP(
                statut="f",
                typ="TXM",
                max="**",
                fr=tr("Nom des colonnes à utiliser en tant que paramètres de la formule"),
            ),
        ),
        b_calcul=BLOC(
            condition="""equal_to("OPERATION", 'CALCUL')""",
            fr=tr("Appliquer des calculs simples sur des colonnes de la table"),
            NOM_PARA=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max="**",
                fr=tr("Nom des colonnes à calculer"),
            ),
            TYPE_CALCUL=SIMP(
                statut="o",
                typ="TXM",
                validators=NoRepeat(),
                max="**",
                into=("MAXI", "MINI", "SOMM", "MOY", "MAXI_ABS", "MINI_ABS", "SOMM_ABS"),
                fr=tr("Type des calculs à appliquer"),
            ),
        ),
    ),
    TYPE_TABLE=SIMP(statut="c", typ="TXM", into=("TABLE", "TABLE_FONCTION", "TABLE_CONTAINER")),
    TITRE=SIMP(statut="f", typ="TXM", fr=tr("Titre de la table produite")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
