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

# person_in_charge: sylvie.audebert at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

COMB_SISM_MODAL = MACRO(
    nom="COMB_SISM_MODAL",
    op=OPS("code_aster.MacroCommands.comb_sism_modal_ops.comb_sism_modal_ops"),
    sd_prod=mode_meca,
    fr=tr("Réponse sismique par recombinaison modale par une méthode spectrale"),
    reentrant="n",
    regles=(
        UN_PARMI("AMOR_REDUIT", "LIST_AMOR", "AMOR_GENE"),
        EXCLUS("TOUT_ORDRE", "NUME_ORDRE", "FREQ", "NUME_MODE", "LIST_FREQ", "LIST_ORDRE"),
        UN_PARMI("AMOR_REDUIT", "LIST_AMOR", "AMOR_GENE"),
    ),
    # ---base modale
    MODE_MECA=SIMP(statut="o", typ=mode_meca),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster, defaut=None),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    b_freq=BLOC(
        condition="""exists("FREQ") or exists("LIST_FREQ")""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),
    # ---amortissement modal
    AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
    LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
    AMOR_GENE=SIMP(statut="f", typ=matr_asse_gene_r),
    # ---pseudo-mode
    MODE_CORR=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
    b_pseudo_mode=BLOC(
        condition="""equal_to("MODE_CORR", 'OUI') """,
        PSEUDO_MODE=SIMP(statut="o", typ=mode_meca),
        FREQ_COUP=SIMP(statut="f", typ="R", min=1, max=1),
    ),
    # ---type excitation ou type analyse
    TYPE_ANALYSE=SIMP(
        statut="f", typ="TXM", into=("MONO_APPUI", "MULT_APPUI"), defaut="MONO_APPUI"
    ),
    # --- definition des appuis pour type analyse multiple appuis
    b_appui=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MULT_APPUI')""",
        APPUIS=FACT(
            statut="o",
            max="**",
            NOM=SIMP(statut="o", typ="TXM", max=1),
            GROUP_NO=SIMP(statut="o", typ=grno, validators=NoRepeat(), max="**"),
        ),
    ),
    # ---chargement: sepctre
    b_spectre_mono_appui=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MONO_APPUI') """,
        SPECTRE=FACT(
            statut="o",
            max="**",
            LIST_AXE=SIMP(
                statut="o", typ="TXM", validators=NoRepeat(), max=3, min=1, into=("X", "Y", "Z")
            ),
            SPEC_OSCI=SIMP(statut="o", typ=(nappe_sdaster, formule)),
            ECHELLE=SIMP(statut="f", typ="R", defaut=1.0),
            NATURE=SIMP(statut="f", typ="TXM", defaut="ACCE", into=("ACCE", "VITE", "DEPL")),
            CORR_FREQ=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
        ),
    ),
    b_spectre_multi_appui=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MULT_APPUI')""",
        SPECTRE=FACT(
            statut="o",
            max="**",
            LIST_AXE=SIMP(
                statut="o", typ="TXM", validators=NoRepeat(), max=3, min=1, into=("X", "Y", "Z")
            ),
            SPEC_OSCI=SIMP(statut="o", typ=(nappe_sdaster, formule)),
            ECHELLE=SIMP(statut="f", typ="R", defaut=1.0),
            NATURE=SIMP(statut="f", typ="TXM", defaut="ACCE", into=("ACCE", "VITE", "DEPL")),
            CORR_FREQ=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
            NOM_APPUI=SIMP(statut="o", typ="TXM", max=1),
        ),
    ),
    # ---- chargement : deplacement du support en cas de multi_appui
    DEPL_MULT_APPUI=FACT(
        statut="f",
        max="**",
        regles=(AU_MOINS_UN("DX", "DY", "DZ")),
        MODE_STAT=SIMP(statut="o", typ=mode_meca),
        NOM_APPUI=SIMP(statut="o", typ="TXM", max=1),
        DX=SIMP(statut="f", typ="R", max=1),
        DY=SIMP(statut="f", typ="R", max=1),
        DZ=SIMP(statut="f", typ="R", max=1),
    ),
    # --- regle de combinaison des modes: on reserve la possible d'avoir plusieurs
    # regles de combi_modal (e.g. differentes regles pour differentes modes à developper)
    COMB_MODE=FACT(
        statut="o",
        max=1,
        TYPE=SIMP(
            statut="f", typ="TXM", into=("SRSS", "CQC", "DSC", "ABS", "DPC", "GUPTA"), defaut="CQC"
        ),
        b_gupta=BLOC(
            condition="""equal_to("TYPE", 'GUPTA') """,
            FREQ_1=SIMP(statut="o", typ="R"),
            FREQ_2=SIMP(statut="o", typ="R"),
        ),
        b_dsc=BLOC(condition="""equal_to("TYPE", 'DSC') """, DUREE=SIMP(statut="o", typ="R")),
    ),
    # --- regle combinaison des directions
    COMB_DIRECTION=SIMP(statut="f", typ="TXM", into=("QUAD", "NEWMARK"), defaut="NEWMARK"),
    # --- règle combinaison des reponses par appuis
    b_group_appui_corr=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MULT_APPUI')""",
        GROUP_APPUI_CORRELE=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("TOUT", "LIST_APPUI"),),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            LIST_APPUI=SIMP(statut="f", typ="TXM", max="**"),
            NOM=SIMP(statut="o", typ="TXM", max=1),
        ),
    ),
    b_comb_dds_correle=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MULT_APPUI')""",
        COMB_DDS_CORRELE=SIMP(statut="f", typ="TXM", into=("QUAD", "LINE", "ABS"), defaut="ABS"),
    ),
    # --- grandeurs interets de sortie
    OPTION=SIMP(
        statut="o",
        typ="TXM",
        validators=NoRepeat(),
        max=10,
        into=(  # champs aux noeuds
            "DEPL",
            "VITE",
            "ACCE_ABSOLU",
            "REAC_NODA",
            "FORC_NODA",
            # champs aux elements
            "SIGM_ELNO",
            "SIEF_ELGA",
            "SIPO_ELNO",
            "EFGE_ELNO",
            "SIEF_ELNO",
        ),
    ),
    # --- Option des types de resu
    b_type_resu_mono=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MONO_APPUI') """,
        TYPE_RESU=FACT(
            statut="o",
            max="**",
            TYPE=SIMP(
                statut="f",
                typ="TXM",
                into=(
                    "VALE_SPEC",
                    # "VALE_OSCI",  # interdire pour le moment
                    "VALE_QS",  # remplacer VALE_ROCH stat, aussi
                    "VALE_DIRE",
                    "VALE_DYNA",  # remplacer VALE_ROCH dyn (osci)
                    "VALE_INER",  # remplacer VALE_RCCM prim (osci + pseudo)
                    "VALE_TOTA",
                ),
                defaut="VALE_TOTA",
            ),
            b_vale_spec=BLOC(
                condition="""equal_to("TYPE", 'VALE_SPEC') """,
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster, defaut=None),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                b_freq=BLOC(
                    condition="""exists("FREQ") or exists("LIST_FREQ")""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                ),
                regles=(
                    UN_PARMI(
                        "TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "NUME_MODE", "FREQ", "LIST_FREQ"
                    ),
                ),
                LIST_AXE=SIMP(statut="o", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_osci=BLOC(
                condition="""equal_to("TYPE", 'VALE_OSCI') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_qs=BLOC(
                condition="""equal_to("TYPE", 'VALE_QS') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_dire=BLOC(
                condition="""equal_to("TYPE", 'VALE_DIRE') """,
                LIST_AXE=SIMP(statut="o", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_tota=BLOC(
                condition="""equal_to("TYPE", 'VALE_TOTA') """,
                NEWMARK=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
            ),
            b_vale_dyna=BLOC(
                condition="""equal_to("TYPE", 'VALE_DYNA') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_iner=BLOC(
                condition="""equal_to("TYPE", 'VALE_INER') """,
                NEWMARK=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
        ),
    ),
    b_type_resu_mult=BLOC(
        condition="""equal_to("TYPE_ANALYSE", 'MULT_APPUI') """,
        TYPE_RESU=FACT(
            statut="o",
            max="**",
            TYPE=SIMP(
                statut="f",
                typ="TXM",
                into=(
                    "VALE_SPEC",
                    # "VALE_OSCI",  # interdire à utiliser
                    "VALE_QS",  # remplacer VALE_ROCH stat, aussi
                    "VALE_DIRE",
                    "VALE_DDS",  # remplacer VALE_RCCM seco, aussi
                    "VALE_DYNA",  # remplacer VALE_ROCH dyn
                    "VALE_INER",  # remplacer VALE_RCCM prim
                    "VALE_TOTA",
                ),
                defaut="VALE_TOTA",
            ),
            b_vale_spec=BLOC(
                condition="""equal_to("TYPE", 'VALE_SPEC') """,
                TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
                NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
                NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
                FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
                LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
                b_freq=BLOC(
                    condition="""exists("FREQ") or exists("LIST_FREQ")""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                ),
                regles=(
                    UN_PARMI(
                        "TOUT_ORDRE", "NUME_ORDRE", "LIST_ORDRE", "NUME_MODE", "FREQ", "LIST_FREQ"
                    ),
                    EXCLUS("TOUT_APPUI", "LIST_APPUI"),
                ),
                LIST_APPUI=SIMP(statut="f", typ="TXM", max="**"),
                TOUT_APPUI=SIMP(statut="f", typ="TXM", into=("OUI",)),
                LIST_AXE=SIMP(statut="o", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_osci=BLOC(
                condition="""equal_to("TYPE", 'VALE_OSCI') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_qs=BLOC(
                condition="""equal_to("TYPE", 'VALE_QS') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_dds=BLOC(
                condition="""equal_to("TYPE", 'VALE_DDS') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_dire=BLOC(
                condition="""equal_to("TYPE", 'VALE_DIRE') """,
                LIST_AXE=SIMP(statut="o", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_tota=BLOC(
                condition="""equal_to("TYPE", 'VALE_TOTA') """,
                NEWMARK=SIMP(statut="f", typ="TXM", into=("OUI",)),
            ),
            b_vale_dyna=BLOC(
                condition="""equal_to("TYPE", 'VALE_DYNA') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
            b_vale_iner=BLOC(
                condition="""equal_to("TYPE", 'VALE_INER') """,
                LIST_AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
            ),
        ),
    ),
    # --- information supplementaire
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
