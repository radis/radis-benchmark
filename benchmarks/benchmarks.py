# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

from radis import calc_spectrum
from radis import get_version

class CO2:
    """
    bla
    
    Also used in :py:func:`radis.test.lbl.test_calc.test_calc_spectrum`
    """
    
    def setup(self):
        self.test_options = {
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
        version = get_version(add_git_number=False)
        if version < '0.9.26':
            del self.test_options['optimization']
    
        # Initial calculation to download databases etc. 
        first_run_options = self.test_options.copy()
        first_run_options['use_cached'] = 'regen'
        calc_spectrum(**first_run_options)
        
    def time_CO2noneq(self):

        calc_spectrum(**self.test_options)


    def peakmem_CO2noneq(self):

        calc_spectrum(**self.test_options)




c=CO2()
c.setup()
c.time_CO2noneq()