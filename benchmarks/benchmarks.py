# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

import os
import re
import sys

from numpy import floor, log10, round
from psutil import virtual_memory

from radis import SpectrumFactory, calc_spectrum, get_version
from radis.lbl.factory import _generate_broadening_range
from radis.misc.printer import printm

from packaging.version import parse


def digits(x, n=1):
    """ Round x to n digits """
    return round(x * 10 ** (-floor(log10(x))), n - 1) * 10 ** (floor(log10(x)))


class CO2_HITRAN:
    """
    Small performance test based on a reduced dataset of CO2 HITRAN

    Also used in :py:func:`radis.test.lbl.test_calc.test_calc_spectrum`
    """

    def setup(self):
        self.test_options = opt = {
            "wavelength_min": 4165,
            "wavelength_max": 4200,
            "databank": "hitran",  # not appropriate for these temperatures, but convenient for automatic testing
            "Tgas": 300,
            "Tvib": 1700,
            "Trot": 1550,
            "path_length": 0.1,
            "mole_fraction": 0.5,
            "molecule": "CO2",
            "isotope": "1,2",
            "wstep": 0.01,
            "cutoff": 1e-25,
            "use_cached": True,
            "medium": "vacuum",
            "optimization": "simple",
            "export_lines": False,
            "warnings": {
                "MissingSelfBroadeningWarning": "ignore",
                "NegativeEnergiesWarning": "ignore",
                "HighTemperatureWarning": "ignore",
            },
        }

        # Backward compatibility
        # ----------------------

        # Old version of RADIS do not necessary work with the latest parameters
        # Fix it :
        version = parse(get_version(add_git_number=False))
        if version < parse("0.9.26"):
            del self.test_options["optimization"]

        # Also fix problems with cache files :

        # First run to check there are no problems with Line database cache-files
        # ... Note @dev : as of 0.9.26 encountering a cache file generated with a future version
        # ... raises an error with no option to automatically regenerate the cache file
        sf = SpectrumFactory(
            **{
                k: v
                for (k, v) in opt.items()
                if k
                in [
                    "wavelength_min",
                    "wavelength_max",
                    "molecule",
                    "isotope",
                    "broadening_max_width",
                    "medium",
                ]
            }
        )

        for attempt in range(15):  # max number of failed cache files
            try:
                sf.fetch_databank()
            except ValueError as err:
                if "generated with a future version" in str(err):
                    # Get failing cache file :
                    fcache = re.search(
                        r"(?<=Cache file \().*(?=\) generated)", str(err)
                    )
                    if fcache is not None:
                        fcache = fcache.group()
                        printm(
                            "Backward compatibility : regenerating cache file",
                            fcache,
                        )
                        os.remove(fcache)
                        continue
                raise
            else:
                break

    def time_noneq_spectrum(self):

        calc_spectrum(**self.test_options)

    def peakmem_noneq_spectrum(self):

        calc_spectrum(**self.test_options)


class CO2_HITEMP:
    """
    Performance test with CO2 HITEMP (2000 - 2250 cm-1 :  ~ 1.5 Million lines )

    Based on the test in :py:func:`radis.test.lbl.test_factory.test_spec_generation`
    """
    timeout = 3600

    def setup(self):
        self.test_options = opt = {
            "wavenum_min": 2000,
            "wavenum_max": 2250,
            "molecule": "CO2",
            "isotope": "1,2,3",
            "verbose": 1,
            "wstep": 0.01,
            "cutoff": 0,
            "chunksize": "auto",
            "truncation": 10,
            "neighbour_lines": 10,
            "databank": "hitemp",
        }

        # Backward compatibility
        # ----------------------

        # Old version of RADIS do not necessary work with the latest parameters
        # Fix it :
        version = parse(get_version(add_git_number=False))

        if version < parse("0.10.1"):
            # no automatic download of CO2
            opt.update({
                "path": [
                    r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_07",
                    r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_08",
                    r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_09",
                ],
                "use_cached": True,
                "dbformat": "cdsd-hitemp",
            })
            del opt["databank"]
            
        if version < parse("0.10.1"):
            # "broadening_max_width" changed to 'truncation' & neighbour_lines
            opt["broadening_max_widith"] = opt["truncation"]
            # del opt["truncation"]
            del opt["neighbour_lines"]
            
        if version < parse("0.9.21"):
            # format name changed
            opt["dbformat"] = "cdsd"

        # Chunksize : number of lines to proceed at the same time (doestn apply if LDM)
        if opt["chunksize"] == "auto":
            opt["chunksize"] = digits(
                virtual_memory().available
                / sys.getsizeof(
                    _generate_broadening_range(
                        opt["wstep"], opt["truncation"]
                    )
                ),
                n=1,
            )
            printm("chunksize auto : ", opt["chunksize"])

        # Also fix problems with cache files :

        # First run to check there are no problems with Line database cache-files
        # ... Note @dev : as of 0.9.26 encountering a cache file generated with a future version
        # ... raises an error with no option to automatically regenerate the cache file
        sf = SpectrumFactory(
            **{
                k: opt[k]
                for k in [
                    "wavenum_min",
                    "wavenum_max",
                    "molecule",
                    "isotope",
                    "wstep",
                    "cutoff",
                    "verbose",
                ]
            }
        )

        for attempt in range(15):  # max number of failed cache files
            try:
                if "databank" in opt:
                    sf.fetch_databank(opt["databank"],  # hitemp
                            parfuncfmt="hapi",
                            levelsfmt="radis",) 
                else:
                    sf.load_databank(
                        path=opt["path"],
                        format=opt["dbformat"],
                        parfuncfmt="hapi",
                        levelsfmt="radis",
                    )
            except ValueError as err:
                if "generated with a future version" in str(err):
                    # Get failing cache file :
                    fcache = re.search(
                        r"(?<=Cache file \().*(?=\) generated)", str(err)
                    )
                    if fcache is not None:
                        fcache = fcache.group()
                        printm(
                            "Backward compatibility : regenerating cache file",
                            fcache,
                        )
                        os.remove(fcache)
                        continue
                raise
            else:
                break

    def time_eq_spectrum(self):
        # Note @ dev:  can't use calc_spectrum directly because it cannot
        # read a custom database
        opt = self.test_options

        sf = SpectrumFactory(
            **{
                # Default parameters added in SpectrumFactory :
                k: opt[k]
                for k in [
                    "wavenum_min",
                    "wavenum_max",
                    "molecule",
                    "isotope",
                    "wstep",
                    "cutoff",
                    "verbose",
                    "chunksize",
                ]
            }
        )
        # Load databank:
        if "databank" in opt:
            sf.fetch_databank(opt["databank"],  # auto-downloaded hitemp
                    parfuncfmt="hapi",
                    levelsfmt="radis",) 
            assert len(sf.df0) == 1464035  #small change with <0.10.1, doesnt change the benchmarks significantly
        else:
            sf.load_databank(
                path=opt["path"],
                format=opt["dbformat"],
                parfuncfmt="hapi",
                levelsfmt="radis",
            )
            assert len(sf.df0) == 1487262  # number of lines
        sf.eq_spectrum(Tgas=1700)

    def peakmem_eq_spectrum(self):
        opt = self.test_options
        sf = SpectrumFactory(
            **{
                k: opt[k]
                for k in [
                    "wavenum_min",
                    "wavenum_max",
                    "molecule",
                    "isotope",
                    "wstep",
                    "cutoff",
                    "verbose",
                    "chunksize",
                ]
            }
        )
        # Load databank:
        if "databank" in opt:
            sf.fetch_databank(opt["databank"],  # auto-downloaded hitemp
                    parfuncfmt="hapi",
                    levelsfmt="radis",)
            assert len(sf.df0) == 1464035  #small change with <0.10.1, doesnt change the benchmarks significantly
        else:
            sf.load_databank(
                path=opt["path"],
                format=opt["dbformat"],
                parfuncfmt="hapi",
                levelsfmt="radis",
            )
            assert len(sf.df0) == 1487308  # number of lines
        sf.eq_spectrum(Tgas=1700)

    def time_noneq_spectrum(self):
        # Note @ dev:  can't use calc_spectrum directly because it cannot
        # read a custom database
        opt = self.test_options
        sf = SpectrumFactory(
            **{
                k: opt[k]
                for k in [
                    "wavenum_min",
                    "wavenum_max",
                    "molecule",
                    "isotope",
                    "wstep",
                    "cutoff",
                    "verbose",
                    "chunksize",
                ]
            }
        )
        # Load databank:
        if "databank" in opt:
            sf.fetch_databank(opt["databank"],  # auto-downloaded hitemp
                    parfuncfmt="hapi",
                    levelsfmt="radis",) 
            assert len(sf.df0) == 1464035  #small change with <0.10.1, doesnt change the benchmarks significantly
        else:
            sf.load_databank(
                path=opt["path"],
                format=opt["dbformat"],
                parfuncfmt="hapi",
                levelsfmt="radis",
            )
            assert len(sf.df0) == 1487262  # number of lines
        
        sf.df0.drop(sf.df0.index[sf.df0['v1u']==-1], inplace=True)
            
        sf.non_eq_spectrum(Ttrans=300, Tvib=1700, Trot=1550)

    def peakmem_noneq_spectrum(self):
        opt = self.test_options
        sf = SpectrumFactory(
            **{
                k: opt[k]
                for k in [
                    "wavenum_min",
                    "wavenum_max",
                    "molecule",
                    "isotope",
                    "wstep",
                    "cutoff",
                    "verbose",
                    "chunksize",
                ]
            }
        )
        # Load databank:
        if "databank" in opt:
            sf.fetch_databank(opt["databank"],  # auto-downloaded hitemp
                    parfuncfmt="hapi",
                    levelsfmt="radis",) 
            assert len(sf.df0) == 1464035  #small change with <0.10.1, doesnt change the benchmarks significantly
        else:
            sf.load_databank(
                path=opt["path"],
                format=opt["dbformat"],
                parfuncfmt="hapi",
                levelsfmt="radis",
            )
            assert len(sf.df0) == 1487262  # number of lines
            
        sf.df0.drop(sf.df0.index[sf.df0['v1u']==-1], inplace=True)
            
        sf.non_eq_spectrum(Ttrans=300, Tvib=1700, Trot=1550)


if __name__ == '__main__':

    C = CO2_HITEMP()
    C.setup()
    from time import perf_counter
    t0 = perf_counter()
    C.peakmem_eq_spectrum()
    print(perf_counter()-t0)