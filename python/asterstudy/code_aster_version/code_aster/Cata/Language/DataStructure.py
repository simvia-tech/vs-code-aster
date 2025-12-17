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

"""
DataStructure object for syntax checking
----------------------------------------

It is not important to use the real class (defined with pybind11).
pybind11 objects must defined a ``getType()`` function that is compared to
the return of the class method ``getType()`` of datastructures.
This *light* definition of ``DataStructure`` is essential to be be used in
graphical interfaces such as *AsterStudy*.

Example:

.. code-block:: python

    maillage_sdaster.getType() == Mesh().getType() == "MAILLAGE"

All types used in the catalogs of commands are inherited from this *light*
``DataStructure`` object.
"""

import warnings
from collections import UserDict
from copy import deepcopy


class DataStructure:
    """Base class for all datastructures"""

    _deepcopy_callback = None

    @classmethod
    def getType(cls):
        """Return the type of DataStructure"""
        # use for static checking (with fake datastructures)
        return cls.__name__.upper()

    @classmethod
    def getSubtypes(cls):
        """Return the type of DataStructure and all its subtypes."""
        types = [cls.getType()]
        for subclass in cls.__subclasses__():
            types.extend(subclass.getSubtypes())
        return types

    @classmethod
    def register_deepcopy_callback(cls, callback):
        """Register *callback* to be called in place of the default method.

        Register *None* to revert to default.

        Arguments:
            callback (callable): Function to call with signature:
                (*DataStructure* instance, ``memodict``).
        """
        cls._deepcopy_callback = callback

    def __deepcopy__(self, memodict):
        """Call the default *__deepcopy__* implementation or the previously
        defined callback."""
        if DataStructure._deepcopy_callback is not None:
            copied = DataStructure._deepcopy_callback(self, memodict)
        else:
            copied = self.__class__()
            memodict[id(self)] = copied
            for (k, v) in list(self.__dict__.items()):
                copied.__dict__[k] = deepcopy(v, memodict)
        return copied

    # for compatibility in sdprod functions
    def is_typco(self):
        """Tell if it is an auxiliary result."""
        return False


def AsType(obj):
    """Return the type of `obj`"""
    # AsterStudy Command objects: return the underlying DataStructure
    if hasattr(obj, "gettype"):
        try:
            return obj.gettype()
        except:
            return
    # pybind11 objects: return a name to find the DataStructure class
    elif hasattr(obj, "getType"):
        try:
            typn = obj.getType().lower()
            return globals().get(typn + "_sdaster") or globals().get(typn)
        except:
            return
    elif isinstance(obj, (list, tuple)) and len(obj) > 0:
        return AsType(obj[0])
    return type(obj)


class PythonVariable(UserDict, DataStructure):
    """Generic type for all Python variables, for conversion only in AsterStudy.

    Inheritance from dict allows to support item assignement,
    indexing... often used for Python variable in a code_aster commands
    file.
    """

    @classmethod
    def getType(cls):
        """A Python variable"""
        return "misc"

    def __hash__(self):
        """Indexing support"""
        return id(self)

    def __eq__(self, other):
        """Compare two objects."""
        return self is other

    def __lt__(self, other):
        """Comparison will be relevant when it will become a Variable"""
        warnings.warn("Comparing 'PythonVariable' may return unexpected results", RuntimeWarning)
        return True

    def __gt__(self, other):
        """Comparison will be relevant when it will become a Variable"""
        warnings.warn("Comparing 'PythonVariable' may return unexpected results", RuntimeWarning)
        return True

    def __repr__(self):
        return "<PythonVariable at 0x{:x}>".format(id(self))


class ValueCheckMixing:
    @staticmethod
    def checkValue(value):
        # None means undefined: type is valid
        if value is None:
            return True

        # AsterStudy: for PythonVariable
        if isinstance(value, PythonVariable):
            # can not be checked now, it will be when it will become a Variable
            return True


class UnitBaseType(ValueCheckMixing):
    """Abstract class for type of  *UNITE* keywords."""

    filter_arg = ()

    @classmethod
    def filter_extensions(cls):
        """Return the extensions for filtering."""
        return cls.filter_arg

    @staticmethod
    def value(value):
        if isinstance(value, int):
            return value

        return list(value.keys())[0]

    @staticmethod
    def checkValue(value):
        if ValueCheckMixing.checkValue(value):
            return True

        if isinstance(value, int):
            return True

        if not isinstance(value, dict):
            return False

        if len(value) != 1:
            return False

        if not isinstance(list(value.keys())[0], int):
            return False

        if not isinstance(list(value.values())[0], str):
            return False

        return True

    @staticmethod
    def checkInto(value, into):
        return UnitBaseType.value(value) in into

    @staticmethod
    def checkMax(value, valMax):
        return UnitBaseType.value(value) <= valMax

    @staticmethod
    def checkMin(value, valMin):
        return valMin <= UnitBaseType.value(value)


class UnitDefault(UnitBaseType):
    """The default class without any filter."""


class UnitMed(UnitBaseType):
    """The type for MED files."""

    filter_arg = ("*.med", "*.mmed", "*.rmed")


class UnitAster(UnitBaseType):
    """The type for Aster files."""

    filter_arg = ("*.mail",)


def UnitType(filter=None):

    """*Factory* of the type of *UNITE* keywords.

    Arguments:
        filter (str): Can be used to pass a filter or an expected filetype.
    """
    if filter == "aster":
        cls = UnitAster
    elif filter == "med":
        cls = UnitMed
    else:
        cls = UnitDefault
    return cls


# Objects provided by Noyau from Eficas
# keep compatibility with old name ASSD
ASSD = DataStructure


class CO(ASSD):
    pass


class not_checked(ASSD):
    pass


class formule(ASSD):
    pass


class formule_c(formule):
    pass


# Objects provided in the header of cata.py
class GEOM:
    @classmethod
    def getType(cls):
        """Return the type of DataStructure"""
        return "TX"


class grma(GEOM):
    pass


class grno(GEOM):
    pass


class ma(GEOM):
    pass


class no(GEOM):
    pass


# To be more consistent with new names
MeshEntity = GEOM


class cabl_precont(ASSD):
    pass


class cara_elem(ASSD):
    pass


class cham_gd_sdaster(ASSD):
    pass


class carte_sdaster(cham_gd_sdaster):
    pass


class cham_elem(cham_gd_sdaster):
    pass


class cham_no_sdaster(cham_gd_sdaster):
    pass


class cham_geom_sdaster(cham_gd_sdaster):
    pass


class cham_mater(ASSD):
    pass


class char_acou(ASSD):
    pass


class char_cine_acou(ASSD):
    pass


class char_cine_meca(ASSD):
    pass


class char_cine_ther(ASSD):
    pass


class char_contact(ASSD):
    pass


class char_cont(ASSD):
    pass


class char_frot(ASSD):
    pass


class char_meca(ASSD):
    pass


class char_ther(ASSD):
    pass


class compor_sdaster(ASSD):
    pass


class compor_mgis(ASSD):
    pass


class corresp_2_mailla(ASSD):
    pass


class entier(ASSD):
    pass


class fiss_xfem(ASSD):
    pass


class fonction_class(ASSD):
    pass


class fonction_sdaster(fonction_class):
    pass


class fonction_c(fonction_class):
    pass


class nappe_sdaster(fonction_class):
    pass


class fond_fissure(ASSD):
    pass


class gfibre_sdaster(ASSD):
    pass


class interf_dyna_clas(ASSD):
    pass


class interspectre(ASSD):
    pass


class list_inst(ASSD):
    pass


class listis_sdaster(ASSD):
    pass


class listr8_sdaster(ASSD):
    pass


class macr_elem_dyna(ASSD):
    pass


class macr_elem_stat(ASSD):
    pass


class maillage_sdaster(ASSD):
    pass


class super_mesh(maillage_sdaster):
    pass


class maillage_p(maillage_sdaster):
    pass


class maillage_partiel(maillage_sdaster):
    pass


class grille_sdaster(maillage_sdaster):
    pass


class squelette(maillage_sdaster):
    pass


class mater_sdaster(ASSD):
    pass


class matr_asse(ASSD):
    pass


class matr_asse_gd(matr_asse):
    pass


class matr_asse_depl_c(matr_asse_gd):
    pass


class matr_asse_depl_r(matr_asse_gd):
    pass


class matr_asse_elim_r(matr_asse_gd):
    pass


class matr_asse_pres_c(matr_asse_gd):
    pass


class matr_asse_pres_r(matr_asse_gd):
    pass


class matr_asse_temp_c(matr_asse_gd):
    pass


class matr_asse_temp_r(matr_asse_gd):
    pass


class matr_asse_gene(ASSD):
    pass


class matr_asse_gene_r(matr_asse_gene):
    pass


class matr_asse_gene_c(matr_asse_gene):
    pass


class matr_elem(ASSD):
    pass


class matr_elem_depl_c(matr_elem):
    pass


class matr_elem_depl_r(matr_elem):
    pass


class matr_elem_pres_c(matr_elem):
    pass


class matr_elem_temp_r(matr_elem):
    pass


class melasflu_sdaster(ASSD):
    pass


class mode_cycl(ASSD):
    pass


class modele_gene(ASSD):
    pass


class modele_sdaster(ASSD):
    pass


class nume_ddl_gene(ASSD):
    pass


class nume_ddl_sdaster(ASSD):
    pass


class nume_ddl_p(nume_ddl_sdaster):
    pass


class reel(ASSD):
    pass


class resultat_sdaster(ASSD):
    pass


class comb_fourier(resultat_sdaster):
    pass


class fourier_elas(resultat_sdaster):
    pass


class fourier_ther(resultat_sdaster):
    pass


class mult_elas(resultat_sdaster):
    pass


class mode_empi(resultat_sdaster):
    pass


class evol_sdaster(resultat_sdaster):
    pass


class evol_char(evol_sdaster):
    pass


class evol_elas(evol_sdaster):
    pass


class evol_noli(evol_sdaster):
    pass


class evol_ther(evol_sdaster):
    pass


class evol_varc(evol_sdaster):
    pass


class dyna_gene(ASSD):
    pass


class dyna_phys(resultat_sdaster):
    pass


class harm_gene(dyna_gene):
    pass


class tran_gene(dyna_gene):
    pass


class acou_harmo(dyna_phys):
    pass


class dyna_harmo(dyna_phys):
    pass


class dyna_trans(dyna_phys):
    pass


class mode_acou(dyna_phys):
    pass


class mode_flamb(dyna_phys):
    pass


class mode_meca(dyna_phys):
    pass


class mode_meca_c(mode_meca):
    pass


class mode_gene(dyna_phys):
    pass


class spectre_sdaster(ASSD):
    pass


class table_sdaster(ASSD):
    pass


class table_fonction(table_sdaster):
    pass


class table_container(table_sdaster):
    pass


class type_flui_stru(ASSD):
    pass


class vect_asse_gene(ASSD):
    pass


class vect_elem(ASSD):
    pass


class vect_elem_depl_r(vect_elem):
    pass


class vect_elem_pres_c(vect_elem):
    pass


class vect_elem_temp_r(vect_elem):
    pass


# dict of objects
class ds_dict(ASSD):
    pass


class evol_ther_dict(ds_dict):
    pass
