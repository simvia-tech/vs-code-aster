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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_CONTACT():
    mcfact = FACT(
        statut="f",
        max=1,
        DEFINITION=SIMP(statut="o", typ=(char_cont, char_frot)),
        # PARAMETRE GENERAL : BOUCLE DE GEOMETRIE
        ALGO_RESO_GEOM=SIMP(statut="f", typ="TXM", into=("POINT_FIXE", "NEWTON"), defaut="NEWTON"),
        b_algo_reso_geomNE=BLOC(
            condition="""equal_to("ALGO_RESO_GEOM", 'NEWTON')""",
            RESI_GEOM=SIMP(statut="f", typ="R", defaut=1e-6),
        ),
        b_algo_reso_geomPF=BLOC(
            condition="""equal_to("ALGO_RESO_GEOM", 'POINT_FIXE')""",
            REAC_GEOM=SIMP(
                statut="f",
                typ="TXM",
                into=("AUTOMATIQUE", "CONTROLE", "SANS"),
                defaut="AUTOMATIQUE",
            ),
            b_automatique=BLOC(
                condition="""equal_to("REAC_GEOM", 'AUTOMATIQUE') """,
                ITER_GEOM_MAXI=SIMP(statut="f", typ="I", defaut=10),
                RESI_GEOM=SIMP(statut="f", typ="R", defaut=1e-6),
            ),
            b_controle=BLOC(
                condition="""equal_to("REAC_GEOM", 'CONTROLE') """,
                NB_ITER_GEOM=SIMP(statut="f", typ="I", defaut=2),
            ),
        ),
        # PARAMETRE GENERAL : BOUCLE DE FROTTEMENT
        b_bouc_frot=BLOC(
            condition="""is_type("DEFINITION") == char_frot""",
            b_algo_frot_geomNE=BLOC(
                condition="""equal_to("ALGO_RESO_GEOM", 'NEWTON')""",
                ALGO_RESO_FROT=SIMP(statut="f", typ="TXM", into=("NEWTON",), defaut="NEWTON"),
            ),
            b_algo_frot_geomPF=BLOC(
                condition="""equal_to("ALGO_RESO_GEOM", 'POINT_FIXE')""",
                ALGO_RESO_FROT=SIMP(
                    statut="f", typ="TXM", into=("POINT_FIXE", "NEWTON"), defaut="POINT_FIXE"
                ),
                b_algo_reso_frotPF=BLOC(
                    condition="""equal_to("ALGO_RESO_FROT", 'POINT_FIXE')""",
                    ITER_FROT_MAXI=SIMP(statut="f", typ="I", defaut=10, val_min=0),
                ),
            ),
            RESI_FROT=SIMP(statut="f", typ="R", defaut=1.0e-4),
        ),
        # AUTRES
        #   CONT_STAT_ELAS=SIMP(statut='f', typ='I',
        #                       val_min=0, defaut=0),
    )

    return mcfact


# Chantier  ADAPTATION à faire (2023)

# Ajouter une methode python pour activer cette option - doc dans la docstring
# -------------------- No contact solving (only pairing)  - Au niveau de la zone -----------------------------------------------------------------------------------
# RESOLUTION       =SIMP(statut='f',typ='TXM',defaut="OUI",into=("OUI","NON")),
#                         b_verif=BLOC(condition = """equal_to("RESOLUTION", 'NON') """,
# TOLE_INTERP   = SIMP(statut='f',typ='R',defaut = 0.),),

#        ARRET DU CALCUL POUR LE MODE SANS RESOLUTION DU CONTACT - Option dans le python
# STOP_INTERP   = SIMP(statut='f', typ='TXM', defaut="NON", into=("OUI","NON"),
#                         fr=tr("Arrête le calcul dès qu'une interpénétration est détectée en mode RESOLUTION='NON'"),),


# Dans MECA_NON_LINE -> CONTACT

# # PARAMETRE GENERAL : BOUCLE DE CONTACT (supprimé - Point fixe)
#   à vérifier si RESI_CONT a un sens pour la méthode NEWTON

# *****                    RESI_CONT=SIMP(statut='f',typ='R',defaut=-1,),


# AUTRES POINTES :
# ADAPTATION chantier 2023 => peut-être dans DEFI_LIST_INST
