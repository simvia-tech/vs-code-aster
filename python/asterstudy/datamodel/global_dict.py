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
Translation dictionary
----------------------

This module defines a dictionary to translate the commands names and their
keywords.

A translation of a command or keyword name is first searched in the
catalog of the command itself (which depends on the selected version), then in
the global dictionary (defined here and common to all code_aster versions),
and finally the name is returned untranslated if no translation was found.

Attributes:
    GLOBAL_DICT (dict): Global translation dictionary.

"""


__all__ = ["GLOBAL_DICT"]


GLOBAL_DICT = {
    "MAILLAGE": "Mesh",
    "MODELE": "Model",
    "MATER": "Material",
    "COMPOR": "Behavior",
    "AFFE": "Assignement",
    "UNITE": "Filename",
    "OUI": "Yes",
    "NON": "No",
    "INFO": "Verbosity",
    "TOUT": "All",
    "GROUP_MA": "Group of element",
    "SANS_GROUP_MA": "Exclude group of element",
    "SANS_MAILLE": "Exclude element",
    "MAILLE": "Element",
    "GROUP_NO": "Group of node",
    "SANS_NOEUD": "Exclude Node",
    "SANS_GROUP_NO": "Exclude group of node",
    "NOEUD": "Node",
    "CHAM_GD": "Field",
    "EVOL": "Transient value",
    "EVOL_NOLI": "Non linear transient",
    "VALE_REF": "Reference value",
    "E": "Young's modulus",
    "NU": "Poisson's ratio",
    "RHO": "Density",
    "ELAS": "Elastic",
    "THER": "Thermic",
    "LONG_CARA": "Characteristic length",
    "COEF_AMOR": "Damping coeficient",
    "LONGUEUR": "Length",
    "PRESSION": "Pressure",
    "TEMPERATURE": "Temperature",
    "TEMP": "Temperature",
    "TEMP_IMPO": "Enforce Temperature",
    "PHENOMENE": "Phenomenon",
    "MECANIQUE": "Mechanic",
    "THERMIQUE": "Thermic",
    "ACOUSTIQUE": "Acoustic",
    "METHODE": "Method",
    "MODELISATION": "Modelisation",
    "CHAM_MATER": "Material field",
    "SOLVEUR": "Solver",
    "CARA_ELEM": "Structural element characteristic",
    "EXCIT": "Loads",
    "OPTION": "Option",
    "CHARGE": "Load",
    "FONC_MULT": "Multiplier function",
    "TYPE_CHARGE": "Load type",
    "LIST_INST": "Time step list",
    "INST": "Time",
    "INST_FIN": "End time step",
    "TITRE": "Title",
    "PESANTEUR": "Gravitational acceleration",
    "ROTATION": "Rotation",
    "DDL_IMPO": "Enforce DOF",
    "DDL_POUTRE": "Enforce beam's DOF",
    "DIRECTION": "Direction",
    "GRAVITE": "Gravitational constant",
    "VITESSE": "Celerity",
    "ABSCISSE": "X-coordinate",
    "ORDONNEE": "Y-coordinate",
    "VALE": "Value",
    "VALE_C": "Complex Value",
    "VERIF": "Check",
    "NOM_PARA": "Parameter name",
    "NOM_RESU": "Resu_name",
    "INTERPOL": "Interpolation",
    "PROL_GAUCHE": "Left extension",
    "PROL_DROITE": "Right extension",
    "GRANDEUR_CARA": "Characteristic value",
    "ASTER": "Aster",
    "MED": "Med",
    "INCREMENT": "Timestepping",
    "ETAT_INIT": "Initial condition",
    "ARCHIVAGE": "Storing ",
    "CRITERE": "Criterion",
    "PRECISION": "Precision",
    "RESU": "Results",
    "FORMAT": "Format",
    "CONCEPT": "Concept",
    "RESULTAT": "Result",
    "SOUS_TITRE": "Subtitle",

}
