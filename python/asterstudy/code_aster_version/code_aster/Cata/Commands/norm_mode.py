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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def norm_mode_prod(MODE, **args):
    if args.get("__all__"):
        return (mode_meca, mode_meca_c, mode_flamb)

    if AsType(MODE) == mode_meca:
        return mode_meca
    if AsType(MODE) == mode_meca_c:
        return mode_meca_c
    if AsType(MODE) == mode_flamb:
        return mode_flamb
    raise AsException("type de concept resultat non prevu")


NORM_MODE = OPER(
    nom="NORM_MODE",
    op=37,
    sd_prod=norm_mode_prod,
    fr=tr("Normer des modes propres en fonction d'un critère choisi par l'utilisateur"),
    reentrant="f:MODE",
    regles=(UN_PARMI("NORME", "GROUP_NO", "AVEC_CMP", "SANS_CMP"),),
    reuse=SIMP(statut="c", typ=CO),
    MODE=SIMP(statut="o", typ=(mode_meca, mode_flamb)),
    NORME=SIMP(
        statut="f",
        typ="TXM",
        fr=tr("Norme prédéfinie : masse généralisée, euclidienne,..."),
        into=("MASS_GENE", "RIGI_GENE", "EUCL", "EUCL_TRAN", "TRAN", "TRAN_ROTA"),
    ),
    GROUP_NO=SIMP(
        statut="f",
        typ=grno,
        fr=tr("Composante donnée d'un groupe contenant un seul noeud spécifié égale à 1"),
    ),
    b_noeud=BLOC(condition="""exists("GROUP_NO")""", NOM_CMP=SIMP(statut="o", typ="TXM")),
    AVEC_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    SANS_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    MODE_SIGNE=FACT(
        statut="f",
        fr=tr("Imposer un signe sur une des composantes des modes"),
        regles=(UN_PARMI("GROUP_NO", "NOEUD"),),
        NOEUD=SIMP(statut="c", typ=no, fr=tr("Noeud où sera imposé le signe")),
        GROUP_NO=SIMP(
            statut="f", typ=grno, fr=tr("Groupe d'un seul noeud où sera imposé le signe")
        ),
        NOM_CMP=SIMP(statut="o", typ="TXM", fr=tr("Composante du noeud où sera imposé le signe")),
        SIGNE=SIMP(
            statut="f",
            typ="TXM",
            defaut="POSITIF",
            into=("NEGATIF", "POSITIF"),
            fr=tr("Choix du signe"),
        ),
    ),
    MASSE=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_gene_r, matr_asse_pres_r)),
    RAIDE=SIMP(
        statut="f", typ=(matr_asse_depl_r, matr_asse_depl_c, matr_asse_gene_r, matr_asse_pres_r)
    ),
    AMOR=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_gene_r)),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
