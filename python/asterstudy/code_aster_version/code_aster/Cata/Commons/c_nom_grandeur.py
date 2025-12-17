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

# person_in_charge: mathieu.courtois at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_NOM_GRANDEUR():
    """Retourne la liste des noms des grandeurs pour le catalogue"""
    return (
        "ABSC_R",
        "CACOQU_R",
        "CAMA_R",
        "CHLI_R",
        "CODE_I",
        "COEH_F",
        "COEH_R",
        "CORR_R",
        "CRRU_R",
        "DBEL_R",
        "DCEL_I",
        "DDLI_C",
        "DDLI_F",
        "DDLI_R",
        "DDLM_C",
        "DDLM_R",
        "DEPL_C",
        "DEPL_F",
        "DEPL_R",
        "DISS_R",
        "DOMA_R",
        "DURT_R",
        "ENDO_R",
        "ENER_R",
        "EPSI_C",
        "EPSI_F",
        "EPSI_R",
        "ERRE_R",
        "FACY_R",
        "FLAP_R",
        "FER2_R",
        "FISS_R",
        "FLUN_F",
        "FLUN_R",
        "FLUX_F",
        "FLUX_R",
        "FORC_C",
        "FORC_F",
        "FORC_R",
        "FREQ_R",
        "FTHM_F",
        "FTHM_R",
        "ETHM_R",
        "ETHM_F",
        "GEOM_R",
        "G_DEPL_R",
        "HYDR_R",
        "IMPE_C",
        "IMPE_F",
        "IMPE_R",
        "INDL_R",
        "INFC_R",
        "INST_R",
        "INTE_R",
        "IRRA_R",
        "MASS_R",
        "MATE_R",
        "MATE_F",
        "NBSP_I",
        "NEUT_F",
        "NEUT_I",
        "NEUT_R",
        "N480_R",
        "NUMC_I",
        "ONDE_F",
        "ONDE_R",
        "PESA_R",
        "PDIL_R",
        "PILO_R",
        "PRES_C",
        "PRES_F",
        "PRES_R",
        "RAYO_F",
        "RAYO_R",
        "RCCM_R",
        "ROTA_R",
        "SIEF_C",
        "SIEF_R",
        "SIEFMX_R",
        "SIZZ_R",
        "SOUR_F",
        "SOUR_R",
        "SPMX_R",
        "STRX_R",
        "TEMP_C",
        "TEMP_F",
        "TEMP_R",
        "VALO_R",
        "VANL_R",
        "VAR2_R",
        "VARI_R",
        "VENTCX_F",
        "VFAC_C",
        "VFAC_F",
        "VFAC_R",
        "CLAC_R",
        "THET_R",
    )
