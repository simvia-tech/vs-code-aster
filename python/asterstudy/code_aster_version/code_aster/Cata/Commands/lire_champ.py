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

# person_in_charge: nicolas.sellenet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def lire_champ_prod(TYPE_CHAM=None, **args):
    # Remarque : si cette liste évolue, il faut penser à mettre à jour son
    #            homologue dans macr_adap_mail
    if args.get("__all__"):
        return (cham_no_sdaster, carte_sdaster, cham_elem)

    if TYPE_CHAM[0:5] == "NOEU_":
        return cham_no_sdaster
    if TYPE_CHAM[0:5] == "CART_":
        return carte_sdaster
    if TYPE_CHAM[0:2] == "EL":
        return cham_elem
    raise AsException("type de concept resultat non prevu")


LIRE_CHAMP = OPER(
    nom="LIRE_CHAMP",
    op=192,
    sd_prod=lire_champ_prod,
    fr=tr("Lire un champ dans un fichier au format MED et le stocker dans un concept."),
    reentrant="n",
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="MED", into=("MED",)),
    UNITE=SIMP(statut="f", typ=UnitType("med"), defaut=81, inout="in"),
    b_format=BLOC(
        condition="""equal_to("FORMAT", 'MED')""",
        regles=(
            UN_PARMI("NOM_CMP_IDEM", "NOM_CMP"),
            PRESENT_PRESENT("NOM_CMP", "NOM_CMP_MED"),
            EXCLUS("NUME_ORDRE", "INST"),
            EXCLUS("NUME_PT", "INST"),
        ),
        NOM_MED=SIMP(statut="o", typ="TXM"),
        NOM_CMP_IDEM=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOM_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CMP_MED=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        PROL_ZERO=SIMP(
            statut="f",
            typ="TXM",
            defaut="NON",
            into=("OUI", "NON"),
            fr=tr("Affecte des valeurs nulles la ou le champ n'est pas defini (sinon il y a NaN)"),
        ),
        NUME_PT=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NUME_ORDRE=SIMP(
            statut="f",
            typ="I",
            validators=NoRepeat(),
            max="**",
            fr=tr("Numero d ordre du champ à lire"),
        ),
        INST=SIMP(statut="f", typ="R", fr=tr("Instant associé")),
        #
        b_precision=BLOC(
            condition="""(exists("INST"))""",
            CRITERE=SIMP(
                statut="f",
                typ="TXM",
                defaut="RELATIF",
                into=("RELATIF", "ABSOLU"),
                fr=tr("Critère de précision sur le choix de l'instant associé"),
            ),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(
                    statut="f",
                    typ="R",
                    defaut=1.0e-6,
                    fr=tr("Précision sur le choix de l'instant associé"),
                ),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                PRECISION=SIMP(
                    statut="o", typ="R", fr=tr("Précision sur le choix de l'instant associé")
                ),
            ),
        ),
        #
        NOM_MAIL_MED=SIMP(statut="f", typ="TXM"),
    ),
    #        Remarque : si cette liste évolue, il faut penser à mettre à jour son
    #                   homologue dans macr_adap_mail
    TYPE_CHAM=SIMP(statut="o", typ="TXM", into=C_TYPE_CHAM_INTO()),
    b_modele=BLOC(
        condition="""exists("TYPE_CHAM") and (TYPE_CHAM[0:2] == 'EL')""",
        MODELE=SIMP(statut="o", typ=modele_sdaster),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
