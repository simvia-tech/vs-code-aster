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
EDF servers adapters
--------------------

Implementation of functions specific to EDF servers.

"""


def adapt_parameters(salome_job, jinf):
    """Adapt *JobParameters* depending on server configuration.

    Arguments:
        salome_job (*JobParameters*): SALOME object for the parameters.
        jinf (*JobInfos*): Job informations provided by the GUI.
    """
    # compute memory per node in GB to choose partition
    nbnodes = max(1, jinf.get('nodes'))
    cpu_per_node = 1. * jinf.get('mpicpu') / nbnodes

    memgb = jinf.get('memory') * cpu_per_node / 1024.

    if jinf.get('partition'):
        salome_job.partition = str(jinf.get('partition'))
    else:
        if str(jinf.get('server')) == 'cronos':
            # from cronos.py asrun plugin
            part = "bm"
            if memgb < 64: # 192 GB available on nodes but without disk
                part = "cn"
            # with this fil"ter, we do not use cn nodes with 384 GB
            if memgb > 300: # for 384 GB and 768 GB nodes
                part = "bm"
            if memgb > 700: # for 6 TB
                part = "tm"
            salome_job.partition = str(part)

        elif str(jinf.get('server')) == 'gaia':
            # noms des partitions sur eole : 'cn' , 'bm'
            part = "cn"
            if memgb > 180: # for 384
                part = "bm"
            salome_job.partition = str(part)

    if jinf.get('qos'):
        salome_job.queue = str(jinf.get('qos'))

    if jinf.get('mpicpu') > 1:
        salome_job.exclusive = True
