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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def dyna_vibra_sdprod(BASE_CALCUL, TYPE_CALCUL, MATR_RIGI, **args):
    if args.get("__all__"):
        return (dyna_trans, dyna_harmo, acou_harmo, tran_gene, harm_gene)

    if BASE_CALCUL == "PHYS":
        if TYPE_CALCUL == "TRAN":
            return dyna_trans
        if AsType(MATR_RIGI) == matr_asse_pres_c:
            return acou_harmo
        return dyna_harmo
    else:
        if TYPE_CALCUL == "TRAN":
            return tran_gene
        return harm_gene


DYNA_VIBRA = OPER(
    nom="DYNA_VIBRA",
    op=29,
    sd_prod=dyna_vibra_sdprod,
    reentrant="f:RESULTAT",
    fr=tr("Calcul dynamique transitoire ou harminque, sur base physique ou généralisée"),
    reuse=SIMP(statut="c", typ=CO),
    # Calculation type and basis
    BASE_CALCUL=SIMP(statut="o", typ="TXM", into=("PHYS", "GENE")),
    TYPE_CALCUL=SIMP(statut="o", typ="TXM", into=("HARM", "TRAN")),
    # Physical model information
    b_phys_model=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS')""",
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    ),
    # Dynamic matrices (mass, stiffness, and damping)
    # Physical basis, transient calculation
    b_matr_tran_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'PHYS')""",
        MATR_MASS=SIMP(statut="o", typ=(matr_asse_depl_r)),
        MATR_RIGI=SIMP(statut="o", typ=(matr_asse_depl_r)),
        MATR_AMOR=SIMP(statut="f", typ=(matr_asse_depl_r)),
        OBSERVATION=C_OBSERVATION("DYNAVIBRA"),
        # Modal damping
        AMOR_MODAL=FACT(
            statut="f",
            regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR")),
            AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
            LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
            MODE_MECA=SIMP(statut="o", typ=mode_meca),
            NB_MODE=SIMP(statut="f", typ="I"),
        ),
    ),
    # Reduced (generalized) basis, transient calculation
    b_matr_tran_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'GENE')""",
        regles=(EXCLUS("AMOR_MODAL", "MATR_AMOR")),
        MATR_MASS=SIMP(statut="o", typ=(matr_asse_gene_r)),
        MATR_RIGI=SIMP(statut="o", typ=(matr_asse_gene_r)),
        MATR_AMOR=SIMP(statut="f", typ=(matr_asse_gene_r)),
        VITESSE_VARIABLE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        b_variable=BLOC(
            condition="""equal_to("VITESSE_VARIABLE", 'OUI')""",
            MATR_GYRO=SIMP(statut="o", typ=(matr_asse_gene_r)),
            VITE_ROTA=SIMP(statut="o", typ=(fonction_sdaster, formule)),
            MATR_RIGY=SIMP(statut="f", typ=(matr_asse_gene_r)),
            ACCE_ROTA=SIMP(statut="f", typ=(fonction_sdaster, formule)),
        ),
        # Modal damping
        AMOR_MODAL=FACT(
            statut="f",
            regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR")),
            AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
            LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        ),
        b_constante=BLOC(
            condition="""equal_to("VITESSE_VARIABLE", 'NON')""",
            VITE_ROTA=SIMP(statut="f", typ="R", defaut=0.0e0),
        ),
    ),
    # Physical basis, harmonic (spectral) calculation
    b_matr_harm_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'PHYS')""",
        regles=(EXCLUS("AMOR_MODAL", "MATR_AMOR")),
        MATR_MASS=SIMP(statut="o", typ=(matr_asse_depl_r, matr_asse_pres_c)),
        MATR_RIGI=SIMP(statut="o", typ=(matr_asse_depl_r, matr_asse_depl_c, matr_asse_pres_c)),
        MATR_AMOR=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_pres_c)),
        MATR_IMPE_PHI=SIMP(statut="f", typ=(matr_asse_depl_r)),
        # Modal damping
        AMOR_MODAL=FACT(
            statut="f",
            regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR")),
            AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
            LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        ),
        # Fluid absorbing damping condition
        b_amor_flui=BLOC(
            condition="""exists("MATR_AMOR") and exists("MATR_IMPE_PHI")""",
            AMOR_FLUI=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
        ),
    ),
    # Reduced basis, harmonic calculation
    b_matr_harm_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'GENE')""",
        MATR_MASS=SIMP(statut="o", typ=(matr_asse_gene_r)),
        MATR_RIGI=SIMP(statut="o", typ=(matr_asse_gene_r, matr_asse_gene_c)),
        MATR_AMOR=SIMP(statut="f", typ=(matr_asse_gene_r)),
        MATR_IMPE_PHI=SIMP(statut="f", typ=(matr_asse_gene_r)),
        # Modal damping
        AMOR_MODAL=FACT(
            statut="f",
            regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR")),
            AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
            LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        ),
        # Fluid absorbing damping condition
        b_amor_flui=BLOC(
            condition="""exists("MATR_AMOR") and exists("MATR_IMPE_PHI")""",
            AMOR_FLUI=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
        ),
    ),
    RESULTAT=SIMP(statut="f", typ=(dyna_harmo, harm_gene)),
    # Harmonic calculation parameters
    b_param_harm=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM')""",
        regles=(UN_PARMI("FREQ", "LIST_FREQ"), EXCLUS("NOM_CHAM", "TOUT_CHAM")),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NOM_CHAM=SIMP(
            statut="f", typ="TXM", validators=NoRepeat(), max=3, into=("DEPL", "VITE", "ACCE")
        ),
        TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI",)),
    ),  # end b_param_harm
    # Transient calculation parameters
    b_param_tran=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN')""",
        # 1. Integration schemes
        SCHEMA_TEMPS=FACT(
            statut="d",
            b_gene=BLOC(
                condition="""equal_to("BASE_CALCUL",'GENE')""",
                SCHEMA=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="RUNGE_KUTTA_32",
                    into=(
                        "NEWMARK",
                        "DIFF_CENTRE",
                        "DEVOGE",
                        "ADAPT_ORDRE1",
                        "ADAPT_ORDRE2",
                        "RUNGE_KUTTA_32",
                        "RUNGE_KUTTA_54",
                        "ITMI",
                        "TRBDF2",
                    ),
                ),
                b_newmark=BLOC(
                    condition="""equal_to("SCHEMA", 'NEWMARK')""",
                    BETA=SIMP(statut="f", typ="R", defaut=0.25),
                    GAMMA=SIMP(statut="f", typ="R", defaut=0.5),
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
                    PAS_MINI=SIMP(statut="f", typ="R", val_min=1e-16),
                    PAS_MAXI=SIMP(statut="f", typ="R", val_min=1e-16),
                    NMAX_ITER_PAS=SIMP(statut="f", typ="I", defaut=16, min=0),
                ),
            ),
            b_not_gene=BLOC(
                condition="""not equal_to("BASE_CALCUL",'GENE')""",
                SCHEMA=SIMP(
                    statut="f",
                    typ="TXM",
                    defaut="NEWMARK",
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
                    PAS_LIMI_RELA=SIMP(statut="f", typ="R", defaut=1.0e-6, val_min=0.0),
                    NB_POIN_PERIODE=SIMP(statut="f", typ="I", defaut=50),
                ),
                b_alladapt=BLOC(
                    condition="""is_in("SCHEMA", ('RUNGE_KUTTA_54','RUNGE_KUTTA_32','DEVOGE','ADAPT_ORDRE1','ADAPT_ORDRE2'))""",
                    PAS_MINI=SIMP(statut="f", typ="R", val_min=1e-16),
                    PAS_MAXI=SIMP(statut="f", typ="R", val_min=1e-16),
                    NMAX_ITER_PAS=SIMP(statut="f", typ="I", defaut=16, min=0),
                ),
            ),
        ),  # end fkw_schema_temps
        # 2. Time discretisation
        INCREMENT=FACT(
            statut="o",
            regles=(UN_PARMI("LIST_INST", "PAS"),),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            b_list=BLOC(
                condition="""exists("LIST_INST")""",
                regles=(EXCLUS("INST_FIN", "NUME_FIN"),),
                NUME_FIN=SIMP(statut="f", typ="I"),
                INST_FIN=SIMP(statut="f", typ="R"),
            ),
            PAS=SIMP(statut="f", typ="R", val_min=1e-16),
            b_pas=BLOC(
                condition="""exists("PAS")""",
                INST_INIT=SIMP(statut="f", typ="R"),
                INST_FIN=SIMP(statut="o", typ="R"),
            ),
            VERI_PAS=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        ),  # end fkw_discretisation
    ),  # end b_param_tran
    # 3. Initial state
    b_init_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'GENE')""",
        ETAT_INIT=FACT(
            statut="f",
            max=1,
            regles=(EXCLUS("RESULTAT", "DEPL"), EXCLUS("RESULTAT", "VITE")),
            RESULTAT=SIMP(statut="f", typ=tran_gene),
            b_resu=BLOC(
                condition="""exists("RESULTAT")""",
                regles=(EXCLUS("NUME_ORDRE", "INST_INIT"),),
                NUME_ORDRE=SIMP(statut="f", typ="I"),
                INST_INIT=SIMP(statut="f", typ="R"),
                b_inst_init=BLOC(
                    condition="""exists("INST_INIT")""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            DEPL=SIMP(statut="f", typ=vect_asse_gene),
            VITE=SIMP(statut="f", typ=vect_asse_gene),
        ),
    ),  # end b_init_gene
    b_init_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'PHYS')""",
        ETAT_INIT=FACT(
            statut="f",
            max=1,
            regles=(
                AU_MOINS_UN("RESULTAT", "DEPL", "VITE", "ACCE"),
                PRESENT_ABSENT("RESULTAT", "DEPL", "VITE", "ACCE"),
            ),
            RESULTAT=SIMP(statut="f", typ=dyna_trans),
            b_resu=BLOC(
                condition="""exists("RESULTAT")""",
                regles=(EXCLUS("NUME_ORDRE", "INST_INIT"),),
                NUME_ORDRE=SIMP(statut="f", typ="I"),
                INST_INIT=SIMP(statut="f", typ="R"),
                b_inst_init=BLOC(
                    condition="""exists("INST_INIT")""",
                    CRITERE=SIMP(
                        statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")
                    ),
                    b_prec_rela=BLOC(
                        condition="""(equal_to("CRITERE", 'RELATIF'))""",
                        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
                    ),
                    b_prec_abso=BLOC(
                        condition="""(equal_to("CRITERE", 'ABSOLU'))""",
                        PRECISION=SIMP(statut="o", typ="R"),
                    ),
                ),
            ),
            DEPL=SIMP(statut="f", typ=cham_no_sdaster),
            VITE=SIMP(statut="f", typ=cham_no_sdaster),
            ACCE=SIMP(statut="f", typ=cham_no_sdaster),
        ),
    ),  # end b_init_phys
    # 4. Archiving parameters
    b_dlt_prec=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'TRAN')""",
        ARCHIVAGE=FACT(
            statut="f",
            max=1,
            regles=(EXCLUS("LIST_INST", "INST"),),
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
            PAS_ARCH=SIMP(statut="f", typ="I", min=0),
            LIST_INST=SIMP(statut="f", typ=(listr8_sdaster)),
            INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
            #               CHAM_EXCLU  =     SIMP(statut='f',typ='TXM',validators=NoRepeat(),max=2,into=("DEPL","VITE","ACCE"),),
        ),  # end fkw_archivage
    ),  # end b_not_dlt_prec
    # 5. Energy calculation
    bloc_ener=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS')""",
        ENERGIE=FACT(
            statut="f", max=1, CALCUL=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI")
        ),
    ),  # end b_bloc_ener
    ##########################################################################################
    #       Definition of the external excitation
    #       A. Harmonic case, physical basis
    b_excit_harm_phys=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'PHYS')""",
        regles=(AU_MOINS_UN("EXCIT", "EXCIT_RESU"),),
        EXCIT=FACT(
            statut="f",
            max="**",
            regles=(
                UN_PARMI("VECT_ASSE", "CHARGE"),
                UN_PARMI("FONC_MULT", "FONC_MULT_C", "COEF_MULT", "COEF_MULT_C"),
            ),
            VECT_ASSE=SIMP(statut="f", typ=cham_no_sdaster),
            CHARGE=SIMP(statut="f", typ=(char_meca, char_cine_meca)),
            FONC_MULT_C=SIMP(statut="f", typ=(fonction_c, formule_c)),
            COEF_MULT_C=SIMP(statut="f", typ="C"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            PHAS_DEG=SIMP(statut="f", typ="R", defaut=0.0e0),
            PUIS_PULS=SIMP(statut="f", typ="I", defaut=0),
        ),
        EXCIT_RESU=FACT(
            statut="f",
            max="**",
            RESULTAT=SIMP(statut="o", typ=(dyna_harmo,)),
            COEF_MULT_C=SIMP(statut="o", typ="C"),
        ),
    ),  # end b_excit_harm_phys
    ##########################################################################################
    #       Definition of the external excitation
    #       A. Harmonic case, reduced basis
    b_excit_harm_gene=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'HARM') and equal_to("BASE_CALCUL", 'GENE')""",
        regles=(AU_MOINS_UN("EXCIT", "EXCIT_RESU"),),
        EXCIT=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("FONC_MULT", "FONC_MULT_C", "COEF_MULT", "COEF_MULT_C"),),
            VECT_ASSE_GENE=SIMP(statut="o", typ=vect_asse_gene),
            FONC_MULT_C=SIMP(statut="f", typ=(fonction_c, formule_c)),
            COEF_MULT_C=SIMP(statut="f", typ="C"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            PHAS_DEG=SIMP(statut="f", typ="R", defaut=0.0e0),
            PUIS_PULS=SIMP(statut="f", typ="I", defaut=0),
        ),
        EXCIT_RESU=FACT(
            statut="f",
            max="**",
            RESULTAT=SIMP(statut="o", typ=(harm_gene,)),
            COEF_MULT_C=SIMP(statut="o", typ="C"),
        ),
    ),  # end b_excit_harm_gene
    ##########################################################################################
    #       B. Transient case, physical basis
    b_excit_line_tran=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'PHYS')""",
        EXCIT=FACT(
            statut="f",
            max="**",
            regles=(
                UN_PARMI("CHARGE", "VECT_ASSE"),
                EXCLUS("FONC_MULT", "COEF_MULT"),
                EXCLUS("ACCE", "COEF_MULT"),
                PRESENT_ABSENT("ACCE", "FONC_MULT"),
                PRESENT_PRESENT("ACCE", "VITE", "DEPL"),
            ),
            VECT_ASSE=SIMP(statut="f", typ=cham_no_sdaster),
            CHARGE=SIMP(statut="f", typ=(char_meca, char_cine_meca)),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MULT_APPUI=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
            b_mult_appui=BLOC(
                condition="""equal_to("MULT_APPUI", 'OUI')""",
                DIRECTION=SIMP(statut="f", typ="R", max="**"),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            ),
        ),
        MODE_STAT=SIMP(statut="f", typ=mode_meca),
        EXCIT_RESU=FACT(
            statut="f",
            max="**",
            RESULTAT=SIMP(statut="o", typ=dyna_trans),
            COEF_MULT=SIMP(statut="o", typ="R"),
        ),
    ),  # end b_excit_line_tran
    ##########################################################################################
    #       C. Transient case, reduced basis
    #       C.1 Regular excitation (linear)
    b_excit_tran_mod=BLOC(
        condition="""equal_to("TYPE_CALCUL", 'TRAN') and equal_to("BASE_CALCUL", 'GENE')""",
        regles=(
            PRESENT_ABSENT("MODE_STAT", "MODE_CORR"),
            PRESENT_PRESENT("BASE_ELAS_FLUI", "NUME_VITE_FLUI"),
        ),
        EXCIT=FACT(
            statut="f",
            max="**",
            regles=(
                UN_PARMI("FONC_MULT", "COEF_MULT", "ACCE"),
                UN_PARMI("VECT_ASSE_GENE", "NUME_ORDRE"),
                PRESENT_PRESENT("ACCE", "VITE", "DEPL"),
                EXCLUS("MULT_APPUI", "CORR_STAT"),
                PRESENT_PRESENT("MULT_APPUI", "ACCE"),
            ),
            VECT_ASSE_GENE=SIMP(statut="f", typ=vect_asse_gene),
            NUME_ORDRE=SIMP(statut="f", typ="I"),
            FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            COEF_MULT=SIMP(statut="f", typ="R"),
            ACCE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            VITE=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            DEPL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            MULT_APPUI=SIMP(statut="f", typ="TXM", into=("OUI",)),
            b_mult_appui=BLOC(
                condition="""equal_to("MULT_APPUI", 'OUI')""",
                DIRECTION=SIMP(statut="f", typ="R", max="**"),
                GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
            ),
            CORR_STAT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            b_corr_stat=BLOC(
                condition="""equal_to("CORR_STAT", 'OUI')""",
                D_FONC_DT=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
                D_FONC_DT2=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
            ),
        ),
        MODE_STAT=SIMP(statut="f", typ=mode_meca),
        MODE_CORR=SIMP(statut="f", typ=(mult_elas, mode_meca)),
        EXCIT_RESU=FACT(
            statut="f",
            max="**",
            RESULTAT=SIMP(statut="o", typ=tran_gene),
            COEF_MULT=SIMP(statut="f", typ="R", defaut=1.0),
        ),
        #       C.2   Non-linear excitations
        COMPORTEMENT=C_COMPORTEMENT_DYNA("DYNA_VIBRA"),
        BASE_ELAS_FLUI=SIMP(statut="f", typ=melasflu_sdaster, max=1),
        NUME_VITE_FLUI=SIMP(statut="f", typ="I", max=1),
        VERI_CHOC=FACT(
            statut="f",
            STOP_CRITERE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
            SEUIL=SIMP(statut="f", typ="R", defaut=0.5),
        ),
        #            Implicit or explicit treatment of choc non-linearities in integration
        b_nl_wet=BLOC(
            condition="""exists("BASE_ELAS_FLUI")""",
            TRAITEMENT_NONL=SIMP(statut="f", typ="TXM", defaut="IMPLICITE", into=("IMPLICITE",)),
        ),
        b_nl_dry=BLOC(
            condition="""not exists("BASE_ELAS_FLUI")""",
            TRAITEMENT_NONL=SIMP(
                statut="f", typ="TXM", defaut="EXPLICITE", into=("IMPLICITE", "EXPLICITE")
            ),
        ),
    ),  # end b_excit_tran_mod
    ##########################################################################################
    #       Solver parameters (common catalogue)
    b_sol_harm_gene=BLOC(
        condition="""equal_to("BASE_CALCUL", 'GENE') and equal_to("TYPE_CALCUL", 'HARM')""",
        fr=tr("Methode de resolution matrice generalisee"),
        SOLVEUR=C_SOLVEUR("DYNA_LINE_HARM", "GENE"),
    ),
    b_sol_harm_phys=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'HARM')""",
        fr=tr("Methode de resolution matrice sur ddl physique"),
        SOLVEUR=C_SOLVEUR("DYNA_LINE_HARM", "PHYS"),
    ),
    b_sol_line_tran=BLOC(
        condition="""equal_to("BASE_CALCUL", 'PHYS') and equal_to("TYPE_CALCUL", 'TRAN')""",
        SOLVEUR=C_SOLVEUR("DYNA_LINE_TRAN"),
    ),
    b_sol_tran_gene=BLOC(
        condition="""equal_to("BASE_CALCUL", 'GENE') and equal_to("TYPE_CALCUL", 'TRAN')""",
        SOLVEUR=C_SOLVEUR("DYNA_TRAN_MODAL"),
    ),
    ##########################################################################################
    #       Diverse
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
    b_impression=BLOC(
        condition="""equal_to("BASE_CALCUL", 'GENE') and equal_to("TYPE_CALCUL", 'TRAN')""",
        IMPRESSION=FACT(
            statut="f",
            regles=(
                PRESENT_ABSENT("UNITE_DIS_VISC", "INST_FIN", "INST_INIT", "TOUT", "NIVEAU"),
                PRESENT_ABSENT("UNITE_DIS_ECRO_TRAC", "INST_FIN", "INST_INIT", "TOUT", "NIVEAU"),
            ),
            TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NIVEAU=SIMP(
                statut="f", typ="TXM", into=("DEPL_LOC", "VITE_LOC", "FORC_LOC", "TAUX_CHOC")
            ),
            INST_INIT=SIMP(statut="f", typ="R"),
            INST_FIN=SIMP(statut="f", typ="R"),
            UNITE_DIS_VISC=SIMP(
                statut="f",
                typ=UnitType(),
                fr=tr("Unité de sortie des variables internes pour les DIS_VISC"),
                inout="out",
            ),
            UNITE_DIS_ECRO_TRAC=SIMP(
                statut="f",
                typ=UnitType(),
                fr=tr("Unité de sortie des variables internes pour les DIS_ECRO_TRAC"),
                inout="out",
            ),
        ),
    ),  # end b_impression
)
