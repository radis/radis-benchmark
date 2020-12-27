# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

from radis import calc_spectrum, SpectrumFactory
from radis import get_version
from radis.misc.printer import printm

class CO2:
    """
    bla
    
    Also used in :py:func:`radis.test.lbl.test_calc.test_calc_spectrum`
    """
    
    def setup(self):
        self.test_options = opt = {
            "wavelength_min":4165,
            "wavelength_max":4200,
            "databank":"fetch",  # not appropriate for these temperatures, but convenient for automatic testing
            "Tgas":300,
            "Tvib":1700,
            "Trot":1550,
            "path_length":0.1,
            "mole_fraction":0.5,
            "molecule":"CO2",
            "isotope":"1,2",
            "wstep":0.01,
            "cutoff":1e-25,
            "use_cached":True,
            "medium":"vacuum",
            "optimization":"simple",
            "warnings":{
                "MissingSelfBroadeningWarning": "ignore",
                "NegativeEnergiesWarning": "ignore",
                "HighTemperatureWarning": "ignore",
            }}
        
        # Backward compatibility
        # ----------------------
        
        # Old version of RADIS do not necessary work with the latest parameters
        # Fix it : 
        version = get_version(add_git_number=False)
        if version < '0.9.26':
            del self.test_options['optimization']
        
        # Also fix problems with cache files :
        
        # First run to check there are no problems with Line database cache-files
        # ... Note @dev : as of 0.9.26 encountering a cache file generated with a future version
        # ... raises an error with no option to automatically regenerate the cache file
        sf = SpectrumFactory(**{k:v for (k,v) in opt.items() if k in [
            'wavelength_min','wavelength_max', 'molecule', 'isotope', 'broadening_max_width',
            'medium']})
        
        try:
            sf.fetch_databank()
        except ValueError as err:
            if "generated with a future version" in str(err) and 'tempfile' in str(err):
                # Clean problematic cache files
                # Note @dev : in 0.9.25 fetch_astroquery() doesnt use the use_cache
                # parameter from SpectrumFactory... Too bad, else we could have simply
                # used the 'regen' value
                from astroquery.hitran import Hitran
                import os
                from os.path import exists, join
                from radis.io.query import CACHE_FILE_NAME
                for iso in sf._get_isotope_list(molecule=opt['molecule']):
                    fcache = join(
                        Hitran.cache_location,
                        CACHE_FILE_NAME.format(**{
                        'molecule':opt['molecule'],'isotope':iso,
                        'wmin':sf.params.wavenum_min_calc,
                        'wmax':sf.params.wavenum_max_calc}),
                    )
                    printm('> ', err)
                    printm('Backward compatibility : regenerating cache file', fcache)
                    if exists(fcache):
                        os.remove(fcache)
                        
        # 2nd run to check there are no problems with Energy levels cache files
        # ... Note @dev : as of 0.9.26 encountering a cache file generated with a future version
        # ... raises an error with no option to automatically regenerate the cache file
    
        try:
            sf.fetch_databank()
        except ValueError as err:
            if "generated with a future version" in str(err) and 'molecules_data' in str(err):
                # Clean problematic cache files
                printm('> ', err)
                printm('Backward compatibility : regenerating energy levels file')
                sf.params.lvl_use_cached = 'regen'
                sf.fetch_databank()
                
        # Initial calculation to make sure cache files are properly working 
        calc_spectrum(**self.test_options)

    def time_CO2noneq(self):
        # print('\n'*5)        
        # print('START')


        # from time import time
        # t0 = time()
        calc_spectrum(**self.test_options,
                      export_lines=False,
                      verbose=3)

        # print('FINISH')
        # print('{0:.0f}s'.format(time()-t0))

    def peakmem_CO2noneq(self):

        calc_spectrum(**self.test_options)


