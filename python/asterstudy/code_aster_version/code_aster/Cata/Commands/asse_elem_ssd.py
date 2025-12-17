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


def asse_elem_ssd_prod(self, RESU_ASSE_SSD, **args):
    MTYPES = {
        "MODELE": modele_gene,
        "NUME_DDL_GENE": nume_ddl_gene,
        "RIGI_GENE": matr_asse_gene_r,
        "MASS_GENE": matr_asse_gene_r,
    }
    if args.get("__all__"):
        return ([None], list(MTYPES.values()))

    for mc, typ in list(MTYPES.items()):
        if RESU_ASSE_SSD.get(mc):
            self.type_sdprod(RESU_ASSE_SSD[mc], typ)
    return None


ASSE_ELEM_SSD = MACRO(
    nom="ASSE_ELEM_SSD",
    op=OPS("code_aster.MacroCommands.asse_elem_ssd_ops.asse_elem_ssd_ops"),
    sd_prod=asse_elem_ssd_prod,
    reentrant="n",
    fr=tr("Enchainer les commandes DEFI_MODELE_GENE, NUME_DDL_GENE et ASSE_MATR_GENE"),
    # pour les concepts de sortie
    RESU_ASSE_SSD=FACT(
        statut="o",
        regles=(
            PRESENT_PRESENT("RIGI_GENE", "NUME_DDL_GENE"),
            PRESENT_PRESENT("MASS_GENE", "NUME_DDL_GENE"),
        ),
        MODELE=SIMP(statut="o", typ=CO),
        NUME_DDL_GENE=SIMP(statut="o", typ=CO),
        RIGI_GENE=SIMP(statut="o", typ=CO),
        MASS_GENE=SIMP(statut="o", typ=CO),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    # pour DEFI_MODELE_GENE
    SOUS_STRUC=FACT(
        statut="o",
        max="**",
        NOM=SIMP(statut="o", typ="TXM"),
        MACR_ELEM_DYNA=SIMP(statut="o", typ=macr_elem_dyna),
        ANGL_NAUT=SIMP(statut="f", typ="R", max=3),
        TRANS=SIMP(statut="f", typ="R", max=3),
    ),
    LIAISON=FACT(
        statut="o",
        max="**",
        SOUS_STRUC_1=SIMP(statut="o", typ="TXM"),
        INTERFACE_1=SIMP(statut="o", typ="TXM"),
        SOUS_STRUC_2=SIMP(statut="o", typ="TXM"),
        INTERFACE_2=SIMP(statut="o", typ="TXM"),
        regles=(EXCLUS("GROUP_MA_MAIT_1", "GROUP_MA_MAIT_2"),),
        GROUP_MA_MAIT_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_MA_MAIT_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        OPTION=SIMP(statut="f", typ="TXM", defaut="CLASSIQUE", into=("REDUIT", "CLASSIQUE")),
    ),
    VERIF=FACT(
        statut="d",
        max=1,
        STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),
    # pour NUME_DDL_GENE
    METHODE=SIMP(statut="f", typ="TXM", defaut="CLASSIQUE", into=("CLASSIQUE", "ELIMINE")),
    STOCKAGE=SIMP(statut="f", typ="TXM", defaut="LIGN_CIEL", into=("LIGN_CIEL", "PLEIN")),
)
