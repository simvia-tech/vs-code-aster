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

# person_in_charge: sam.cuvilliez at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_essai_geomeca_prod(self, **args):
    if args.get("__all__"):
        return ([None], [None, table_sdaster])

    for key, fact in list(args.items()):
        if not key.startswith("ESSAI_"):
            continue
        if not fact:
            continue
        for occurrence in fact:
            res = occurrence.get("TABLE_RESU")
            if not res:
                continue
            for table in res:
                self.type_sdprod(table, table_sdaster)
    return None


CALC_ESSAI_GEOMECA = MACRO(
    nom="CALC_ESSAI_GEOMECA",
    op=OPS("code_aster.MacroCommands.calc_essai_geomeca_ops.calc_essai_geomeca_ops"),
    sd_prod=calc_essai_geomeca_prod,
    fr=tr(
        "Simulation 0D des essais de laboratoire pour les lois geomecaniques du Code_Aster (Hujeux, Mohr-Coulomb etc.)"
    ),
    reentrant="n",
    MATER=SIMP(statut="o", typ=mater_sdaster),
    COMPORTEMENT=C_COMPORTEMENT("CALC_ESSAI_GEOMECA"),
    CONVERGENCE=C_CONVERGENCE("SIMU_POINT_MAT"),
    regles=(  # COMPORTEMENT est facultatif dans C_COMPORTEMENT
        AU_MOINS_UN("COMPORTEMENT"),
        AU_MOINS_UN(
            "ESSAI_TRIA_DR_M_D",
            "ESSAI_TRIA_ND_M_D",
            "ESSAI_CISA_DR_C_D",
            "ESSAI_TRIA_ND_C_F",
            "ESSAI_TRIA_ND_C_D",
            "ESSAI_TRIA_DR_C_D",
            "ESSAI_OEDO_DR_C_F",
            "ESSAI_ISOT_DR_C_F",
            #'ESSAI_XXX'   ,
        ),
    ),
    # ---
    # Essai TRIAxial DRaine Monotone a Deformation imposee (TRIA_DR_M_D)
    # ---
    ESSAI_TRIA_DR_M_D=FACT(
        statut="f",
        max="**",
        fr=tr("Essai triaxial monotone draine a deformation controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        EPSI_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=100),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=("P-Q", "EPS_AXI-Q", "EPS_AXI-EPS_VOL", "P-EPS_VOL"),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR=SIMP(statut="f", typ="I", max="**"),
        STYLE=SIMP(statut="f", typ="I", max="**"),
    ),
    # ---
    #  Essai TRIAxial Non Draine Monotone a Deformation imposee (TRIA_ND_M_D)
    # ---
    ESSAI_TRIA_ND_M_D=FACT(
        statut="f",
        max="**",
        fr=tr("Essai triaxial monotone non draine a deformation controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        EPSI_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        BIOT_COEF=SIMP(statut="f", typ="R", defaut=1.0),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=100),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=("P-Q", "EPS_AXI-Q", "EPS_AXI-PRE_EAU"),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR=SIMP(statut="f", typ="I", max="**"),
        STYLE=SIMP(statut="f", typ="I", max="**"),
    ),
    # ---
    #  Essai de CISAillement DRaine Cyclique a Deformation imposee (CISA_DR_C_D)
    # ---
    ESSAI_CISA_DR_C_D=FACT(
        statut="f",
        max="**",
        fr=tr("Essai de cisaillement cyclique draine a deformation controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        GAMMA_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        GAMMA_ELAS=SIMP(statut="f", typ="R", defaut=1.0e-7, val_max=1.0e-7),
        NB_CYCLE=SIMP(statut="o", typ="I", val_min=1),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=("GAMMA-SIG_XY", "GAMMA-G_SUR_GMAX", "GAMMA-DAMPING", "G_SUR_GMAX-DAMPING"),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV1=SIMP(statut="f", typ="I", max="**"),
        COULEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV2=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # ---
    #  Essai TRIAxial Non Draine Cyclique a Force imposee ('TRIA_ND_C_F')
    # ---
    ESSAI_TRIA_ND_C_F=FACT(
        statut="f",
        max="**",
        # regles=(UN_PARMI('RU_MAX','EPSI_AXI_MAX',),),
        fr=tr("Essai triaxial cyclique non draine a force controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        SIGM_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        BIOT_COEF=SIMP(statut="f", typ="R", defaut=1.0),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        CRIT_LIQUEFACTION=SIMP(
            statut="o", typ="TXM", max=3, into=("RU_MAX", "EPSI_ABSO_MAX", "EPSI_RELA_MAX")
        ),
        VALE_CRIT=SIMP(statut="o", typ="R", max=3),
        ARRET_LIQUEFACTION=SIMP(statut="f", typ="TXM", max=1, defaut="OUI", into=("OUI", "NON")),
        UN_SUR_K=SIMP(statut="o", typ="R"),
        NB_CYCLE=SIMP(statut="o", typ="I", val_min=1),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        NB_INST_MONO=SIMP(statut="f", typ="I", val_min=100, defaut=400),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=(
                "NCYCL-DSIGM",
                "P-Q",
                "SIG_AXI-PRE_EAU",
                "EPS_AXI-PRE_EAU",
                "SIG_AXI-RU",
                "EPS_AXI-RU",
                "EPS_AXI-Q",
            ),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV1=SIMP(statut="f", typ="I", max="**"),
        COULEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV2=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # ---
    # Essai TRIAxial Non Draine Cylique a Deplacement impose (TRIA_ND_C_D)
    # ---
    ESSAI_TRIA_ND_C_D=FACT(
        statut="f",
        max="**",
        fr=tr("Essai triaxial cyclique non draine a deformation controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        EPSI_MINI=SIMP(statut="o", typ="R", max="**"),
        EPSI_MAXI=SIMP(statut="o", typ="R", max="**"),
        EPSI_ELAS=SIMP(statut="f", typ="R", defaut=1.0e-7, val_max=1.0e-7),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        NB_CYCLE=SIMP(statut="o", typ="I", val_min=1),
        BIOT_COEF=SIMP(statut="f", typ="R", defaut=1.0),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        UN_SUR_K=SIMP(statut="o", typ="R"),
        RU_MAX=SIMP(statut="f", typ="R", defaut=0.8),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=(
                "NCYCL-DEPSI",
                "DEPSI-RU_MAX",
                "DEPSI-E_SUR_EMAX",
                "DEPSI-DAMPING",
                "P-Q",
                "EPS_AXI-EPS_VOL",
                "EPS_AXI-Q",
                "P-EPS_VOL",
                "EPS_AXI-PRE_EAU",
                "EPS_AXI-RU",
                "P-PRE_EAU",
            ),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV1=SIMP(statut="f", typ="I", max="**"),
        COULEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV2=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # ---
    # Essai TRIAxial DRaine Cylique a Deplacement impose (TRIA_DR_C_D)
    # ---
    ESSAI_TRIA_DR_C_D=FACT(
        statut="f",
        max="**",
        fr=tr("Essai triaxial cyclique draine a deformation controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        EPSI_MINI=SIMP(statut="o", typ="R", max="**"),
        EPSI_MAXI=SIMP(statut="o", typ="R", max="**"),
        EPSI_ELAS=SIMP(statut="f", typ="R", defaut=1.0e-7, val_max=1.0e-7),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        NB_CYCLE=SIMP(statut="o", typ="I", val_min=1),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=(
                "P-Q",
                "EPS_AXI-Q",
                "EPS_VOL-Q",
                "EPS_AXI-EPS_VOL",
                "P-EPS_VOL",
                "DEPSI-E_SUR_EMAX",
                "DEPSI-DAMPING",
            ),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV1=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV1=SIMP(statut="f", typ="I", max="**"),
        COULEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR_NIV2=SIMP(statut="f", typ="I", max="**"),
        STYLE_NIV2=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # ---
    #  Essai OEDOmetrique DRaine Cyclique a force imposee (OEDO_DR_C_F)
    # ---
    ESSAI_OEDO_DR_C_F=FACT(
        statut="f",
        max="**",
        fr=tr("Essai eodometrique cyclique draine a force controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        SIGM_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        SIGM_DECH=SIMP(statut="o", typ="R", max="**"),
        KZERO=SIMP(statut="f", typ="R", defaut=1.0),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(
            statut="f",
            typ="TXM",
            max="**",
            validators=NoRepeat(),
            defaut=("P-EPS_VOL", "SIG_AXI-EPS_VOL"),
        ),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR=SIMP(statut="f", typ="I", max="**"),
        STYLE=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # --
    #  Essai de compression ISOTrope DRainee Cyclique a force imposee (ISOT_DR_C_F)
    # ---
    ESSAI_ISOT_DR_C_F=FACT(
        statut="f",
        max="**",
        fr=tr("Essai isotrope cyclique draine a force controlee"),
        PRES_CONF=SIMP(statut="o", typ="R", max="**"),
        SIGM_IMPOSE=SIMP(statut="o", typ="R", max="**"),
        SIGM_DECH=SIMP(statut="o", typ="R", max="**"),
        NB_INST=SIMP(statut="f", typ="I", val_min=5, defaut=25),
        TABLE_RESU=SIMP(statut="f", typ=CO, max="**", validators=NoRepeat()),
        GRAPHIQUE=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat(), defaut="P-EPS_VOL"),
        PREFIXE_FICHIER=SIMP(
            statut="f", typ="TXM", max=1, fr=tr("prefixe des noms de fichier xmgrace recuperes")
        ),
        TABLE_REF=SIMP(statut="f", typ=table_sdaster, max="**"),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**", validators=NoRepeat()),
        COULEUR=SIMP(statut="f", typ="I", max="**"),
        MARQUEUR=SIMP(statut="f", typ="I", max="**"),
        STYLE=SIMP(statut="f", typ="I", max="**"),
        TYPE_CHARGE=SIMP(
            statut="f", typ="TXM", max=1, defaut="SINUSOIDAL", into=("SINUSOIDAL", "TRIANGULAIRE")
        ),
    ),
    # ---
    #  Essai ... ('XXX')
    # ---
    # ESSAI_XXX = FACT(statut='f',max='**',
    #
    #     PRES_CONF  = SIMP(statut='o',typ='R',max='**',),
    #     ...
    #
    #     TABLE_RESU = SIMP(statut='f',typ=CO,max='**',validators=NoRepeat(),),
    #     GRAPHIQUE  = SIMP(statut='f',typ='TXM',max='**',validators=NoRepeat(),
    #                        into=  ('XXX','XXX','XXX',),
    #                        defaut=('XXX','XXX','XXX',),),
    #     TABLE_REF  = SIMP(statut='f',typ=table_sdaster,max='**',),
    #
    #                 ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
