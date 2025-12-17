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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_INTERF_DYNA = OPER(
    nom="DEFI_INTERF_DYNA",
    op=98,
    sd_prod=interf_dyna_clas,
    reentrant="n",
    fr=tr("Définir les interfaces d'une structure et leur affecter un type"),
    NUME_DDL=SIMP(statut="o", typ=nume_ddl_sdaster),
    INTERFACE=FACT(
        statut="o",
        max="**",
        regles=(
            ENSEMBLE("NOM", "TYPE"),
            #  erreur doc U sur la condition qui suit
            UN_PARMI("NOEUD", "GROUP_NO"),
        ),
        NOM=SIMP(statut="o", typ="TXM"),
        TYPE=SIMP(statut="o", typ="TXM", into=("MNEAL", "CRAIGB", "CB_HARMO", "AUCUN")),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        #           DDL_ACTIF       =SIMP(statut='f',typ='TXM',max='**'),
        MASQUE=SIMP(statut="f", typ="TXM", max="**"),
    ),
    FREQ=SIMP(statut="f", typ="R", defaut=1.0),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
