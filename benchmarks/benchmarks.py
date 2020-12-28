# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

import os
from os.path import join
from radis import SpectrumFactory, calc_spectrum, get_version
from radis.misc.printer import printm


class CO2_HITRAN:
    """
    Small performance test based on a reduced dataset of CO2 HITRAN

    Also used in :py:func:`radis.test.lbl.test_calc.test_calc_spectrum`
    """

    def setup(self):
        self.test_options = opt = {
            "wavelength_min": 4165,
            "wavelength_max": 4200,
            "databank": "fetch",  # not appropriate for these temperatures, but convenient for automatic testing
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
        version = get_version(add_git_number=False)
        if version < "0.9.26":
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
        
        from radis.db.utils import getFile
        def get_astroquery_cache(iso):
            from astroquery.hitran import Hitran
            try:
                from radis.io.query import CACHE_FILE_NAME
            except ImportError:
                CACHE_FILE_NAME = 'tempfile_{molecule}_{isotope}_{wmin:.2f}_{wmax:.2f}.h5'
            fcache = join(
                Hitran.cache_location,
                CACHE_FILE_NAME.format(
                    **{
                        "molecule": opt["molecule"],
                        "isotope": iso,
                        "wmin": sf.params.wavenum_min_calc,
                        "wmax": sf.params.wavenum_max_calc,
                    }
                )
            )
            return fcache

        for attempt in range(15):  # max number of failed cache files
            try:
                sf.fetch_databank()
            except ValueError as err:
                if "generated with a future version" in str(err):
                    for fcache in [
                        get_astroquery_cache(iso=1),
                        get_astroquery_cache(iso=2),
                        get_astroquery_cache(iso=3),
                        getFile(join("CO2", "molecules_data_CO2_iso1_X_levels.h5")),
                        getFile(join("CO2", "molecules_data_CO2_iso2_X_levels.h5")),
                        getFile(join("CO2", "co2_iso1_levels.h5")), # old (0.9.19?) syntax
                        getFile(join("CO2", "co2_iso2_levels.h5")), # old (0.9.19?) syntax
                    ]:
                        if fcache in str(err):
                            printm(
                                "Backward compatibility : regenerating cache file",
                                fcache,
                            )
                            os.remove(fcache)
                else:
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

    def setup(self):
        self.test_options = opt = {
            "wavenum_min": 2000,
            "wavenum_max": 2250,
            "molecule": "CO2",
            "isotope": "1,2,3",
            "verbose": 3,
            "wstep": 0.01,
            "cutoff": 0,
            "path": [
                r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_07",
                r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_08",
                r"D:\Dropbox\Data ECP\14_Databases\CDSD-HITEMP\cdsd_hitemp_09",
            ],
            "use_cached": True,
            "dbformat": "cdsd-hitemp",
        }

        # Backward compatibility
        # ----------------------

        # Old version of RADIS do not necessary work with the latest parameters
        # Fix it :
        version = get_version(add_git_number=False)
        if version < "0.9.21":
            opt["dbformat"] = "cdsd"

        # Also fix problems with cache files :
        from radis.db.utils import getFile

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
                sf.load_databank(
                    path=opt["path"],
                    format=opt["dbformat"],
                    parfuncfmt="hapi",
                    levelsfmt="radis",
                )
            except ValueError as err:
                if "generated with a future version" in str(err):
                    for fcache in [
                        opt["path"][0] + ".h5",
                        opt["path"][1] + ".h5",
                        opt["path"][2] + ".h5",
                        getFile(join("CO2", "molecules_data_CO2_iso1_X_levels.h5")),
                        getFile(join("CO2", "molecules_data_CO2_iso2_X_levels.h5")),
                        getFile(join("CO2", "co2_iso1_levels.h5")), # old (0.9.19?) syntax
                        getFile(join("CO2", "co2_iso2_levels.h5")), # old (0.9.19?) syntax
                    ]:
                        if fcache in str(err):
                            printm(
                                "Backward compatibility : regenerating cache file",
                                fcache,
                            )
                            os.remove(fcache)
                else:
                    raise
            else:
                break

    def time_eq_spectrum(self):
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
                ]
            }
        )
        sf.load_databank(
            path=opt["path"],
            format=opt["dbformat"],
            parfuncfmt="hapi",
            levelsfmt="radis",
        )
        assert len(sf.df0) == 1487308  # number of lines
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
                ]
            }
        )
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
                ]
            }
        )
        sf.load_databank(
            path=opt["path"],
            format=opt["dbformat"],
            parfuncfmt="hapi",
            levelsfmt="radis",
        )
        assert len(sf.df0) == 1487308  # number of lines
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
                ]
            }
        )
        sf.load_databank(
            path=opt["path"],
            format=opt["dbformat"],
            parfuncfmt="hapi",
            levelsfmt="radis",
        )
        assert len(sf.df0) == 1487308  # number of lines
        sf.non_eq_spectrum(Ttrans=300, Tvib=1700, Trot=1550)