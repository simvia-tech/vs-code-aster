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
# person_in_charge: yannick.tampango at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def dyna_line_sdprod(self, TYPE_CALCUL, BASE_RESU=None, RESU_GENE=None, **args):
    if args.get("__all__"):
        return ([dyna_trans, dyna_harmo], [None, mode_meca], [None, tran_gene, harm_gene])

    if BASE_RESU is not None:
        self.type_sdprod(BASE_RESU, mode_meca)
    if RESU_GENE is not None:
        if TYPE_CALCUL == "TRAN":
            self.type_sdprod(RESU_GENE, tran_gene)
        else:
            self.type_sdprod(RESU_GENE, harm_gene)
    if TYPE_CALCUL == "TRAN":
        return dyna_trans
    else:
        return dyna_harmo


DYNA_LINE = MACRO(
    nom="DYNA_LINE",
    op=OPS("code_aster.MacroCommands.dyna_line_ops.dyna_line_ops"),
    sd_prod=dyna_line_sdprod,
    reentrant="n",
    fr=tr("Calcul dynamique transitoire ou harmonique"),
    # reuse=SIMP(statut='c', typ=CO),
    # Calculation type and basis
    TYPE_CALCUL=SIMP(statut="o", typ="TXM", into=("HARM", "TRAN")),
    BASE_CALCUL=SIMP(statut="o", typ="TXM", into=("PHYS", "GENE")),
    # Physical model information
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    CHARGE=SIMP(statut="f", typ=(char_meca, char_cine_meca), max="**"),
    # if no value, F_max computed automaticaly, F_min set to 0
    # if only one value => F_max, F_min set to 0
    # if two value F_min set to the first one, F_max set to the second one
    # F_max is used to compute the time step automatically
    # if 2 values  , sinon F_min et F_max
    BANDE_ANALYSE=SIMP(statut="f", typ="R", min=1, max=2),
    PCENT_COUP=SIMP(
        fr=tr("Pourcentage du cumul quadratique pour calculer frequence de coupure"),
        statut="f",
        typ="I",
        val_min=80,
        val_max=100,
        max=1,
        defaut=90,
    ),
    b_param_gene=BLOC(
        condition="""equal_to("BASE_CALCUL", 'GENE')""",
        BASE_RESU=SIMP(statut="f", typ=CO, validators=NoRepeat()),
        RESU_GENE=SIMP(statut="f", typ=CO, validators=NoRepeat()),
    ),
    # Dans Python on pourra se servir de BANDE_ANALYSE pour definir les frequences harmoniques
    # Harmonic calculation parameters
    b_param_harm=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM')""",
        regles=(UN_PARMI("FREQ", "LIST_FREQ"),),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    ),
    # Transient calculation parameters
    b_param_tran=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN')""",
        # 1. Integration schemes
        SCHEMA_TEMPS=FACT(
            statut="d",
            SCHEMA=SIMP(
                statut="f",
                typ="TXM",
                defaut="DEVOGE",
                into=(
                    "NEWMARK",
                    "WILSON",
                    "DIFF_CENTRE",
                    "DEVOGE",
                    "ADAPT_ORDRE1",
                    "ADAPT_ORDRE2",
                    "RUNGE_KUTTA_32",
                    "RUNGE_KUTTA_54",
                    "ITMI",
                ),
            ),
            b_newmark=BLOC(
                condition="""equal_to("SCHEMA", 'NEWMARK')""",
                BETA=SIMP(statut="f", typ="R", defaut=0.25),
                GAMMA=SIMP(statut="f", typ="R", defaut=0.5),
            ),
            b_wilson=BLOC(
                condition="""equal_to("SCHEMA", 'WILSON')""",
                THETA=SIMP(statut="f", typ="R", defaut=1.4),
            ),
            b_rk_devo=BLOC(
                condition="""equal_to("SCHEMA", 'RUNGE_KUTTA_54') or equal_to("SCHEMA", 'RUNGE_KUTTA_32') or equal_to("SCHEMA", 'DEVOGE')""",
                TOLERANCE=SIMP(statut="f", typ="R", defaut=1.0e-5),
                ALPHA=SIMP(statut="f", typ="R", defaut=0.0),
            ),
            b_adapt_ord=BLOC(
                condition="""equal_to("SCHEMA", 'ADAPT_ORDRE1') or  equal_to("SCHEMA", 'ADAPT_ORDRE2')""",
                VITE_MIN=SIMP(statut="f", typ="TXM", defaut="NORM", into=("MAXI", "NORM")),
                COEF_MULT_PAS=SIMP(statut="f", typ="R", defaut=1.1),
                COEF_DIVI_PAS=SIMP(statut="f", typ="R", defaut=1.3333334),
                PAS_LIMI_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6),
                NB_POIN_PERIODE=SIMP(statut="f", typ="I", defaut=50),
            ),
            b_alladapt=BLOC(
                condition="""is_in("SCHEMA", ('RUNGE_KUTTA_54','RUNGE_KUTTA_32','DEVOGE','ADAPT_ORDRE1','ADAPT_ORDRE2'))""",
                PAS_MINI=SIMP(statut="f", typ="R"),
                PAS_MAXI=SIMP(statut="f", typ="R"),
                NMAX_ITER_PAS=SIMP(statut="f", typ="I", defaut=16),
            ),
        ),  # end fkw_schema_temps
        # 2. Time discretisation
        INCREMENT=FACT(
            statut="o",
            INST_INIT=SIMP(statut="f", typ="R"),
            PAS=SIMP(statut="f", typ="R"),
            INST_FIN=SIMP(statut="o", typ="R"),
        ),  # end fkw_discretisation
    ),  # end b_param_tran
    # 4. Archiving parameters
    b_dlt_prec=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'TRAN')""",
        ARCHIVAGE=FACT(
            statut="f",
            max=1,
            regles=(EXCLUS("LIST_INST", "INST"), AU_MOINS_UN("LIST_INST", "INST", "PAS_ARCH")),
            PAS_ARCH=SIMP(statut="f", typ="I"),
            LIST_INST=SIMP(statut="f", typ=(listr8_sdaster)),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            b_list_inst=BLOC(
                condition="""(exists("LIST_INST") or exists("INST"))""",
                CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
                b_prec_rela=BLOC(
                    condition="""(equal_to("CRITERE", 'RELATIF'))""",
                    PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                ),
                b_prec_abso=BLOC(
                    condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                    PRECISION=SIMP(statut="o", typ="R"),
                ),
            ),  # end b_list_inst
            CHAM_EXCLU=SIMP(
                statut="f", typ="TXM", validators=NoRepeat(), max=2, into=("DEPL", "VITE", "ACCE")
            ),
        ),  # end fkw_archivage
    ),  # end b_dlt_prec
    b_not_dlt_prec=BLOC(
        condition="""not equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'TRAN')""",
        ARCHIVAGE=FACT(
            statut="f",
            max=1,
            regles=(EXCLUS("LIST_INST", "INST"), AU_MOINS_UN("LIST_INST", "INST", "PAS_ARCH")),
            PAS_ARCH=SIMP(statut="f", typ="I"),
            LIST_INST=SIMP(statut="f", typ=(listr8_sdaster)),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            #               CHAM_EXCLU  =     SIMP(statut='f',typ='TXM',validators=NoRepeat(),max=2,into=("DEPL","VITE","ACCE"),),
        ),  # end fkw_archivage
    ),  # end b_not_dlt_prec
    #       Transient case
    b_excit_line_tran=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN')""",
        regles=AU_MOINS_UN("ETAT_INIT", "EXCIT"),
        # 3. Initial state
        ETAT_INIT=FACT(
            statut="f",
            max=1,
            #                       regles=(EXCLUS('RESULTAT','DEPL'), EXCLUS('RESULTAT','VITE'),),
            # RESULTAT    =         SIMP(statut='f',typ=dyna_trans),
            # b_resu      =         BLOC(condition = """exists("RESULTAT")""", regles = (EXCLUS('NUME_ORDRE','INST_INIT'),),
            # NUME_ORDRE  =             SIMP(statut='f',typ='I'),
            # INST_INIT   =             SIMP(statut='f',typ='R'),
            # b_inst_init =             BLOC(condition = """exists("INST_INIT")""",
            # CRITERE     =                 SIMP(statut='f',typ='TXM',defaut="RELATIF",into=("RELATIF","ABSOLU"),),
            # b_prec_rela =                 BLOC(condition="""(equal_to("CRITERE", 'RELATIF'))""",
            # PRECISION   =                     SIMP(statut='f',typ='R',defaut= 1.E-6,),),
            # b_prec_abso =                 BLOC(condition="""(equal_to("CRITERE", 'ABSOLU'))""",
            # PRECISION   =                     SIMP(statut='o',typ='R',),),),),
            DEPL=SIMP(statut="f", typ=cham_no_sdaster),
            VITE=SIMP(statut="f", typ=cham_no_sdaster),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            TYPE_APPUI=SIMP(statut="f", typ="TXM", into=("MONO", "MULTI")),
            b_no_appui=BLOC(
                condition="""not exists("TYPE_APPUI")""",
                CHARGE=SIMP(statut="o", typ=char_meca),
                FONC_MULT=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
            ),
            b_mult_mono=BLOC(
                condition="""equal_to("TYPE_APPUI", 'MONO')""",
                regles=(
                    PRESENT_PRESENT("ACCE", "VITE", "DEPL"),
                    PRESENT_ABSENT("ACCE", "FONC_MULT"),
                ),
                DIRECTION=SIMP(statut="o", typ="R", max=6),
                FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            ),
            b_mult_appui=BLOC(
                condition="""equal_to("TYPE_APPUI", 'MULTI')""",
                regles=(
                    PRESENT_PRESENT("ACCE", "VITE", "DEPL"),
                    PRESENT_ABSENT("ACCE", "FONC_MULT"),
                ),
                DIRECTION=SIMP(statut="o", typ="R", max=6),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
                FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
                DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            ),
        ),
    ),  # end b_excit_line_tran
    #       Transient case
    b_excit_line_harm=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM')""",
        EXCIT=FACT(
            statut="o",
            max="**",
            regles=(UN_PARMI("FONC_MULT", "FONC_MULT_C", "COEF_MULT", "COEF_MULT_C"),),
            TYPE_APPUI=SIMP(statut="f", typ="TXM", into=("MONO", "MULTI")),
            FONC_MULT_C=SIMP(statut="f", typ=(fonction_c, formule_c)),
            COEF_MULT_C=SIMP(statut="f", typ="C"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            PHAS_DEG=SIMP(statut="f", typ="R", defaut=0.0e0),
            PUIS_PULS=SIMP(statut="f", typ="I", defaut=0),
            b_no_appui=BLOC(
                condition="""not exists("TYPE_APPUI")""", CHARGE=SIMP(statut="o", typ=char_meca)
            ),
            b_mult_mono=BLOC(
                condition="""equal_to("TYPE_APPUI", 'MONO')""",
                DIRECTION=SIMP(statut="o", typ="R", max=6),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            ),
            b_mult_appui=BLOC(
                condition="""equal_to("TYPE_APPUI", 'MULTI')""",
                DIRECTION=SIMP(statut="o", typ="R", max=6),
                GROUP_NO=SIMP(statut="o", typ=grno, validators=NoRepeat(), max="**"),
            ),
        ),
    ),  # end b_excit_line_harm
    # Damping
    b_amor_tran_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'PHYS')""",
        AMORTISSEMENT=FACT(
            statut="f",
            TYPE_AMOR=SIMP(statut="o", typ="TXM", into=("RAYLEIGH",)),
            VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
        ),
    ),  # end b_amor_tran_phys
    b_amor_harm_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'PHYS')""",
        AMORTISSEMENT=FACT(
            statut="f",
            TYPE_AMOR=SIMP(statut="o", typ="TXM", into=("RAYLEIGH", "HYST")),
            b_amor_flui_abso=BLOC(
                condition="""equal_to("TYPE_AMOR", 'RAYLEIGH')""",
                VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
                MATR_IMPE_PHI=SIMP(
                    statut="f", typ="TXM", defaut="NON", into=("OUI", "NON"), min=1, max=1
                ),
            ),
        ),
    ),  # end b_amor_harm_phys
    b_amor_tran_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'GENE')""",
        AMORTISSEMENT=FACT(
            statut="f",
            TYPE_AMOR=SIMP(statut="o", typ="TXM", into=("RAYLEIGH", "MODAL")),
            b_modal=BLOC(
                condition="""equal_to("TYPE_AMOR", 'MODAL')""",
                AMOR_REDUIT=SIMP(statut="o", typ="R", max="**"),
            ),
            b_amor_flui_abso=BLOC(
                condition="""equal_to("TYPE_AMOR", 'RAYLEIGH')""",
                VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
            ),
        ),
    ),  # end b_amor_tran_gene
    b_amor_harm_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'GENE')""",
        AMORTISSEMENT=FACT(
            statut="f",
            TYPE_AMOR=SIMP(statut="o", typ="TXM", into=("RAYLEIGH", "MODAL", "HYST")),
            b_modal=BLOC(
                condition="""equal_to("TYPE_AMOR", 'MODAL')""",
                AMOR_REDUIT=SIMP(statut="o", typ="R", max="**"),
            ),
            b_amor_flui_abso=BLOC(
                condition="""equal_to("TYPE_AMOR", 'RAYLEIGH')""",
                VNOR=SIMP(statut="f", typ="R", into=(1.0, -1.0), defaut=1.0),
                MATR_IMPE_PHI=SIMP(
                    statut="f", typ="TXM", defaut="NON", into=("OUI", "NON"), min=1, max=1
                ),
            ),
        ),
    ),  # end b_amor_harm_gene
    b_harm_phys=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'HARM')""",
        SOLVEUR=C_SOLVEUR("DYNA_LINE_HARM", "PHYS"),
    ),
    b_tran_phys=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'TRAN')""",
        SOLVEUR=C_SOLVEUR("DYNA_LINE_TRAN"),
    ),
    b_harm_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'GENE')""",
        regles=EXCLUS("ISS", "IFS"),
        ISS=SIMP(statut="f", typ="TXM", into=("OUI",)),
        IFS=SIMP(statut="f", typ="TXM", into=("OUI",)),
        b_no_ifs=BLOC(
            condition="""not exists("IFS")""",
            SOLVEUR=C_SOLVEUR("DYNA_LINE_HARM", "GENE"),
            ENRI_STAT=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            b_param_enri_stat=BLOC(
                condition="""equal_to("ENRI_STAT", 'OUI')""",
                ORTHO=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                FREQ_COUP_STAT=SIMP(statut="f", typ="R"),
            ),
        ),
        b_iss_harm=BLOC(
            condition="""equal_to("ISS", 'OUI')""",
            VERSION_MISS=SIMP(
                statut="f",
                typ="TXM",
                into=("V6.7", "V6.6", "V6.5"),
                defaut="V6.7",
                fr=tr("Version de Miss utilisée"),
            ),
            CALC_IMPE_FORC=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            GROUP_MA_INTERF=SIMP(
                statut="o", typ=grma, max="**", fr=tr("Groupe de mailles de l'interface")
            ),
            GROUP_NO_INTERF=SIMP(
                statut="o", typ=grno, max="**", fr=tr("Groupe de noeuds de l'interface")
            ),
            TYPE_MODE=SIMP(
                statut="f",
                typ="TXM",
                into=("PSEUDO", "CRAIG_BAMPTON", "INTERF"),
                defaut="CRAIG_BAMPTON",
            ),
            b_nb_mode_interf=BLOC(
                condition="""equal_to("TYPE_MODE",'INTERF')""",
                NB_MODE_INTERF=SIMP(statut="o", typ="I"),
            ),
            b_not_calc_impe_forc=BLOC(
                condition="""equal_to("CALC_IMPE_FORC", 'NON')""",
                UNITE_RESU_IMPE=SIMP(
                    statut="o",
                    typ=UnitType(),
                    inout="in",
                    fr=tr("Unité logique des impédances écrites par Miss"),
                ),
                UNITE_RESU_FORC=SIMP(
                    statut="o",
                    typ=UnitType(),
                    inout="in",
                    fr=tr("Unité logique des forces sismiques écrites par Miss"),
                ),
            ),
            b_calc_impe_forc=BLOC(
                condition="""equal_to("CALC_IMPE_FORC", 'OUI')""",
                regles=(EXCLUS("TABLE_SOL", "MATER_SOL"),),
                UNITE_IMPR_ASTER=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité des résultats transmis par Code_Aster à Miss"),
                ),
                UNITE_RESU_IMPE=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité logique des impédances écrites par Miss"),
                ),
                UNITE_RESU_FORC=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité logique des forces sismiques écrites par Miss"),
                ),
                TABLE_SOL=SIMP(
                    statut="f", typ=table_sdaster, fr=tr("Table des propriétés du sol stratifié")
                ),
                MATER_SOL=FACT(
                    statut="f",
                    fr=tr("Propriétés du sol homogène"),
                    E=SIMP(statut="o", typ="R", val_min=0.0),
                    NU=SIMP(statut="o", typ="R", val_min=-1.0, val_max=0.5),
                    RHO=SIMP(statut="o", typ="R", val_min=0.0),
                    AMOR_HYST=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0),
                ),
                # Paramètres du calcul Miss
                PARAMETRE=FACT(
                    statut="f",
                    regles=(
                        PRESENT_PRESENT("OFFSET_MAX", "OFFSET_NB"),
                        PRESENT_PRESENT("FREQ_MIN", "FREQ_MAX", "FREQ_PAS"),
                        EXCLUS("FREQ_MIN", "LIST_FREQ", "FREQ_IMAG"),
                    ),
                    FREQ_MIN=SIMP(statut="f", typ="R"),
                    FREQ_MAX=SIMP(statut="f", typ="R"),
                    FREQ_PAS=SIMP(statut="f", typ="R"),
                    LIST_FREQ=SIMP(statut="f", typ="R", max="**"),
                    FREQ_IMAG=SIMP(statut="f", typ="R"),
                    Z0=SIMP(statut="f", typ="R", defaut=0.0),
                    TYPE=SIMP(statut="f", typ="TXM", into=("BINAIRE", "ASCII"), defaut="ASCII"),
                    ALLU=SIMP(statut="f", typ="R", defaut=0.0),
                    SURF=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                    DREF=SIMP(statut="f", typ="R"),
                    OFFSET_MAX=SIMP(statut="f", typ="R"),
                    OFFSET_NB=SIMP(statut="f", typ="I"),
                    AUTO=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                    b_auto_harm=BLOC(
                        condition="""equal_to("AUTO", 'OUI')""",
                        OPTION_DREF=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                        OPTION_RFIC=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                        RFIC=SIMP(statut="f", typ="R"),
                        SPEC_MAX=SIMP(statut="f", typ="R"),
                        SPEC_NB=SIMP(statut="f", typ="I"),
                        COEF_OFFSET=SIMP(statut="f", typ="I", defaut=12),
                    ),
                    b_noauto_harm=BLOC(
                        condition="""equal_to("AUTO", 'NON')""",
                        regles=(PRESENT_PRESENT("SPEC_MAX", "SPEC_NB"),),
                        ALGO=SIMP(statut="f", typ="TXM", into=("DEPL", "REGU")),
                        RFIC=SIMP(statut="f", typ="R", defaut=0.0),
                        SPEC_MAX=SIMP(statut="f", typ="R"),
                        SPEC_NB=SIMP(statut="f", typ="I"),
                    ),
                ),
            ),
        ),  # end b_iss_harm
        b_ifs_harm=BLOC(
            condition="""equal_to("IFS", 'OUI')""",
            FORC_AJOU=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_INTERF=SIMP(
                statut="o", typ=grma, max="**", fr=tr("Groupe de mailles de l'interface")
            ),
            GROUP_MA_FLUIDE=SIMP(statut="o", typ=grma, max="**", fr=tr("Groupe de mailles fluide")),
            MODELISATION_FLU=SIMP(statut="o", typ="TXM", into=("3D", "COQUE")),
            RHO_FLUIDE=FACT(
                statut="o",
                regles=(UN_PARMI("TOUT", "GROUP_MA", "MAILLE"),),
                RHO=SIMP(statut="o", typ="R"),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
                MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
            ),
            PRESSION_FLU_IMPO=FACT(
                statut="o",
                PRES_FLUIDE=SIMP(statut="o", typ="R"),
                GROUP_NO=SIMP(statut="o", typ=grno, max="**"),
            ),
        ),  # end b_ifs_harm
    ),  # end b_harm_gene
    b_tran_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'GENE')""",
        regles=EXCLUS("ISS", "IFS"),
        ISS=SIMP(statut="f", typ="TXM", into=("OUI",)),
        IFS=SIMP(statut="f", typ="TXM", into=("OUI",)),
        b_no_ifs=BLOC(
            condition="""not exists("IFS")""",
            SOLVEUR=C_SOLVEUR("DYNA_TRAN_MODAL"),
            ENRI_STAT=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            b_param_enri_stat=BLOC(
                condition="""equal_to("ENRI_STAT", 'OUI')""",
                ORTHO=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                FREQ_COUP_STAT=SIMP(statut="f", typ="R"),
            ),
        ),
        b_iss_tran=BLOC(
            condition="""equal_to("ISS", 'OUI')""",
            regles=(
                AU_MOINS_UN("ACCE_X", "ACCE_Y", "ACCE_Z", "DEPL_X", "DEPL_Y", "DEPL_Z"),
                PRESENT_ABSENT("ACCE_X", "DEPL_X", "DEPL_Y", "DEPL_Z"),
                PRESENT_ABSENT("ACCE_Y", "DEPL_X", "DEPL_Y", "DEPL_Z"),
                PRESENT_ABSENT("ACCE_Z", "DEPL_X", "DEPL_Y", "DEPL_Z"),
            ),
            VERSION_MISS=SIMP(
                statut="f",
                typ="TXM",
                into=("V6.6", "V6.5"),
                defaut="V6.6",
                fr=tr("Version de Miss utilisée"),
            ),
            CALC_IMPE_FORC=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
            GROUP_MA_INTERF=SIMP(
                statut="o", typ=grma, max="**", fr=tr("Groupe de mailles de l'interface")
            ),
            GROUP_NO_INTERF=SIMP(
                statut="o", typ=grno, max="**", fr=tr("Groupe de noeuds de l'interface")
            ),
            TYPE_MODE=SIMP(
                statut="f",
                typ="TXM",
                into=("PSEUDO", "CRAIG_BAMPTON", "INTERF"),
                defaut="CRAIG_BAMPTON",
            ),
            b_nb_mode_interf=BLOC(
                condition="""equal_to("TYPE_MODE",'INTERF')""",
                NB_MODE_INTERF=SIMP(statut="o", typ="I"),
            ),
            b_not_calc_impe_forc=BLOC(
                condition="""equal_to("CALC_IMPE_FORC", 'NON')""",
                UNITE_RESU_IMPE=SIMP(
                    statut="o",
                    typ=UnitType(),
                    inout="in",
                    fr=tr("Unité logique des impédances écrites par Miss"),
                ),
                UNITE_RESU_FORC=SIMP(
                    statut="o",
                    typ=UnitType(),
                    inout="in",
                    fr=tr("Unité logique des forces sismiques écrites par Miss"),
                ),
            ),
            b_calc_impe_forc=BLOC(
                condition="""equal_to("CALC_IMPE_FORC", 'OUI')""",
                regles=(EXCLUS("TABLE_SOL", "MATER_SOL"),),
                UNITE_IMPR_ASTER=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité des résultats transmis par Code_Aster à Miss"),
                ),
                UNITE_RESU_IMPE=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité logique des impédances écrites par Miss"),
                ),
                UNITE_RESU_FORC=SIMP(
                    statut="f",
                    typ=UnitType(),
                    inout="out",
                    fr=tr("Unité logique des forces sismiques écrites par Miss"),
                ),
                TABLE_SOL=SIMP(
                    statut="f", typ=table_sdaster, fr=tr("Table des propriétés du sol stratifié")
                ),
                MATER_SOL=FACT(
                    statut="f",
                    fr=tr("Propriétés du sol homogène"),
                    E=SIMP(statut="o", typ="R", val_min=0.0),
                    NU=SIMP(statut="o", typ="R", val_min=-1.0, val_max=0.5),
                    RHO=SIMP(statut="o", typ="R", val_min=0.0),
                    AMOR_HYST=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0),
                ),
                # Paramètres du calcul Miss
                PARAMETRE=FACT(
                    statut="f",
                    regles=(
                        PRESENT_PRESENT("OFFSET_MAX", "OFFSET_NB"),
                        PRESENT_PRESENT("FREQ_MIN", "FREQ_MAX", "FREQ_PAS"),
                        UN_PARMI("FREQ_MIN", "LIST_FREQ", "FREQ_IMAG"),
                    ),
                    FREQ_MIN=SIMP(statut="f", typ="R"),
                    FREQ_MAX=SIMP(statut="f", typ="R"),
                    FREQ_PAS=SIMP(statut="f", typ="R"),
                    LIST_FREQ=SIMP(statut="f", typ="R", max="**"),
                    FREQ_IMAG=SIMP(statut="f", typ="R"),
                    Z0=SIMP(statut="f", typ="R", defaut=0.0),
                    TYPE=SIMP(statut="f", typ="TXM", into=("BINAIRE", "ASCII"), defaut="ASCII"),
                    ALLU=SIMP(statut="f", typ="R", defaut=0.0),
                    SURF=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                    DREF=SIMP(statut="f", typ="R"),
                    OFFSET_MAX=SIMP(statut="f", typ="R"),
                    OFFSET_NB=SIMP(statut="f", typ="I"),
                    AUTO=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                    b_auto_tran=BLOC(
                        condition="""equal_to("AUTO", 'OUI')""",
                        OPTION_DREF=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                        OPTION_RFIC=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
                        RFIC=SIMP(statut="f", typ="R"),
                        SPEC_MAX=SIMP(statut="f", typ="R"),
                        SPEC_NB=SIMP(statut="f", typ="I", defaut=16384),
                        COEF_OFFSET=SIMP(statut="f", typ="I", defaut=12),
                    ),
                    b_noauto_tran=BLOC(
                        condition="""equal_to("AUTO", 'NON')""",
                        regles=(PRESENT_PRESENT("SPEC_MAX", "SPEC_NB"),),
                        ALGO=SIMP(statut="f", typ="TXM", into=("DEPL", "REGU")),
                        RFIC=SIMP(statut="f", typ="R", defaut=0.0),
                        SPEC_MAX=SIMP(statut="f", typ="R"),
                        SPEC_NB=SIMP(statut="f", typ="I"),
                    ),
                ),
            ),
            ACCE_X=SIMP(statut="f", typ=fonction_c),
            ACCE_Y=SIMP(statut="f", typ=fonction_c),
            ACCE_Z=SIMP(statut="f", typ=fonction_c),
            DEPL_X=SIMP(statut="f", typ=fonction_c),
            DEPL_Y=SIMP(statut="f", typ=fonction_c),
            DEPL_Z=SIMP(statut="f", typ=fonction_c),
        ),  # end b_iss_tran
        b_ifs_tran=BLOC(
            condition="""equal_to("IFS", 'OUI')""",
            FORC_AJOU=SIMP(statut="f", typ="TXM", into=("OUI",)),
            GROUP_MA_INTERF=SIMP(
                statut="o", typ=grma, max="**", fr=tr("Groupe de mailles de l'interface")
            ),
            GROUP_MA_FLUIDE=SIMP(statut="o", typ=grma, max="**", fr=tr("Groupe de mailles fluide")),
            MODELISATION_FLU=SIMP(statut="o", typ="TXM", into=("3D", "COQUE")),
            RHO_FLUIDE=FACT(
                statut="o",
                regles=(UN_PARMI("TOUT", "GROUP_MA"),),
                RHO=SIMP(statut="o", typ="R"),
                TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
                GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
            ),
            PRESSION_FLU_IMPO=FACT(
                statut="o",
                PRES_FLUIDE=SIMP(statut="o", typ="R"),
                GROUP_NO=SIMP(statut="o", typ=grno, max="**"),
            ),
        ),  # end b_ifs_tran
        b_comportement=BLOC(
            condition="""not exists("ISS") and not exists("IFS")""",
            COMPORTEMENT=C_COMPORTEMENT_DYNA("DYNA_LINE"),
        ),
    ),  # end b_tran_gene
)
