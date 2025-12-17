# -*- coding: utf-8 -*-

# Copyright 2023 EDF R&D
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

# pylint: disable=too-many-locals

"""
Utility functions for parsing and manipulating post-processing
concept in AsterStudy application.
"""

from collections import OrderedDict

from .config import DEBUG, FIELD_LABELS


def parse_file(source, aster=True):
    """
    Reads brut pvsimple information regarding the input med file
    and creates a dictionnary of available outputs based on the
    med file information.

    Note this is adapted from
    PARAVIS_V9_3_0/bin/salome/test/MEDReader/testMEDReader10.py
    """
    # Get the array/support type separator, ex. @@][@@
    sep = source.GetProperty('Separator').GetData()

    # Get complete PV identifiers
    # ex. ['TS0/MAIL/ComSup0/RESU____SIEF_ELGA@@][@@GAUSS', ...]
    keys = source.GetProperty("FieldsTreeInfo")[::2]

    series = [':'.join(key.split("/")[:3]) for key in keys]
    fidents = {}
    for serie, key in zip(series, keys):
        if serie not in fidents:
            fidents[serie] = []
        fidents[serie].append(key)

    # List all the names of the arrays, including their mesh support type.
    # Note that an array name includes both the concept and field name for
    # most code_aster results.
    # ---------------------------------------------------------------------
    # Ex. array  : >RESU____SIEF_ELGA<
    #     concept: >RESU<
    #     field  : >SIEF_ELGA<
    meshes = [key.split("/")[1] for key in keys]
    arrays_and_discs = [key.split("/")[-1] for key in keys]

    arrays = [ans.split(sep)[0] for ans in arrays_and_discs]
    discs = [ans.split(sep)[-1] for ans in arrays_and_discs]

    output = OrderedDict()
    for key, array, disc, mesh, serie in zip(keys, arrays, discs, meshes, series):
        if aster:
            concept, field = get_aster_concept(array)
        else:
            concept, field = '<root>', array + ''

        if not concept in output:
            output[concept] = OrderedDict()

        output[concept][field] = {'pv-key': key,
                                  'pv-fident': fidents[serie],
                                  'pv-aident': array,
                                  'support': equivalent_support(disc),
                                  'disc': disc,
                                  'components': get_components(source, array, fidents[serie], disc),
                                  'label': field_label(field),
                                  'mesh': mesh
                                  }
    return output


def get_aster_concept(array):
    """
    Given an array name, determine the code_aster concept
    and field name. Returns <root> for fields printed out
    without their concept name.
    """
    rtu = remove_trailing_underscore
    if len(array) <= 8:
        return '<root>', rtu(array)

    raw8chars = array[:8]
    nextchars = array[8:]
    if nextchars.upper() == nextchars:
        return rtu(raw8chars), rtu(nextchars)

    return '<root>', rtu(array)


def get_components(source, array, keys, disc):
    """
    Returns the available components for a given array
    belonging to a PV proxy/source
    """
    # Select the PV key corresponding to the chosen array

    # Tick the relevant identifiers for the input file reader proxy in paraview
    if source.FieldsStatus[0] != keys[0]:
        source.FieldsStatus = keys
        source.UpdatePipeline()

    data = getattr(source, '{}Data'.format(
        disc_to_support(disc)))

    pv_array = None
    nbarrays = data.GetNumberOfArrays()
    for i in range(nbarrays):
        pv_array = data.GetArray(i)
        if pv_array.Name == array:
            break

    if not pv_array:
        print('Error obtaining components of', array, keys, disc)
        return []

    if not pv_array.Name == array:
        return []

    nbcomp = pv_array.GetNumberOfComponents()

    comps = [None] * nbcomp
    for i in range(nbcomp):
        compname = pv_array.GetComponentName(i)
        comps[i] = compname if compname else 'Scalar'

    return comps


def disc_to_support(disc):
    """
    Converts the raw discretisation support (P0, P1, GAUSS)
    to the equivalent support for Data information for ex.
    Point, Cell, or Field
    """
    if disc in ['GSSNE', 'GAUSS']:
        return 'Field'
    if disc == 'P0':
        return 'Cell'
    return 'Point'


def equivalent_support(disc):
    """
    Converts the raw discretisation support (P0, P1, GAUSS)
    to the equivalent support considering the future application
    of filters in the representations.
    For example, a GAUSS discretisation is referenced here
    as CELLS, GSSNE as POINTS, P* as POINTS.
    """
    supp = disc_to_support(disc)
    if supp == 'Field':
        if disc == 'GAUSS':
            return 'CELLS'
        return 'POINTS'
    return supp.upper() + 'S'


def remove_trailing_underscore(sname):
    """Removes trailing underscores in strings longer than 2 chars"""
    if len(sname) < 2:
        return sname
    proceed = (len(sname) > 1) and (sname[-1] == '_')
    while proceed:
        sname = sname[:-1]
        proceed = False
        if len(sname) > 1:
            if sname[-1] == '_':
                proceed = True
    return sname


def field_label(aster_field):
    """
    Return a nicer label for a given aster-named field
    """
    if aster_field in FIELD_LABELS:
        return FIELD_LABELS[aster_field]
    return aster_field


def colorbar_title(flabel, component):
    """
    Return a nicer color bar title for a given
    aster-named field and colored component
    """
    if component == 'Scalar':
        return flabel.split('(')[0]

    return "%s - %s" % (flabel.split('(')[0], component)


def fetch_source(source):
    """
    Returns a single block source brut PV data from a
    given source
    """
    import pvsimple as pvs
    fetched = pvs.servermanager.Fetch(source)

    # Select the initial block in the case of a
    # multi blocks structure
    if hasattr(fetched, 'GetBlock'):
        fetched = fetched.GetBlock(0)

    return fetched


def get_array_data(source, arrname, atype='point', fetched=None):
    """
    Return the brut array data after extracting the information
    from a multi-block data set and filtering the existing
    arrays.
    """
    if not fetched:
        fetched = fetch_source(source)

    # Extract the point, cell, or field data
    data = getattr(fetched, 'Get%sData' % (atype.title()))()

    nbarr = data.GetNumberOfArrays()
    array = None
    for arr in range(nbarr):
        if data.GetArrayName(nbarr - arr - 1) == arrname:
            array = data.GetArray(nbarr - arr - 1)
            break
    if not array:
        dbg_print("No %sData array of name %s found "
                  "in source %s" % (atype.title(), arrname, source))
        return None
    return array


def get_full_array_range(source, arrname, comp, atype='point'):
    """
    Retrieve the array range for a component (compname) over all the
    data steps available.

    Note: comp = -1 is a shortcut to obtain the magnitude value range.
    """
    import pvsimple as pvs

    # Use a TemporalStatistics filter to obtain the min/max values
    # based on the given source
    tstat = pvs.TemporalStatistics(Input=source)
    tstat.ComputeAverage = 0
    tstat.ComputeStandardDeviation = 0
    tstat.UpdatePipeline()

    minarr = '{}_minimum'.format(arrname)
    maxarr = '{}_maximum'.format(arrname)

    min_min, _ = get_array_range(tstat, minarr, comp, atype)
    _, max_max = get_array_range(tstat, maxarr, comp, atype)

    pvs.Delete(tstat)
    del tstat

    return (min_min, max_max)


def get_array_range(source, arrname, comp, atype='point', fetched=None):
    """
    Retrieve the current value range for a component (compname) in an
    array (arrname) from a source FOR THE CURRENT STEP.

    Source is basically any Paraview pipeline node like a MED file reader, a
    calculator, contour, etc. Type can be point, cell, or field.

    Note: comp = -1 is a shortcut to obtain the magnitude value range.
    """
    array = get_array_data(source, arrname, atype, fetched=fetched)
    if array is None:
        return (0., 0.)

    # print('Inside get_array_range with array = {}; comp = {}'.format(arrname,comp))
    nbcomp = array.GetNumberOfComponents()
    if isinstance(comp, int):
        if comp < nbcomp:
            return array.GetValueRange(comp)
    elif isinstance(comp, (list, tuple)):
        return [array.GetValueRange(c) for c in comp if c in range(nbcomp)]
    elif isinstance(comp, str):
        if comp in ['Magnitude', 'Scalar']:
            comp = 0 if nbcomp == 1 else -1
            return array.GetValueRange(comp)

        for icomp in range(nbcomp):
            if array.GetComponentName(icomp) == comp:
                return array.GetValueRange(icomp)

    dbg_print("Component %s not found in array %s" % (str(comp), arrname))
    return (0., 0.)


def locate_array_min_max(source, arrname, comp, atype='point'):
    """
    Return the value range for a component (compname) in an array
    array (arrname) from a source as well as the position of
    the points where the max is located.
    """
    # Special treatment for colored warp representation
    if arrname.endswith(':TRAN') and comp == -1:
        arrname = arrname.replace(':TRAN', ':MAGTRAN')
        comp = 0

    fetched = fetch_source(source)
    # Note : fetch the source only once as to avoid duplicate operations.
    # call thus get_array_values with the already fetched source
    np_array = get_array_values(source, arrname, comp, atype,
                                fetched=fetched)

    amax_ind, amax = np_array.argmax(), np_array.max()
    amin_ind, amin = np_array.argmin(), np_array.min()

    if atype == 'point':
        pos_cdg = (fetched.GetPoint(amin_ind),
                   fetched.GetPoint(amax_ind))
    elif atype == 'cell':
        # It seems that VTK python access prefers such an explicit
        # access to the cell data, otherwise it really gets mixed up
        minpos = [0., 0., 0.]
        nbp = fetched.GetCell(amin_ind).GetPoints().GetNumberOfPoints()
        for p_id in range(nbp):
            pos_pt = fetched.GetCell(amin_ind).GetPoints().GetPoint(p_id)
            minpos = [pos_pt[i] / nbp + minpos[i] for i in range(3)]

        maxpos = [0., 0., 0.]
        nbp = fetched.GetCell(amax_ind).GetPoints().GetNumberOfPoints()
        for p_id in range(nbp):
            pos_pt = fetched.GetCell(amax_ind).GetPoints().GetPoint(p_id)
            maxpos = [pos_pt[i] / nbp + maxpos[i] for i in range(3)]

        pos_cdg = (minpos, maxpos)

    return (amin, amax), pos_cdg


# pragma pylint: disable=no-member
def get_array_values(source, arrname, comp, atype='point', fetched=None):
    """
    Return a numpy array of the values for a component (compname)
    array (arrname) from a source. Source is basically any Paraview
    pipeline node like a MED file read, a calculator, contour, etc.
    type can be point, cell, or field
    """
    # import numpy support for paraview arrays
    from paraview import numpy_support as ns
    import numpy as np

    array = get_array_data(source, arrname, atype, fetched=fetched)
    if array is None:
        return np.array([])

    nbcomp = array.GetNumberOfComponents()
    # Simple component => just return that
    if nbcomp == 1:
        return ns.vtk_to_numpy(array)

    # Multiple components => search for the user request
    # that can be a component index or name
    if isinstance(comp, int):
        # Component index given
        if comp < nbcomp:
            np_array = ns.vtk_to_numpy(array)
            return np_array[:, comp]
    else:
        # Component name given
        for icomp in range(nbcomp):
            if array.GetComponentName(icomp) == comp:
                np_array = ns.vtk_to_numpy(array)
                return np_array[:, icomp]

    dbg_print("Component %s not found in array %s" % (str(comp), arrname))
    return np.array([])

# pragma pylint: disable=too-many-branches,too-many-statements


def pvcontrol(results, request):
    """
    Main pvsimple view control for common actions available in the
    custom toolbar provided by the results tab above the embedded view
    """
    import pvsimple as pvs

    ren_view = results.ren_view
    if request == 'refresh':
        results.redraw()
        ren_view.Update()
        pvs.UpdatePipeline()
    elif request == 'resetview':
        ren_view.CameraPosition = [-1e5, -5e4, 1e5]
        ren_view.ResetCamera()
        ren_view.CameraFocalPoint = [1.0, 1.0, 0.0]
        ren_view.CameraViewUp = [0.0, 0.0, 1.0]
        ren_view.ResetCamera()
    elif request == 'xproj':
        refpos = [-1e5, 0., 0.]\
            if ren_view.CameraPosition[0] > 0\
            else [1e5, 0., 0.]
        ren_view.CameraPosition = refpos
        ren_view.CameraFocalPoint = [0.0, 0.0, 0.0]
        ren_view.CameraViewUp = [0.0, 0.0, 1.0]
        ren_view.ResetCamera()
    elif request == 'yproj':
        refpos = [0., -1e5, 0.] if ren_view.CameraPosition[1] > 0 else [0., 1e5, 0.]
        ren_view.CameraPosition = refpos
        ren_view.CameraFocalPoint = [0.0, 0.0, 0.0]
        ren_view.CameraViewUp = [0.0, 0.0, 1.0]
        ren_view.ResetCamera()
    elif request == 'zproj':
        refpos = [0., 0., 1e5] if ren_view.CameraPosition[2] < 0 \
            else [0., 0., -1e5]
        ren_view.CameraPosition = refpos
        ren_view.CameraFocalPoint = [0.0, 0.0, 0.0]
        ren_view.CameraViewUp = [0.0, 1.0, 0.0]
        ren_view.ResetCamera()
    elif request == 'ortho_proj':
        prev_proj = ren_view.CameraParallelProjection
        ren_view.CameraParallelProjection = 0 if prev_proj else 1

        #################################################################
        #       T I M E    M A N I P U L A T I O N   C O N T R O L S    #
    elif request in ['tprev', 'tnext']:
        tchange = False
        ctime = ren_view.ViewTime
        available = list(results.current.full_source.TimestepValues)
        cindex = available.index(ctime) if ctime in available else 0
        ctime = available[cindex]
        cindex = cindex + {'tprev': -1, 'tnext': 1}[request]
        if -1 < cindex < len(available):
            ren_view.ViewTime = available[cindex]
            tchange = True
        if results.shown.scene and not 'Mode' in results.shown.name:
            if request == 'tprev':
                results.shown.scene.GoToPrevious()
            else:
                results.shown.scene.GoToNext()
    elif request in ['last']:
        tchange = False
        ctime = ren_view.ViewTime
        last = list(results.current.full_source.TimestepValues)[-1]
        tchange = (ctime != last)
        ren_view.ViewTime = last
        if results.shown.scene and not 'Mode' in results.shown.name:
            results.shown.scene.GoToLast()
    elif request in ['first']:
        tchange = False
        ctime = ren_view.ViewTime
        first = list(results.current.full_source.TimestepValues)[0]
        tchange = (ctime != first)
        ren_view.ViewTime = first
        if results.shown:
            if results.shown.scene and not 'Mode' in results.shown.name:
                results.shown.scene.GoToFirst()
    elif request == 'play':
        results.play_btn.setVisible(False)
        results.pause_btn.setVisible(True)

        # When playing, the color bar and scale are in fact fixed
        # We need to enforce coherence at the end of the playing
        # of the scene
        if results.shown.name != 'Mode Animation':
            if not 'all steps' in results.shown.opts['ColorBarAuto']:
                results.shown.opts['ColorBarAuto'] = 'Custom'

            if 'ScaleFactor' in results.shown.opts:
                results.shown.opts['ScaleFactorAuto'] = False

            results.params.update_params()

        if results.minmax_shown():
            # Unchecking the button results in calling
            # the pvcontrol properly and hiding the
            # min max labels and sources...
            results.minmax_btn.setChecked(False)

        results.shown.animate(play=True)
        results.update_infobar()
        results.play_btn.setVisible(True)
        results.pause_btn.setVisible(False)

    elif request == 'pause':
        if results.shown.scene:
            results.shown.scene.Stop()
        results.play_btn.setVisible(True)
        results.pause_btn.setVisible(False)
        results.update_infobar()
    elif request == 'outline':
        grid = ren_view.AxesGrid
        if grid.Visibility:
            grid.Visibility = 0
        else:
            grid.Visibility = 1
            grid.ShowGrid = 1
            grid.XTitleColor = [0., 0., 0.]
            grid.YTitleColor = [0., 0., 0.]
            grid.ZTitleColor = [0., 0., 0.]
            grid.XLabelColor = [0., 0., 0.]
            grid.YLabelColor = [0., 0., 0.]
            grid.ZLabelColor = [0., 0., 0.]
            grid.GridColor = [0., 0., 0.]
    elif request == 'screenshot':
        save_shot_movie(results, movie=False)
    elif request == 'movie':
        save_shot_movie(results, movie=True)
    elif request == 'min_max':
        from .representation import ModesRep
        if not isinstance(results.shown, ModesRep):
            # Attention the button state refers to that AFTER *
            # the click has occured.
            # If the state is true, we need to shown the min max
            if results.minmax_shown():
                results.min_max_src = show_min_max(results.shown,
                                                   override_opacity=True)
            else:
                pvcontrol(results, 'hide_min_max')
    elif request == 'hide_min_max':
        for source in results.min_max_src:
            pvs.Hide(source, results.ren_view)
        if results.shown:
            if results.shown.opts['Opacity'] == 0.1:
                results.shown.opts['Opacity'] = 1.0
                results.shown.display.Opacity = 1.0
    elif request == 'clear_selection':
        pvs.ClearSelection(results.shown.source)
        text = pvs.FindSource('<PROBE> VALUE LABEL')
        if text:
            pvs.Hide(text, results.shown.ren_view)
        if results.shown.opts['Representation'] == 'Points':
            results.shown.update_({'Representation': 'Surface'})
    elif request == 'reference':
        results.shown.toggle_reference()
    elif request == 'probe':
        pvcontrol(results, 'clear_selection')
        if 'Warp' in results.shown.name:
            support = results.shown.opts['ColorField'].info['support']
        else:
            support = results.shown.field.info['support']

        if support == 'POINTS':
            # Force activation of the points view
            results.shown.opts['Representation'] = 'Points'
            results.params.update_params()
            results.shown.display.Representation = 'Points'
        else:
            # Force activation of the surface view
            results.shown.opts['Representation'] = 'Surface'
            results.params.update_params()
            results.shown.display.Representation = 'Surface'
        pvs.Render()

        key = {'POINTS': 'Select Points On (d)',
               'CELLS': 'Select Cells On (s)'}[support]
        toolbutton = results.toolbuttons[key]
        results.probing = True
        toolbutton.click()

    elif request == 'plot_over_time':
        selection, _, _ = get_active_selection(results.shown.source)
        if not selection:
            support = ('POINTS' if 'Warped' in results.shown.name
                       else results.shown.field.info['support'])
            key = {'POINTS': 'Interactive Select Points On',
                   'CELLS': 'Interactive Select Cells On'}[support]
            toolbutton = results.toolbuttons[key]
            results.probing = False
            toolbutton.click()
        else:
            selection_plot(results)

    elif request == 'rescale_colorbar':
        if hasattr(results.shown, 'update_colorbar'):
            results.shown.opts['ColorBarType'] = 'Continuous'
            results.shown.opts['ColorBarAuto'] = 'Automatic: current step'
            results.shown.update_colorbar(timechange=False)
            results.params.update_params()

    if request in ['tprev', 'tnext', 'first', 'last']:
        if tchange:
            pvs.Render()
            if results.shown:
                results.update_infobar()
                if results.shown.name == 'Mode Animation':
                    # This allows the mode to be recalculated and played
                    results.represent(results.shown.field, results.shown.__class__,
                                      forced=True, **results.shown.opts)
                else:
                    if hasattr(results.shown, 'update_colorbar'):
                        results.shown.update_colorbar(timechange=True)
                        results.params.update_params()

                if results.minmax_shown():
                    show_min_max(results.shown)

    if not request in ['probe', 'plot_over_time']:
        pvs.Render()


def save_movie_callback(fpath, view, scene, frate=1):
    """
    Callback for saving a movie, to be called in a separate thread
    for performance purposes.
    """
    from ..common import wait_cursor

    if scene.PlayMode == 'Real Time':
        # Mode animation, fix a minimum of 15 fps
        frate = max(15, frate)
        fwindow = scene.Duration * frate
    else:
        # Time history
        fwindow = scene.NumberOfFrames

    wait_cursor(True)
    save_animation(fpath, view, scene,
                   FrameWindow=[0, fwindow],
                   FrameRate=frate)
    wait_cursor(False)


def save_shot_movie(results, movie=False):
    """
    Callback to the save screenshot or movie button
    """
    import pvsimple as pvs

    import os.path as osp
    from ..common import get_file_name

    item, ext = 'view', 'png'
    if movie:
        item, ext = 'animation', 'ogv'
        if not results.shown.scene:
            results.shown.animate(play=False)

    dotext = '.' + ext

    docont = True
    fpath = ""
    while docont:
        fpath = get_file_name(0, results.main_window,
                              "Export %s to %s file" % (item, ext), fpath, "*%s" % (dotext))
        docont = False
        if fpath:
            if dotext != osp.splitext(fpath)[-1]:
                fpath = fpath + dotext
                docont = osp.isfile(fpath)


# pragma pylint: disable=too-many-locals


def show_min_max(shown, override_opacity=False):
    """
    Shows minimum and maximum values using a sphere representation
    colored in red color for the max and blue for the min
    """
    import pvsimple as pvs
    import salome
    from .representation import WarpRep, BaseRep

    source = shown.source
    arrname = shown.array
    comp = shown.opts.get('Component', -1)
    comp = -1 if comp == 'Magnitude' else comp

    if isinstance(shown, WarpRep):
        atype = shown.opts['ColorField'].info['support'][:-1].lower()
    else:
        atype = shown.field.info['support'][:-1].lower()  # point or cell

    vals, pos = locate_array_min_max(source, arrname, comp, atype)
    # cols = [(0., 0., 1.), (1., 0., 0.)]  # blue then red; min then max
    cols = [(7./255, 143./255, 1.), (1., 19./255, 151./255)]  # Rainbow colors

    if salome.hasDesktop():
        print('A minimum of %g is located at %s' % (vals[0], pos[0]))
        print('A maximum of %g is located at %s' % (vals[1], pos[1]))

    data_info = source.GetDataInformation().DataInformation
    xmin, xmax, ymin, ymax, zmin, zmax = data_info.GetBounds()
    radius = max([xmax - xmin, ymax - ymin, zmax - zmin]) / 100.

    labels = ['Minimum', 'Maximum']
    text_pos = [[0.01, 0.92], [0.01, 0.95]]
    sources = []
    for i, val in enumerate(vals):
        # False radius only used to allow 2 different spheres
        # to be registered for min and then max
        point_source = BaseRep.register_source(
            'PointSource', 'root',
            Radius=i + 1,
            label='<{}> LOCATOR'.format(labels[i].upper()))

        point_source.Center = pos[i]
        point_source.Radius = radius

        display = pvs.Show(point_source, shown.ren_view)
        display.DiffuseColor = cols[i]
        display.PointSize = 10
        display.Representation = 'Surface'

        text = BaseRep.register_source(
            'Text', 'root', Text=labels[i],
            label='<{}> VALUE LABEL'.format(labels[i].upper()))

        text.Text = '{}: {:E}'.format(labels[i], val)
        display = pvs.Show(text, shown.ren_view)

        display.FontFamily = str('Arial')
        display.FontSize = 12
        display.Color = [c*0.7 for c in cols[i]]
        # display.WindowLocation = str('AnyLocation')
        # display.Position = text_pos[i]
        # display.Bold = 1
        display.Interactivity = 0

        display.TextPropMode = 'Billboard 3D Text'
        display.BillboardPosition = pos[i]
        display.DisplayOffset = [10, 0]
        pvs.Hide3DWidgets(proxy=display)

        sources += [point_source, text]

        shown.ren_view.Update()

    if override_opacity:
        shown.opts['Opacity'] = 0.1
        shown.display.Opacity = 0.1

    if shown.opts['Opacity'] == 0.1:
        shown.hide_reference()

    pvs.Render()
    return sources


def get_active_selection(source):
    """
    Gives the point or cell ids of the active selection.
    """
    is_point = True
    sel_ids = []
    selection_inputs = source.GetSelectionInput(0)

    if not selection_inputs or not selection_inputs.Input:
        return None, [], True

    selection = selection_inputs.Input[0]
    is_point = (selection.FieldType == 'POINT')

    sids = selection.IDs

    if len(sids) < 3:
        return None, [], is_point

    sel_ids = [sids[i] for i in range(2, len(sids), 3)]

    return selection, sel_ids, is_point

# pragma pylint: disable=too-many-locals,no-member


def selection_plot(results):
    """
    Extract data for a single point or cell over time and
    plot the results in a separate window using a specific
    widget
    """
    import pvsimple as pvs
    from paraview import numpy_support as ns
    import numpy as np

    shown = results.shown
    source = shown.source
    selection, sel_ids, is_point = get_active_selection(source)

    if not selection:
        return

    plot = pvs.PlotSelectionOverTime()
    plot.Input = source
    plot.Selection = selection
    plot.UpdatePipeline()

    fetched = pvs.servermanager.Fetch(plot)
    # Issue 29343 : avoid error when the selection is not valid.
    if fetched is None:
        return

    if hasattr(fetched, 'GetBlock'):
        fetched = fetched.GetBlock(0)

    nbcols = fetched.GetNumberOfColumns()

    pvs.Delete(plot)
    del plot

    field = shown.field if 'Warp' not in shown.name \
        else shown.opts['ColorField']
    comps = field.info['components']
    comp = shown.opts['Component'] if 'Contour' not in shown.name else None
    if ':MAGTRAN' in shown.array:
        comp = None

    if isinstance(comp, str):
        if comp != 'Magnitude':
            comp = comps.index(comp) if len(comps) > 1 else None
        elif 'Warp' not in shown.name:
            comp = None

    search = 'avg({} ({}))'.format(shown.array, comp) if comp is not None \
        else 'avg({})'.format(shown.array)

    to_find = ['Time', search]
    col_ind = {}

    tf_elems = to_find + []
    for col in range(nbcols)[::-1]:
        if not tf_elems:
            break
        for elem in tf_elems:
            if elem == fetched.GetColumnName(col):
                col_ind[elem] = col
                tf_elems.remove(elem)
                break

    if tf_elems:
        dbg_print('{} : not found'.format(tf_elems))
        return

    data = [[], []]
    for i, elem in enumerate(to_find):
        data[i] = ns.vtk_to_numpy(fetched.GetColumn(col_ind[elem]))

    if len(data[0]) < 2:
        data[0] = np.array([data[0][0], data[0][0] + 1e-12])
        data[1] = np.array([data[1][0], data[1][0]])

    variable = shown.opts['Title'] if 'Title' in shown.opts else '-'
    if len(sel_ids) > 1:
        variable = '{}, averaged ({} {})'.format(
            variable,
            len(sel_ids),
            ('points' if is_point else 'cells'))

    results.plot(data, variable)


def selection_probe(results):
    """
    Shows minimum and maximum values using a sphere representation
    colored in red color for the max and blue for the min
    """
    import pvsimple as pvs
    from .representation import WarpRep, BaseRep

    shown = results.shown
    source = shown.source
    _, sel_ids, is_point = get_active_selection(source)

    if not sel_ids:
        text = pvs.FindSource('<PROBE> VALUE LABEL')
        if text:
            pvs.Hide(text, shown.ren_view)
            pvs.Render()
        return

    supp = 'point' if is_point else 'cell'

    arrname = shown.array
    comp = shown.opts.get('Component', -1)
    comp = -1 if comp == 'Magnitude' else comp

    if isinstance(shown, WarpRep):
        atype = shown.opts['ColorField'].info['support'][:-1].lower()
    else:
        atype = shown.field.info['support'][:-1].lower()  # point or cell

    if atype != supp:
        dbg_print('Selection support ({}s) is different than \
that of the shown field ({}s)'.format(supp, atype))
        pvs.ClearSelection(shown.source)
        text = pvs.FindSource('<PROBE> VALUE LABEL')
        if text:
            pvs.Hide(text, shown.ren_view)
        pvs.Render()
        return

    np_array = get_array_values(source, arrname, comp, atype)
    vals = np_array[sel_ids]

    if len(sel_ids) == 1:
        text_str = 'Probe value: {:E}'.format(vals[0])
    else:
        text_str = 'Probe  (over {} {}s)\n> Average: {:E}\n'\
                   '> Lower bound: {:E}\n> Upper bound: {:E}'.format(
                       vals.size, supp, vals.mean(),
                       vals.min(), vals.max())

    text = BaseRep.register_source('Text', 'root',
                                   Text='Probe', label='<PROBE> VALUE LABEL')

    text.Text = text_str
    display = pvs.Show(text, shown.ren_view)

    display.FontFamily = str('Arial')
    display.FontSize = 12
    display.Color = (0., 0., 0.)
    display.WindowLocation = str('Lower Right Corner')

    shown.ren_view.Update()
    pvs.Render()


def default_scale(source, array, ratio=0.05):
    """
    Calculates a default scale for a given source and array
    based on the array range and the box size.
    Used for default scaling warp and mode representations.

    5% max deformation seems right...
    """
    ranges = get_array_range(source, array, list(range(3)))
    abs_max = 0.
    for rang in ranges:
        if not isinstance(rang, (list, tuple)):
            rang = [rang]
        abs_max = max([abs(v) for v in rang] + [abs_max])

    if abs_max < 1.e-12:
        return 1.0

    data_info = source.GetDataInformation().DataInformation
    xmin, xmax, ymin, ymax, zmin, zmax = data_info.GetBounds()
    box_dim_max = max([xmax - xmin, ymax - ymin, zmax - zmin])

    return ratio * box_dim_max / abs_max


def save_animation(filename, view_or_layout=None, scene=None, **params):
    """
    Reimplemented paraview SaveAnimation function as there seems to
    be a bug with the frame rate!
    """
    import pvsimple as pvs
    # use active view if no view or layout is specified.
    view_or_layout = view_or_layout if view_or_layout else pvs.GetActiveView()

    if not view_or_layout:
        raise ValueError("A view or layout must be specified.")

    scene = scene if scene else pvs.GetAnimationScene()
    if not scene:
        raise RuntimeError("Missing animation scene.")

    controller = pvs.servermanager.ParaViewPipelineController()
    options = pvs.servermanager.misc.SaveAnimation()
    controller.PreInitializeProxy(options)

    options.AnimationScene = scene
    options.Layout = view_or_layout if view_or_layout.IsA(
        "vtkSMViewLayoutProxy") else None
    options.View = view_or_layout if view_or_layout.IsA("vtkSMViewProxy") else None
    options.SaveAllViews = bool(view_or_layout.IsA("vtkSMViewLayoutProxy"))

    # this will choose the correct format.
    options.UpdateDefaultsAndVisibilities(filename)

    controller.PostInitializeProxy(options)

    # Addition ################################################
    if 'FrameRate' in params:
        options.FrameRate = params['FrameRate']
    ###########################################################

    # explicitly process format properties.
    format_proxy = options.Format
    format_props = format_proxy.ListProperties()
    for prop in format_props:
        if prop in params:
            format_proxy.SetPropertyWithName(prop, params[prop])
            del params[prop]

    pvs.SetProperties(options, **params)
    return options.WriteAnimation(filename)


def mesh_dims_nbno(fpath):
    """
    Returns mesh properties and extracts mesh to a temporary file
    """
    import medcoupling as mc
    import MEDLoader as ml
    dim_geo = mc.MEDCouplingMesh.GetDimensionOfGeometricType
    nbno_geo = mc.MEDCouplingMesh.GetNumberOfNodesOfGeometricType

    dim_nbno = []

    meshes = list(ml.GetMeshNames(fpath))
    if meshes:
        if len(meshes) > 1:
            print('Only parsing the first mesh in file')
        mesh = ml.MEDFileMesh.New(fpath, meshes[0])
        geo_types = mesh.getAllGeoTypes()
        dim_nbno = [(dim_geo(gt), nbno_geo(gt)) for gt in geo_types]

        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_name = tmp_file.name + ".med"

        mesh.write(tmp_name, True)

    return dim_nbno, tmp_name

def is_quadratic(dims_nbno):
    """
    Returns whether the mesh element dimensions correspond to
    the presence of quadratic elements.
    dims_nbno : list of couples (elem dim, number of points)

    For example a 3d shell with 9 points is identified as
    a (2, 9) entry in dims_nbno

    This function returns None if there are no quadratic elements
    It returns 1 if there are actually quadratic elements

    This is done this way in order to allow to toggle between
    quadratic and linear representations (quad = 0/1) without
    having to use a new flag, since quad=None if there is no need
    to propose the toggle function from the first place!
    """
    # Number of points for a linear element
    linear = {0: 1,
              1: 2,
              2: 4,
              3: 6}
    for dim, nbno in dims_nbno:
        if nbno > linear[dim]:
            return 1
    return None

def nb_points_cells(source):
    """
    Returns the number of points and cells from a given PV source
    """
    data_info = source.GetDataInformation().DataInformation
    return data_info.GetNumberOfPoints(), data_info.GetNumberOfCells()


def get_pv_mem_use():
    """
    Reads and interprets the current memory usage by paraview
    in kilobytes
    """
    import paraview.benchmark as bm
    used_mem = bm.logbase.get_memuse()
    # used_mem = ['CL[0] 619044 / 8387368', 'DS_RS[0] 619044 / 8387368']
    _, current, _, _ = used_mem[0].split()
    return (int(current), get_total_memory())


def dbg_print(msg):
    """
    Prints (to stdout) a message, if the config.DEBUG flag is True
    """
    if DEBUG and msg:
        print(msg)


def get_total_memory():
    """
    Returns the total system's RAM in kilobytes
    """
    import os
    if os.name == 'nt':
        import ctypes
        mem = ctypes.c_uint64
    else:
        mem_bytes = os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
        mem = mem_bytes/1024.
    return int(mem)

def clear_pipeline():
    """
    Clears the paraview pipeline
    """
    import pvsimple as pvs
    pxm = pvs.servermanager.ProxyManager()

    all_proxies = pxm.GetProxiesInGroup('sources')
    for key in all_proxies:
        pname = key[0]
        pobj = all_proxies[key]
        # TODO: A MORE ROBUST WAY TO IDENTIFY ASTERSTUDY PV SOURCES ?
        if pname.startswith('<'):
            pxm.UnRegisterProxy('sources', pname, pobj)
            pvs.Delete(pobj)
            del pobj

    # pxm.UnRegisterProxies()
    # del pxm
    # pvs.Disconnect()
    # pvs.Connect()

def clear_pipeline_forced():
    """
    Force clearing of all pipeline elements in paraview, asterstudy
    elements as well as other existing elements
    """
    import pvsimple as pvs
    pxm = pvs.servermanager.ProxyManager()
    pxm.UnRegisterProxies()
    del pxm
    pvs.Disconnect()
    pvs.Connect()

def clear_pv_proxies(obj):
    """
    Deletes any pv proxies defined as attributes of the given object
    """
    import pvsimple as pvs
    import paraview
    obj_keys = list(obj.__dict__.keys())
    for attr in obj_keys:
        val_attr = getattr(obj, attr)
        if isinstance(val_attr, paraview.servermanager.Proxy):
            setattr(obj, None)
            pvs.Delete(val_attr)
            del val_attr
    return obj

def is_locframe(field):
    """Tell if the field is based on a LocalFrame."""
    if field.name.startswith('.REPLO_'):
        return True
    if field.concept.name == 'RepLocal' and field.name.startswith('_'):
        return True
    return False


def convert_color(value):
    """
    Converts HEX color format to RGB [0, 1] scaled color.
    """
    value = value.lstrip('#')
    size = len(value)
    return tuple(int(value[i:i + size // 3], 16) /
                 255. for i in range(0, size, size // 3))

def create_axes():
    """
    Creates a vtkAxesActor in 3D with specific coloring for x, y and z
    Used both for the reference axis and the orientation marker
    """
    import vtk
    axes = vtk.vtkAxesActor()
    def axis_text_property(color):
        """Create a new text property for the axis label"""
        tprop = vtk.vtkTextProperty()
        tprop.SetBold(1)
        tprop.SetItalic(0)
        tprop.SetColor(*convert_color(color))
        tprop.SetOpacity(1.0)
        tprop.SetFontFamilyToTimes()
        return tprop
    for label, color in zip((axes.GetXAxisCaptionActor2D(),
                             axes.GetYAxisCaptionActor2D(),
                             axes.GetZAxisCaptionActor2D()),
                            ('#ba0000', '#00a300', '#000094')):
        label.SetWidth(0.03)
        label.SetHeight(0.03)
        label.SetCaptionTextProperty(axis_text_property(color))
    return axes
