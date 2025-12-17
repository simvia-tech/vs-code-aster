# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2024 - EDF R&D - www.code-aster.org
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
    """Adapt syntax before checking syntax.

    Change defaults depending on the parallel execution context and consume
    argument to force to exit after the command.

    Arguments:
        keywords (dict): Keywords arguments of user's keywords, changed
            in place.
    """
    if keywords.pop("FORMAT_HDF", None):
        deprecate("FIN/FORMAT_HDF", case=2)
    if keywords.pop("PROC0", None):
        deprecate("FIN/PROC0", case=2)


FIN = FIN_PROC(
    nom="FIN",
    op=9999,
    repetable="n",
    fr=tr("Fin d'une étude, fin du travail engagé par une des commandes DEBUT ou POURSUITE"),
    compat_syntax=compat_syntax,
    # FIN est appelé prématurément en cas d'exception ("SIGUSR1", ArretCPUError,
    # ConvergenceError..., erreurs <S> ou erreurs <F> récupérées).
    # En cas d'ArretCPUError, on limite au maximum le travail à faire dans FIN.
    RETASSAGE=SIMP(
        fr=tr("retassage de la base GLOBALE"),
        statut="f",
        typ="TXM",
        defaut="NON",
        into=("OUI", "NON"),
    ),
    INFO_BASE=SIMP(
        fr=tr(
            "impression des informations sur les objets existants la base globale "
            "même si celui-ci n'est pas sauvegardée"
        ),
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
    ),
    INFO_RESU=SIMP(
        fr=tr("impression des informations sur les structures de données résultats"),
        statut="f",
        typ="TXM",
        defaut="NON",
        into=("OUI", "NON"),
    ),
)
