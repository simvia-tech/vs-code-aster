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

# person_in_charge: harinaivo.andriambololona at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_essai_prod(self, RESU_IDENTIFICATION, RESU_MODIFSTRU, **args):
    MTYPES = {
        "MODELE": modele_sdaster,
        "MODE_MECA": mode_meca,
        "NUME_DDL": nume_ddl_sdaster,
        "MAILLAGE": maillage_sdaster,
        "MASS_MECA": matr_asse_depl_r,
        "RIGI_MECA": matr_asse_depl_r,
        "AMOR_MECA": matr_asse_depl_r,
        "MACR_ELEM": macr_elem_stat,
        "PROJ_MESU": mode_gene,
        "BASE_ES": mode_meca,
        "BASE_LMME": mode_meca,
        "MODE_STA": mode_meca,
    }
    if args.get("__all__"):
        return ([None], [None, interspectre], [None] + list(MTYPES.values()))

    if RESU_IDENTIFICATION is not None:
        for res in RESU_IDENTIFICATION:
            self.type_sdprod(res["TABLE"], interspectre)

    if RESU_MODIFSTRU is not None:
        for mc, typ in list(MTYPES.items()):
            if RESU_MODIFSTRU[mc]:
                self.type_sdprod(RESU_MODIFSTRU[mc], typ)
    return None


CALC_ESSAI = MACRO(
    nom="CALC_ESSAI",
    op=OPS("code_aster.MacroCommands.calc_essai_ops.calc_essai_ops"),
    sd_prod=calc_essai_prod,
    reentrant="n",
    fr=tr("Outil de post-traitement pour Meidee "),
    RESU_IDENTIFICATION=FACT(statut="f", max="**", TABLE=SIMP(statut="f", typ=CO)),
    RESU_MODIFSTRU=FACT(
        statut="f",
        max=1,
        MODELE=SIMP(statut="f", typ=CO),
        MODE_MECA=SIMP(statut="f", typ=CO),
        MAILLAGE=SIMP(statut="f", typ=CO),
        NUME_DDL=SIMP(statut="f", typ=CO),
        MASS_MECA=SIMP(statut="f", typ=CO),
        RIGI_MECA=SIMP(statut="f", typ=CO),
        AMOR_MECA=SIMP(statut="f", typ=CO),
        MACR_ELEM=SIMP(statut="f", typ=CO),
        PROJ_MESU=SIMP(statut="f", typ=CO),
        BASE_ES=SIMP(statut="f", typ=CO),
        BASE_LMME=SIMP(statut="f", typ=CO),
        MODE_STA=SIMP(statut="f", typ=CO),
    ),
    EXPANSION=FACT(
        statut="f",
        max="**",
        CALCUL=SIMP(statut="o", typ=mode_meca),
        NUME_MODE_CALCUL=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
        MESURE=SIMP(statut="o", typ=mode_meca),
        NUME_MODE_MESURE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**", defaut=0),
        RESOLUTION=SIMP(statut="f", typ="TXM", defaut="SVD", into=("SVD", "LU")),
        b_reso=BLOC(
            condition="""equal_to("RESOLUTION", 'SVD')""", EPS=SIMP(statut="f", typ="R", defaut=0.0)
        ),
    ),
    IDENTIFICATION=FACT(
        statut="f",
        max="**",
        ALPHA=SIMP(statut="f", typ="R", defaut=0.0),
        EPS=SIMP(statut="f", typ="R", defaut=0.0),
        OBSERVABILITE=SIMP(statut="o", typ=mode_meca),
        COMMANDABILITE=SIMP(statut="o", typ=mode_meca),
        INTE_SPEC=SIMP(statut="o", typ=interspectre),
        BASE=SIMP(statut="o", typ=mode_meca),
    ),
    MODIFSTRUCT=FACT(
        statut="f",
        max=1,
        MESURE=SIMP(statut="o", typ=mode_meca),
        MODELE_SUP=SIMP(statut="o", typ=modele_sdaster),
        MATR_RIGI=SIMP(statut="o", typ=matr_asse_depl_r),
        RESOLUTION=SIMP(statut="f", typ="TXM", into=("ES", "LMME"), defaut="ES"),
        b_resol=BLOC(
            condition="""equal_to("RESOLUTION", 'LMME')""",
            MATR_MASS=SIMP(statut="o", typ=matr_asse_depl_r),
        ),
        NUME_MODE_MESU=SIMP(statut="o", typ="I", max="**"),
        NUME_MODE_CALCUL=SIMP(statut="o", typ="I", max="**"),
        MODELE_MODIF=SIMP(statut="o", typ=modele_sdaster),
    ),
    # Si on realise une modification structurale, on donne les DDL capteurs et interface
    b_modif=BLOC(
        condition="""exists("MODIFSTRUCT")""",
        GROUP_NO_CAPTEURS=FACT(
            statut="f",
            max="**",
            GROUP_NO=SIMP(statut="o", typ=grno),
            NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
        ),
        GROUP_NO_EXTERIEUR=FACT(
            statut="f",
            max="**",
            GROUP_NO=SIMP(statut="o", typ=grno),
            NOM_CMP=SIMP(statut="o", typ="TXM", max="**"),
        ),
    ),
)
