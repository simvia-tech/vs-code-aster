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

# person_in_charge: j-pierre.lefebvre at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_JEVEUX = PROC(
    nom="IMPR_JEVEUX",
    op=16,
    fr=tr("Imprimer le contenu des objets créés par JEVEUX (pour développeur)"),
    ENTITE=SIMP(
        fr=tr("choix de l'observation"),
        statut="o",
        typ="TXM",
        into=("DISQUE", "MEMOIRE", "REPERTOIRE", "OBJET", "ATTRIBUT", "SYSTEME", "ENREGISTREMENT"),
    ),
    b_objet=BLOC(
        condition="""(equal_to("ENTITE", 'OBJET'))""",
        NOMOBJ=SIMP(fr=tr("nom d'objet"), statut="f", typ="TXM"),
        NUMOC=SIMP(fr=tr("numéro d objet de collection"), statut="f", typ="I"),
        NOMOC=SIMP(fr=tr("nom d'objet de collection"), statut="f", typ="TXM"),
    ),
    b_attribut=BLOC(
        condition="""(equal_to("ENTITE", 'ATTRIBUT'))""",
        NOMOBJ=SIMP(fr=tr("nom de collection"), statut="f", typ="TXM"),
        NOMATR=SIMP(
            fr=tr("nom d attribut de collection"),
            statut="f",
            typ="TXM",
            into=("$$DESO", "$$IADD", "$$IADM", "$$NOM", "$$LONG", "$$LONO", "$$LUTI", "$$NUM"),
        ),
    ),
    b_systeme=BLOC(
        condition="""(equal_to("ENTITE", 'SYSTEME'))""",
        CLASSE=SIMP(statut="o", typ="TXM", into=("G", "V")),
        NOMATR=SIMP(
            fr=tr("nom d attribut systeme"),
            statut="f",
            typ="TXM",
            into=(
                "$$CARA",
                "$$IADD",
                "$$GENR",
                "$$TYPE",
                "$$MARQ",
                "$$DOCU",
                "$$ORIG",
                "$$RNOM",
                "$$LTYP",
                "$$LONG",
                "$$LONO",
                "$$DATE",
                "$$LUTI",
                "$$HCOD",
                "$$INDX",
                "$$TLEC",
                "$$TECR",
                "$$IADM",
                "$$ACCE",
                "$$USADI",
            ),
        ),
    ),
    b_repertoire=BLOC(
        condition="""(equal_to("ENTITE", 'REPERTOIRE'))""",
        CLASSE=SIMP(statut="f", typ="TXM", into=("G", "V", " "), defaut=" "),
    ),
    b_disque=BLOC(
        condition="""(equal_to("ENTITE", 'DISQUE'))""",
        CLASSE=SIMP(statut="f", typ="TXM", into=("G", "V", " "), defaut=" "),
    ),
    b_enregist=BLOC(
        condition="""(equal_to("ENTITE", 'ENREGISTREMENT'))""",
        CLASSE=SIMP(statut="f", typ="TXM", into=("G", "V"), defaut="G"),
        NUMERO=SIMP(statut="o", typ="I", val_min=1),
        INFO=SIMP(statut="f", typ="I", into=(1, 2), defaut=1),
    ),
    IMPRESSION=FACT(
        statut="f",
        NOM=SIMP(statut="f", typ="TXM"),
        UNITE=SIMP(statut="f", typ=UnitType(), inout="out"),
    ),
    COMMENTAIRE=SIMP(statut="f", typ="TXM"),
)
