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
from ..Language.SyntaxUtils import deprecate


def compat_syntax(keywords):
    """Hook to adapt syntax from a old version or for compatibility reasons.

    Arguments:
        keywords (dict): Keywords arguments of user's keywords, changed
            in place.
    """
    # SEPAR is deprecated but tolerated syntax replaced by SEPARATEUR
    separ = keywords.pop("SEPAR", None)
    if separ:
        deprecate("LIRE_FONCTION/SEPAR", case=3, help="Prefer use SEPARATEUR=... instead.")
        if "SEPARATEUR" not in keywords:
            if separ in ("None", ",", ";", "/"):
                keywords["SEPARATEUR"] = separ


def lire_fonction_prod(self, TYPE, **args):
    if args.get("__all__"):
        return (fonction_sdaster, fonction_c, nappe_sdaster)

    if TYPE == "FONCTION":
        return fonction_sdaster
    elif TYPE == "FONCTION_C":
        return fonction_c
    elif TYPE == "NAPPE":
        return nappe_sdaster
    raise AsException("type de concept resultat non prevu")


LIRE_FONCTION = MACRO(
    nom="LIRE_FONCTION",
    op=OPS("code_aster.MacroCommands.lire_fonction_ops.lire_fonction_ops"),
    sd_prod=lire_fonction_prod,
    fr=tr(
        "Lit les valeurs réelles dans un fichier de données représentant une "
        "fonction et crée un concept de type fonction ou nappe"
    ),
    reentrant="n",
    compat_syntax=compat_syntax,
    FORMAT=SIMP(statut="f", typ="TXM", into=("LIBRE", "NUMPY"), defaut="LIBRE"),
    TYPE=SIMP(statut="f", typ="TXM", into=("FONCTION", "FONCTION_C", "NAPPE"), defaut="FONCTION"),
    SEPARATEUR=SIMP(statut="f", typ="TXM", defaut="None"),
    INDIC_PARA=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 1]),
    b_fonction=BLOC(
        condition="""equal_to("TYPE", 'FONCTION') """,
        INDIC_RESU=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 2]),
    ),
    b_fonction_c=BLOC(
        condition="""equal_to("TYPE", 'FONCTION_C') """,
        FORMAT_C=SIMP(
            statut="f", typ="TXM", defaut="REEL_IMAG", into=("REEL_IMAG", "MODULE_PHASE")
        ),
        b_reel_imag=BLOC(
            condition="""equal_to("FORMAT_C", 'REEL_IMAG') """,
            INDIC_REEL=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 2]),
            INDIC_IMAG=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 3]),
        ),
        b_modu_phas=BLOC(
            condition="""equal_to("FORMAT_C", 'MODULE_PHASE') """,
            INDIC_MODU=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 2]),
            INDIC_PHAS=SIMP(statut="f", typ="I", min=2, max=2, defaut=[1, 3]),
        ),
    ),
    b_nappe=BLOC(
        condition="""equal_to("TYPE", 'NAPPE') """,
        NOM_PARA_FONC=SIMP(statut="o", typ="TXM", into=C_PARA_FONCTION()),
        INDIC_ABSCISSE=SIMP(statut="o", typ="I", min=2, max=2),
        INTERPOL_FONC=SIMP(
            statut="f",
            typ="TXM",
            max=2,
            defaut="LIN",
            into=("LIN", "LOG"),
            fr=tr("Type d'interpolation pour les abscisses et les ordonnées de la fonction"),
        ),
        PROL_DROITE_FONC=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
        PROL_GAUCHE_FONC=SIMP(
            statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
        ),
        DEFI_FONCTION=FACT(
            statut="f", max="**", INDIC_RESU=SIMP(statut="o", typ="I", min=2, max=2)
        ),
    ),
    UNITE=SIMP(statut="o", typ=UnitType(), inout="in"),
    NOM_PARA=SIMP(statut="o", typ="TXM", into=C_PARA_FONCTION()),
    NOM_RESU=SIMP(statut="f", typ="TXM", defaut="TOUTRESU"),
    INTERPOL=SIMP(
        statut="f",
        typ="TXM",
        max=2,
        defaut="LIN",
        into=("LIN", "LOG"),
        fr=tr(
            "Type d'interpolation pour les abscisses et les ordonnées de la "
            "fonction ou bien pour le paramètre de la nappe."
        ),
    ),
    PROL_DROITE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    VERIF=SIMP(statut="f", typ="TXM", defaut="CROISSANT", into=("CROISSANT", "NON")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
