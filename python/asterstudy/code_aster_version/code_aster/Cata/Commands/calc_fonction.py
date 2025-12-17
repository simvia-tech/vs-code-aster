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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_fonction_prod(
    self,
    DERIVE,
    EXTRACTION,
    INTEGRE,
    INVERSE,
    COMB,
    COMB_C,
    MULT,
    ENVELOPPE,
    FRACTILE,
    PROL_SPEC_OSCI,
    SPEC_OSCI,
    ASSE,
    FFT,
    COMPOSE,
    CORR_ACCE,
    COHERENCE,
    PUISSANCE,
    LISS_ENVELOP,
    ABS,
    REGR_POLYNOMIALE,
    DSP,
    MOYENNE,
    INTEGRE_FREQ,
    DERIVE_FREQ,
    INTERPOL_FFT,
    **args
):
    if args.get("__all__"):
        return (fonction_sdaster, fonction_c, nappe_sdaster)

    if INTEGRE is not None:
        return fonction_sdaster
    if DERIVE is not None:
        return fonction_sdaster
    if INVERSE is not None:
        return fonction_sdaster
    if COMB is not None:
        type_vale = AsType(COMB[0]["FONCTION"])
        for mcfact in COMB:
            if AsType(mcfact["FONCTION"]) != type_vale:
                raise AsException("CALC_FONCTION/COMB : pas de types hétérogènes nappe/fonction")
        return type_vale
    if COMB_C is not None:
        vale = COMB_C[0]["FONCTION"]
        if AsType(vale) == nappe_sdaster:
            for mcfact in COMB_C[1:]:
                if AsType(mcfact["FONCTION"]) != nappe_sdaster:
                    raise AsException(
                        "CALC_FONCTION/COMB_C : pas de types hétérogènes nappe/fonction"
                    )
            return nappe_sdaster
        else:
            for mcfact in COMB_C:
                if AsType(mcfact["FONCTION"]) == nappe_sdaster:
                    raise AsException(
                        "CALC_FONCTION/COMB_C : pas de types hétérogènes nappe/fonction"
                    )
            return fonction_c
    if ENVELOPPE is not None:
        return AsType(ENVELOPPE[0]["FONCTION"])
    if FRACTILE is not None:
        return AsType(FRACTILE[0]["FONCTION"])
    if MOYENNE is not None:
        return AsType(MOYENNE[0]["FONCTION"])
    if EXTRACTION is not None:
        return fonction_sdaster
    if PROL_SPEC_OSCI is not None:
        return fonction_sdaster
    if SPEC_OSCI is not None:
        if SPEC_OSCI[0]["TYPE_RESU"] == "NAPPE":
            return nappe_sdaster
        else:
            if SPEC_OSCI[0]["AMOR_REDUIT"] is not None:
                if len(SPEC_OSCI[0]["AMOR_REDUIT"]) == 1:
                    return fonction_sdaster
                else:
                    return nappe_sdaster
            else:
                return nappe_sdaster
    if DSP is not None:
        return fonction_sdaster
    if COMPOSE is not None:
        return fonction_sdaster
    if ASSE is not None:
        return fonction_sdaster
    if MULT is not None:
        type_vale = AsType(MULT[0]["FONCTION"])
        for mcfact in MULT:
            if AsType(mcfact["FONCTION"]) != type_vale:
                raise AsException("CALC_FONCTION/MULT : pas de types hétérogènes nappe/fonction")
        return type_vale
    if FFT is not None:
        vale = FFT[0]["FONCTION"]
        if AsType(vale) == fonction_sdaster:
            return fonction_c
        if AsType(vale) == fonction_c:
            return fonction_sdaster
    if INTERPOL_FFT is not None:
        return fonction_sdaster
    if CORR_ACCE is not None:
        return fonction_sdaster
    if COHERENCE is not None:
        return fonction_sdaster
    if LISS_ENVELOP is not None:
        return nappe_sdaster
    if REGR_POLYNOMIALE is not None:
        return fonction_sdaster
    if PUISSANCE is not None:
        return AsType(PUISSANCE[0]["FONCTION"])
    if ABS is not None:
        return fonction_sdaster
    if INTEGRE_FREQ is not None:
        return fonction_sdaster
    if DERIVE_FREQ is not None:
        return fonction_sdaster
    raise AsException("type de concept resultat non prevu")


CALC_FONCTION = MACRO(
    nom="CALC_FONCTION",
    op=OPS("code_aster.MacroCommands.calc_fonction_ops.calc_fonction_ops"),
    sd_prod=calc_fonction_prod,
    fr=tr("Effectue des opérations mathématiques sur des concepts de type fonction"),
    reentrant="n",
    regles=(
        UN_PARMI(
            "DERIVE",
            "INTEGRE",
            "SPEC_OSCI",
            "DSP",
            "FFT",
            "CORR_ACCE",
            "COMB",
            "COMB_C",
            "MULT",
            "ASSE",
            "INVERSE",
            "ABS",
            "ENVELOPPE",
            "COMPOSE",
            "EXTRACTION",
            "PUISSANCE",
            "PROL_SPEC_OSCI",
            "INTEGRE_FREQ",
            "DERIVE_FREQ",
            "LISS_ENVELOP",
            "FRACTILE",
            "REGR_POLYNOMIALE",
            "MOYENNE",
            "COHERENCE",
            "INTERPOL_FFT",
        ),
    ),
    FFT=FACT(
        statut="f",
        fr=tr("Transformée de Fourier ou de son inverse"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c)),
        METHODE=SIMP(
            statut="f", typ="TXM", defaut="PROL_ZERO", into=("PROL_ZERO", "TRONCATURE", "COMPLET")
        ),
        b_syme=BLOC(
            condition=""" is_type("FONCTION")==fonction_c """,
            SYME=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
        ),
    ),
    INTERPOL_FFT=FACT(
        statut="f",
        fr=tr("Interpolation d'un accélérogramme par zero padding"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster)),
        PAS_INST=SIMP(statut="o", typ="R", fr=tr("Nouveau pas d'échantillonnage souhaité")),
        PRECISION=SIMP(
            statut="f",
            typ="R",
            fr=tr("Ecart maximum entre le pas souhaité et le pas calculé"),
            defaut=1e-2,
        ),
    ),
    DERIVE=FACT(
        statut="f",
        fr="Dérivée d une fonction",
        METHODE=SIMP(statut="f", typ="TXM", defaut="DIFF_CENTREE", into=("DIFF_CENTREE",)),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
    ),
    INTEGRE=FACT(
        statut="f",
        fr=tr("Intégrale d'une fonction"),
        METHODE=SIMP(statut="f", typ="TXM", defaut="TRAPEZE", into=("SIMPSON", "TRAPEZE")),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        COEF=SIMP(statut="f", typ="R", defaut=0.0e0, fr=tr("Valeur de la constante d intégration")),
    ),
    LISS_ENVELOP=FACT(
        statut="f",
        fr=tr("Lissage d une enveloppe"),
        regles=(UN_PARMI("NAPPE", "FONCTION", "TABLE"),),
        NAPPE=SIMP(statut="f", typ=nappe_sdaster, max="**"),
        TABLE=SIMP(statut="f", typ=table_sdaster, max="**"),
        FONCTION=SIMP(statut="f", typ=fonction_sdaster, min=1, max=1),
        LIST_AMOR=SIMP(statut="f", typ="R", max="**"),
        OPTION=SIMP(statut="o", typ="TXM", into=("CONCEPTION", "VERIFICATION")),
        b_verif=BLOC(
            condition="""equal_to("OPTION", 'VERIFICATION') """,
            ELARG=SIMP(statut="f", typ="R", max="**", val_min=0.0, val_max=1.0),
        ),
        FREQ_MIN=SIMP(statut="f", typ="R"),
        FREQ_MAX=SIMP(statut="f", typ="R"),
        LIST_FREQ=SIMP(statut="f", typ="R", max="**"),
        NB_FREQ_LISS=SIMP(
            statut="f",
            typ="I",
            max=2,
            val_min=1,
            defaut=(10,),
            fr=tr("Nb de points pour le lissage "),
        ),
        ZPA=SIMP(statut="f", typ="R"),
    ),
    REGR_POLYNOMIALE=FACT(
        statut="f",
        fr=tr("Régression polynomiale d'une fonction"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        DEGRE=SIMP(statut="o", typ="I"),
    ),
    PROL_SPEC_OSCI=FACT(
        statut="f",
        fr=tr("Prolonger un Spectre d'oscillateur par DEPL_MAX"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster, fr=tr("Spectre d'oscillateur")),
        NORME=SIMP(statut="o", typ="R", fr=tr("Valeur de la norme du spectre d oscillateur")),
        DEPL_MAX=SIMP(
            statut="o", typ="R", val_min=0.0, fr=tr("Deplacement maximal pour la prolongation")
        ),
    ),
    SPEC_OSCI=FACT(
        statut="f",
        fr=tr("Spectre d'oscillateur"),
        TYPE_RESU=SIMP(statut="f", typ="TXM", defaut="NAPPE", into=("NAPPE", "FONCTION")),
        METHODE=SIMP(statut="f", typ="TXM", defaut="NIGAM", into=("NIGAM", "HARMO", "RICE")),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", max="**"),
        NORME=SIMP(statut="o", typ="R", fr=tr("Valeur de la norme du spectre d oscillateur")),
        NATURE=SIMP(statut="f", typ="TXM", defaut="ACCE", into=("DEPL", "VITE", "ACCE")),
        b_methode=BLOC(
            condition="""not equal_to("METHODE", 'RICE') """,
            NATURE_FONC=SIMP(statut="f", typ="TXM", defaut="ACCE", into=("ACCE",)),
        ),
        b_rice=BLOC(
            condition="""equal_to("METHODE", 'RICE') """,
            DUREE=SIMP(
                statut="o",
                typ="R",
                val_min=0.0,
                fr=tr("durée de la phase forte pour facteur de pic"),
            ),
            NATURE_FONC=SIMP(statut="f", typ="TXM", defaut="DSP", into=("DSP",)),
        ),
    ),
    DSP=FACT(
        statut="f",
        fr=tr("Densité spectrale"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        AMOR_REDUIT=SIMP(statut="o", typ="R", val_min=0.0, val_max=1.0),
        NORME=SIMP(statut="o", typ="R"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NB_ITER=SIMP(
            statut="f",
            typ="I",
            val_min=0,
            defaut=10,
            fr=tr("nombre d'iterations pour fitter le spectre"),
        ),
        FREQ_FILTRE_ZPA=SIMP(
            statut="f",
            typ="R",
            defaut=0.0,
            val_min=0.0,
            fr=tr("frequence du filtre Butterworth passe-bas"),
        ),
        NB_FREQ_LISS=SIMP(
            statut="f",
            typ="I",
            defaut=0,
            fr=tr("Nb de points pour le lissage par fenêtre de Hamming"),
        ),
        FREQ_PAS=SIMP(statut="f", typ="R"),
        regles=(UN_PARMI("FREQ_PAS", "LIST_FREQ"),),
        FREQ_COUP=SIMP(statut="o", typ="R", fr=tr("fréquence de coupure")),
        DUREE=SIMP(
            statut="o", typ="R", val_min=0.0, fr=tr("durée de la phase forte pour facteur de peak")
        ),
        FRACT=SIMP(statut="f", typ="R", defaut=0.5, val_min=0.0, val_max=1.0, fr=tr("fractile")),
    ),
    ABS=FACT(
        statut="f",
        fr=tr("Valeur absolue d'une fonction"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
    ),
    COMB=FACT(
        statut="f",
        max="**",
        fr=tr("Combinaison linéaire réelle de fonctions"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster)),
        COEF=SIMP(
            statut="o",
            typ="R",
            fr=tr("Coefficient réel de la combinaison linéaire associée à la fonction"),
        ),
    ),
    COMB_C=FACT(
        statut="f",
        max="**",
        fr=tr("Combinaison linéaire complexe de fonctions"),
        regles=(UN_PARMI("COEF_R", "COEF_C"),),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c, nappe_sdaster)),
        COEF_R=SIMP(
            statut="f",
            typ="R",
            fr=tr("Coefficient réel de la combinaison linéaire associée à la fonction"),
        ),
        COEF_C=SIMP(
            statut="f",
            typ="C",
            fr=tr("Coefficient complexe de la combinaison linéaire associée à la fonction"),
        ),
    ),
    MULT=FACT(
        statut="f",
        max="**",
        fr=tr("Produit de fonctions réelles"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, fonction_c, nappe_sdaster)),
    ),
    b_comb=BLOC(
        condition="""exists("COMB") or exists("COMB_C") or exists("REGR_POLYNOMIALE") or exists("MULT")""",
        LIST_PARA=SIMP(statut="f", typ=listr8_sdaster),
    ),
    COMPOSE=FACT(
        statut="f",
        fr=tr("Composition de deux fonctions FONC_RESU(FONC_PARA)"),
        FONC_RESU=SIMP(statut="o", typ=fonction_sdaster),
        FONC_PARA=SIMP(statut="o", typ=fonction_sdaster),
    ),
    EXTRACTION=FACT(
        statut="f",
        fr=tr("Extraction sur une fonction complexe"),
        FONCTION=SIMP(statut="o", typ=fonction_c),
        PARTIE=SIMP(
            statut="o",
            typ="TXM",
            into=("REEL", "IMAG", "MODULE", "PHASE"),
            fr=tr("Partie à extraire"),
        ),
    ),
    ENVELOPPE=FACT(
        statut="f",
        fr=tr("Enveloppe d une famille de fonctions"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster), max="**"),
        CRITERE=SIMP(
            statut="f", typ="TXM", defaut="SUP", into=("SUP", "INF"), fr=tr("Type de l enveloppe")
        ),
    ),
    FRACTILE=FACT(
        statut="f",
        fr=tr("Fractile d une famille de fonctions ou de nappes"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster), max="**"),
        FRACT=SIMP(
            statut="f", typ="R", defaut=1.0, val_min=0.0, val_max=1.0, fr=tr("Valeur du fractile")
        ),
    ),
    MOYENNE=FACT(
        statut="f",
        fr=tr("Moyenne d une famille de fonctions ou de nappes"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster), max="**"),
    ),
    COHERENCE=FACT(
        statut="f",
        fr=tr("Fonction de coherence"),
        NAPPE_1=SIMP(statut="o", typ=(nappe_sdaster)),
        NAPPE_2=SIMP(statut="o", typ=(nappe_sdaster)),
        FREQ_COUP=SIMP(statut="f", typ="R", fr=tr("fréquence de coupure")),
        OPTION=SIMP(
            statut="f",
            typ="TXM",
            defaut="TOUT",
            validators=NoRepeat(),
            into=("DUREE_PHASE_FORTE", "TOUT"),
        ),
        b_option_f=BLOC(
            condition="""equal_to("OPTION", 'DUREE_PHASE_FORTE')""",
            BORNE_INF=SIMP(statut="f", typ="R", defaut=0.05e0, val_min=0.0, val_max=0.5),
            BORNE_SUP=SIMP(statut="f", typ="R", defaut=0.95e0, val_min=0.5, val_max=1.0),
        ),
        NB_FREQ_LISS=SIMP(
            statut="f",
            typ="I",
            defaut=12,
            fr=tr("Nb de points pour le lissage par fenêtre de Hamming"),
        ),
    ),
    ASSE=FACT(
        statut="f",
        fr=tr("Concatenation de fonctions"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster, min=2, max=2),
        SURCHARGE=SIMP(statut="f", typ="TXM", defaut="DROITE", into=("DROITE", "GAUCHE")),
    ),
    CORR_ACCE=FACT(
        statut="f",
        fr=tr("Correction d un accelerogramme reel"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        METHODE=SIMP(statut="o", typ="TXM", into=("FILTRAGE", "POLYNOME")),
        b_corr1=BLOC(
            condition="""equal_to("METHODE", 'FILTRAGE') """,
            FREQ_FILTRE=SIMP(
                statut="f", typ="R", defaut=0.05, val_min=0.0, fr=tr("frequence du filtre temporel")
            ),
        ),
        b_corr2=BLOC(
            condition="""equal_to("METHODE", 'POLYNOME') """,
            CORR_DEPL=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
        ),
    ),
    PUISSANCE=FACT(
        statut="f",
        fr=tr("Fonction élevée à une puissance"),
        FONCTION=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster)),
        EXPOSANT=SIMP(statut="f", typ="I", defaut=1),
    ),
    INVERSE=FACT(
        statut="f", fr=tr("Inverse d'une fonction"), FONCTION=SIMP(statut="o", typ=fonction_sdaster)
    ),
    INTEGRE_FREQ=FACT(
        statut="f",
        fr=tr("Integration frequentielle d un accelerogramme reel"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        NIVEAU=SIMP(statut="f", typ="I", defaut=2, into=(1, 2)),
        FREQ_FILTRE=SIMP(
            statut="f", typ="R", defaut=0.0, val_min=0.0, fr=tr("frequence du filtre temporel")
        ),
        FREQ_COUP=SIMP(statut="o", typ="R", val_min=0.0, fr=tr("frequence de coupure")),
    ),
    DERIVE_FREQ=FACT(
        statut="f",
        fr=tr("Integration frequentielle d un accelerogramme reel"),
        FONCTION=SIMP(statut="o", typ=fonction_sdaster),
        NIVEAU=SIMP(statut="f", typ="I", defaut=2, into=(1, 2)),
        FREQ_COUP=SIMP(
            statut="f", typ="R", defaut=50.0, val_min=0.0, fr=tr("frequence de coupure")
        ),
    ),
    NOM_PARA=SIMP(statut="f", typ="TXM", into=C_PARA_FONCTION()),
    NOM_RESU=SIMP(statut="f", typ="TXM"),
    INTERPOL=SIMP(
        statut="f",
        typ="TXM",
        max=2,
        into=("LIN", "LOG"),
        fr=tr(
            "Type d'interpolation pour les abscisses et les ordonnées de la "
            "fonction ou bien pour le paramètre de la nappe."
        ),
    ),
    PROL_DROITE=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    NOM_PARA_FONC=SIMP(statut="f", typ="TXM", into=C_PARA_FONCTION()),
    INTERPOL_FONC=SIMP(
        statut="f",
        typ="TXM",
        max=2,
        into=("LIN", "LOG"),
        fr=tr("Type d'interpolation pour les abscisses et les ordonnées de la fonction"),
    ),
    PROL_DROITE_FONC=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE_FONC=SIMP(statut="f", typ="TXM", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
