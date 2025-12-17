# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Result naming dictionary
------------------------

This module defines a dictionary to name the result produced by a command.

The names are built:

- by direct translation (for example: *model*),

- or by joining type + variant (for example: *reslin* for *result* + *linear*
  and not *linear result*),

- or by abbreviation.


Attributes:
    SD_DICT (dict): SD name dictionary.

"""


__all__ = ["SD_DICT"]


SD_DICT = {
    "acou_harmo": "resacou",
    "cara_elem": "elemprop",
    "carte": "field",
    "cham_elem": "field",
    "cham_gd": "field",
    "cham_mater": "fieldmat",
    "cham_no": "field",
    "char_acou": "load",
    "char_cine_acou": "load",
    "char_cine_meca": "load",
    "char_cine_ther": "load",
    "char_contact": "contact",
    "char_meca": "load",
    "char_ther": "load",
    "compor": "behav",
    "dyna_harmo": "resharm",
    "dyna_trans": "restran",
    "entier": "var",
    "evol_char": "loadtran",
    "evol_elas": "reslin",
    "evol_noli": "resnonl",
    "evol_ther": "resther",
    "evol_varc": "statvars",
    "fiss_xfem": "xfem",
    "fonction_c": "func",
    "fonction": "func",
    "fond_fiss": "crack",
    "formule": "formula",
    "gfibre": "fiber",
    "grille": "grid",
    "harm_gene": "resharm",
    "interspectre": "spec",
    "list_inst": "times",
    "listis": "listint",
    "listr8": "listr",
    "macr_elem_dyna": "macrelem",
    "macr_elem_stat": "macrelem",
    "maillage": "mesh",
    "mater": "mater",
    "matr_asse_depl_c": "matrass",
    "matr_asse_depl_r": "matrass",
    "matr_asse_gd": "matrass",
    "matr_asse_gene_c": "matrass",
    "matr_asse_gene": "matrass",
    "matr_asse_gene_r": "matrass",
    "matr_asse": "matrass",
    "matr_asse_pres_c": "matrass",
    "matr_asse_pres_r": "matrass",
    "matr_asse_temp_c": "matrass",
    "matr_asse_temp_r": "matrass",
    "matr_elem_depl_c": "matrelem",
    "matr_elem_depl_r": "matrelem",
    "matr_elem": "matrelem",
    "matr_elem_pres_c": "matrelem",
    "matr_elem_temp_r": "matrelem",
    "mode_acou": "modes",
    "mode_cycl": "modes",
    "mode_empi": "modes",
    "mode_flamb": "modes",
    "mode_gene": "modes",
    "modele_gene": "modes",
    "modele": "model",
    "mode_meca_c": "modes",
    "mode_meca": "modes",
    "mult_elas": "reslin",
    "nappe": "func2d",
    "nume_ddl_gene": "number",
    "nume_ddl": "number",
    "reel": "var",
    "spectre": "spec",
    "table_container": "table",
    "table_fonction": "table",
    "table": "table",
    "tran_gene": "restran",
    "vect_asse_gene": "vectass",
    "vect_elem_depl_r": "vectelem",
    "vect_elem_pres_c": "vectelem",
    "vect_elem_temp_r": "vectelem",
    "vect_elem": "vectelem",
}


# Result name are limited to 8 chars
def _check():
    import keyword
    lkw = dir(__builtins__)
    lkw.extend(keyword.kwlist)

    for name in SD_DICT.values():
        assert len(name) <= 8, "template name too long: {0!r}".format(name)
        assert name not in lkw, "conflict with a reserved name: " \
            "{0!r}".format(name)

_check()
