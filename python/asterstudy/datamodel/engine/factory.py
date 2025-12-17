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
Engine factory
--------------

Provide functions to create the runner objects according to the configuration
and the job properties.

"""


import os

from ...common import translate


class Engine:
    """Enumerator for the different types of engine."""
    Simulator = 0x01
    AsRun = 0x02
    Salome = 0x04
    Direct = 0x08
    Yacs = 0x10

    # If revert to AsRun by default, see changeset 2e851e61bfe3 to restore
    # a relevant message about the job output
    Default = Simulator if os.getenv('ASTERSTUDY_SIMULATOR') else Salome

    @staticmethod
    def name(engine):
        """Return a name of an Engine."""
        return {
            Engine.Simulator: "Simulator",
            Engine.AsRun: "AsRun",
            Engine.Salome: "Salome",
            Engine.Direct: "Direct",
            Engine.Yacs: "Yacs",
        }[engine]

def _select_engine(engine):
    """Select the proper engine type."""
    if engine & Engine.Simulator:
        from .simulator import Simulator, SimulatorInfos
        return Simulator, SimulatorInfos

    if engine & Engine.AsRun:
        from .asrun_runner import AsRun, AsRunInfos
        return AsRun, AsRunInfos

    if engine & Engine.Salome:
        from .salome_runner import Salome, SalomeInfos
        return Salome, SalomeInfos

    if engine & Engine.Direct:
        from .direct_runner import Direct, DirectInfos
        return Direct, DirectInfos

    if engine & Engine.Yacs:
        from .yacs_runner import Yacs, YacsInfos
        return Yacs, YacsInfos

    raise TypeError(translate('Runner',
                              "Unknown engine type: {0}").format(engine))

def runner_factory(engine=None, **kwargs):
    """Return the proper runner instance."""
    if engine is None:
        engine = Engine.Default
    if kwargs.get("case") and kwargs["case"].use_yacs:
        engine = Engine.Yacs
    class_ = _select_engine(engine)[0]
    return class_(**kwargs)


def serverinfos_factory(engine=None, **kwargs):
    """Return the proper server informations instance."""
    if engine is None:
        engine = Engine.Default
    class_ = _select_engine(engine)[1]
    return class_(**kwargs)


def init_default_engine(engine):
    """Init default engine."""
    assert engine in (Engine.Simulator, Engine.AsRun, Engine.Salome,
                      Engine.Direct)
    Engine.Default = Engine.Simulator \
        if os.getenv('ASTERSTUDY_SIMULATOR') else engine
