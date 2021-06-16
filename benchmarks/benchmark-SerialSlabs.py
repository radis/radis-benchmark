# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 20:40:25 2021

@author: erwan

Line-of-sight benchmark

"""

from numpy import zeros
from radis import calc_spectrum, SerialSlabs
from time import time

class LineOfSight_Benchmark:
    """
    Small performance test for LOS functions with multiple spectra

    Benchmarks :py:func:`radis.los.slabs.SerialSlabs`
    """

    def setup(self):

        s = calc_spectrum(1900, 2300,         # cm-1
                          molecule='CO',
                          isotope='1,2,3',
                          pressure=1.01325,   # bar
                          Tgas=700,           # K
                          mole_fraction=0.1,
                          path_length=1,      # cm
                          wstep=0.01,
                          verbose=False,
                          )
        self.s_list =  [s.copy()]*100

    def time_SerialSlabs(self):

        SerialSlabs(*self.s_list, modify_inputs=False)  # modify_inputs=True

    def peakmem_SerialSlabs(self):

        SerialSlabs(*self.s_list, modify_inputs=False)  # modify_inputs=True)



#%% Test : Compare to simple LOS

if __name__ == '__main__':

    LOS = LineOfSight_Benchmark()
    LOS.setup()
    print(f'LOS for {len(LOS.s_list)} spectra:')

    # %% Benchmark using RADIS's LOS SerialSlabs

    t0 = time()
    LOS.time_SerialSlabs()
    print(f'SerialSlabs in {time()-t0:.2f}s')
    # print(s_los.get('radiance_noslit')[1])


    # %% Compare to naive version (without unit conversions / etc, so very efficient !)
    t0 = time()

    I = zeros(len(LOS.s_list[0]))
    for si in LOS.s_list:
        ti = si.get('transmittance_noslit', copy=False)[1]
        ri = si.get('radiance_noslit', copy=False)[1]
        I = I * ti + ri

    print(f'Simple LOS in {time()-t0:.2f}s')
    # print(I)

    # %% Jit  (but actually slower than pure Python?):

    from numba import jit
    from numpy import array
    T_array = array([si.get('transmittance_noslit', copy=False)[1] for si in LOS.s_list])
    I_array = array([(si.get('radiance_noslit', copy=False)[1]) for si in LOS.s_list])
    N = len(T_array[0])

    @jit(nopython=True)
    def LOS_jit():
        I = zeros(N)
        for ti, ri in zip(T_array, I_array):
            I = I * ti + ri
        return I

    t0 = time()
    LOS_jit()
    print(f'Simple LOS (numba-jit) in {time()-t0:.2f}s')