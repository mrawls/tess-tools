import os
import matplotlib.pyplot as plt
import lightkurve as lk
from glob import glob


def plotTessLightcurve(tic, downloadDir='/epyc/data/tess',
                       sectorList=[1, 2, 3, 4, 5, 6, 7], offset=0,
                       saveFits=False, savePlot=False, plotFile=None):
    """Plotting function for TESS short-cadence light curves.

    Parameters
    ----------
    tic : `int`, TESS Input Catalogue ID number
    downloadDir : `str`, location where target pixel files exist
                   and/or should be saved, optional
    sectorList :  `list`, all observing sectors to use when downloading,
                   plotting, and saving TESS data
    offset : `float`, amount by which to offset normalized flux median from 1
              on the y-axis in plots. Useful if you are looping over
              plotTessLightcurve multiple times and want to plot several
              light curves on the same plot but not have them entirely overlap
    saveFits : `boolean`, if True save FITS lightcurve file to working directory
                if False do not save any output files
    saveFig : `boolean`, if True and plotFile is defined, save figure to disk
               if False or plotFile is None, display figure instead
    plotFile : `str`, required to save figure to disk when saveFig is True

    Example
    -------
    Suggested use:
        import os
        import matplotlib.pyplot as plt
        import lightkurve as lk
        from glob import glob
        from tessLightcurvePlotter import plotTessLightcurve
        plt.figure()
        # define your own ticList here, e.g., ticList = [1234567, 2345678]
        for idx, tic in enumerate(ticList):
            plotTessLightcurve(tic, offset=0.05*idx)
        plt.show()
    """
    downloadDir = os.path.normpath(downloadDir)
    tpf = None
    lc = None
    for sector in sectorList:
        sectorStr = "%.3d" % sector
        if 'epyc' in downloadDir:  # files are in sector subdirectories
            filePath = glob(downloadDir + '/sector' + sectorStr + '/tess*s0' +
                            sectorStr + '*' + str(tic) + '*/*.fits')
        else:  # files are all in one directory (lightkurve default)
            filePath = glob(downloadDir + '/tess*s0' + sectorStr + '*' + str(tic) + '*/*.fits')
        if len(filePath) > 0:  # the file is on disk
            filePath.append(filePath[0])  # hack to avoid fits file opening failure
            tpf = lk.TessTargetPixelFile(filePath[0])
        else:  # the file isn't on disk
            if list(lk.search_targetpixelfile(tic, sector=sector)):  # nonzero search results
                print('Downloading sector {0} for star {1}'.format(sector, tic))
                tpf = lk.search_targetpixelfile(tic, sector=sector).download()
        if tpf and not lc:
            lc = tpf.to_lightcurve().normalize()
        elif tpf and lc:
            newlc = tpf.to_lightcurve().normalize()
            lc = lc.append(newlc)
        else:
            pass  # there is no tpf for this target + sector
    if lc:
        plt.plot(lc.time, lc.flux - offset, label=tic, marker='.', ls='None', alpha=0.2, mec='None')
        if saveFits:
            lc.to_fits(path=str(tic)+'Norm.fits', overwrite=True)
    else:
        print(tic, 'No LC found for any sector')
    plt.xlabel('Time (days)')
    plt.ylabel('Normalized flux')
    plt.legend(frameon=False)
    plt.gca().set_ylim(0.5, 1.1)
    if savePlot and plotFile:
        plt.savefig(plotFile)
