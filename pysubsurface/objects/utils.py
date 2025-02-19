import numpy as np
import segyio

from pysubsurface.utils.utils import findclosest_scatter

# seismic ebcdic decoders
_a2e = [
    0,  1,  2,  3,  55, 45, 46, 47, 22, 5,  37, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 60, 61, 50, 38, 24, 25, 63, 39, 28, 29, 30, 31,
    64, 79, 127,123,91, 108,80, 125,77, 93, 92, 78, 107,96, 75, 97,
    240,241,242,243,244,245,246,247,248,249,122,94, 76, 126,110,111,
    124,193,194,195,196,197,198,199,200,201,209,210,211,212,213,214,
    215,216,217,226,227,228,229,230,231,232,233,74, 224,90, 95, 109,
    121,129,130,131,132,133,134,135,136,137,145,146,147,148,149,150,
    151,152,153,162,163,164,165,166,167,168,169,192,106,208,161,7,
    32, 33, 34, 35, 36, 21, 6,  23, 40, 41, 42, 43, 44, 9,  10, 27,
    48, 49, 26, 51, 52, 53, 54, 8,  56, 57, 58, 59, 4,  20, 62, 225,
    65, 66, 67, 68, 69, 70, 71, 72, 73, 81, 82, 83, 84, 85, 86, 87,
    88, 89, 98, 99, 100,101,102,103,104,105,112,113,114,115,116,117,
    118,119,120,128,138,139,140,141,142,143,144,154,155,156,157,158,
    159,160,170,171,172,173,174,175,176,177,178,179,180,181,182,183,
    184,185,186,187,188,189,190,191,202,203,204,205,206,207,218,219,
    220,221,222,223,234,235,236,237,238,239,250,251,252,253,254,255
]

_e2a = [
    0,  1,  2,  3,  156,9,  134,127,151,141,142, 11,12, 13, 14, 15,
    16, 17, 18, 19, 157,133,8,  135,24, 25, 146,143,28, 29, 30, 31,
    128,129,130,131,132,10, 23, 27, 136,137,138,139,140,5,  6,  7,
    144,145,22, 147,148,149,150,4,  152,153,154,155,20, 21, 158,26,
    32, 160,161,162,163,164,165,166,167,168,91, 46, 60, 40, 43, 33,
    38, 169,170,171,172,173,174,175,176,177,93, 36, 42, 41, 59, 94,
    45, 47, 178,179,180,181,182,183,184,185,124,44, 37, 95, 62, 63,
    186,187,188,189,190,191,192,193,194,96, 58, 35, 64, 39, 61, 34,
    195,97, 98, 99, 100,101,102,103,104,105,196,197,198,199,200,201,
    202,106,107,108,109,110,111,112,113,114,203,204,205,206,207,208,
    209,126,115,116,117,118,119,120,121,122,210,211,212,213,214,215,
    216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,
    123,65, 66, 67, 68, 69, 70, 71, 72, 73, 232,233,234,235,236,237,
    125,74, 75, 76, 77, 78, 79, 80, 81, 82, 238,239,240,241,242,243,
    92, 159,83, 84, 85, 86, 87, 88, 89, 90, 244,245,246,247,248,249,
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 250,251,252,253,254,255
]


def _findclosest_point(point, seismic):
    """Find inline and crossline in seismic data that
    are closest to a single point

    Parameters
    ----------
    point : :obj:`tuple`
        Point as (x, y)
    seismic : :obj:`pysubsurface.objects.Seismic` or :obj:`pysubsurface.objects.SeismicIrregular`
        Seismic object

    Returns
    -------
    ilwell : :obj:`int`
        Inline closest to point
    xlwell : :obj:`int`
        Crossline closest to point

    """
    iclosest =\
        findclosest_scatter(np.vstack([seismic.cdpx, seismic.cdpy]), point)
    head = seismic.read_headervalues(iclosest, (seismic._iline, seismic._xline))
    ilwell = head[segyio.tracefield.TraceField(seismic._iline)]
    xlwell = head[segyio.tracefield.TraceField(seismic._xline)]
    return ilwell, xlwell


def _findclosest_point_surface(point, surface):
    """Find inline and crossline in surface that are closest to a single point

    Parameters
    ----------
    point : :obj:`tuple`
        Point as (x, y)
    surface : :obj:`pysubsurface.objects.Surface`
        Surface object

    Returns
    -------
    ilwell : :obj:`int`
        Inline closest to point
    xlwell : :obj:`int`
        Crossline closest to point

    """
    iclosest =\
        findclosest_scatter(np.vstack([surface._xs_orig,
                                       surface._ys_orig]), point)
    ilwell = int(surface._ils[iclosest])
    xlwell = int(surface._xls[iclosest])

    return ilwell, xlwell


def _findclosest_well_seismicsections(well, seismic, traj=False,
                                      dmd=None, verb=False):
    """Find inline and crossline in seismic data that are closest to well head
    or well trajectory

    Parameters
    ----------
    well : :obj:`pysubsurface.objects.Well`
        Well object
    seismic : :obj:`pysubsurface.objects.Seismic` or :obj:`pysubsurface.objects.SeismicIrregular`
        Seismic object
    traj : :obj:`bool`, optional
        Find indeces for every point in trajectory (``True``)
        or just well head (``False``)
    dmd : :obj:`float`, optional
        Sampling in MD to be used (if ``None`` use irregular sampling as in
        trajectory)
    verb : :obj:`bool`, optional
        Verbosity

    Returns
    -------
    ilwell : :obj:`int` or :obj:`np.ndarray`
        Inline closest to well head or
        inlines closest to each point of well trajectory
    xlwell : :obj:`int` or :obj:`np.ndarray`
        Crossline closest to well or
        crosslines closest to each point of well trajectory

    """
    if not traj:
        # work with just well head
        ilwell, xlwell = _findclosest_point((well.xcoord, well.ycoord), seismic)
    else:
        if dmd is not None:
            mds = well.trajectory.df['MD (meters)']
            mdreg = np.arange(mds.min(), mds.max(), dmd)
            xsabs = np.interp(mdreg, mds, well.trajectory.df['X Absolute'])
            ysabs = np.interp(mdreg, mds, well.trajectory.df['Y Absolute'])
        else:
            xsabs = well.trajectory.df['X Absolute']
            ysabs = well.trajectory.df['Y Absolute']

        ilwell = np.zeros(len(xsabs))
        xlwell = np.zeros_like(ilwell)
        for ipoint, (xabs, yabs) in enumerate(zip(xsabs, ysabs)):
            ilwell[ipoint], xlwell[ipoint] = \
                _findclosest_point((xabs, yabs), seismic)

    if verb:
        print('IL={}, XL={}'.format(ilwell, xlwell))
    return ilwell, xlwell
