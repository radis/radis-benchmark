# radis-benchmark

Performance Benchmarks for [RADIS](http://radis.github.io/) 

## Automatic benchmarks 

Benchmarks can be found in [benchmarks/benchmarks.py](./benchmarks/benchmarks.py)

Benchmarks are executed with [Airspeed Velocity](https://asv.readthedocs.io/en/stable/#). 
Results: 🔗 https://radis.github.io/radis-benchmark/

Run the benchmarks :

```
asv run HASHFILE:tested_radis_versions.txt -e
asv publish
asv preview
``` 

Benchmarks are executed many times. Some involve calculations of 1+ millions of lines, before the LDM method was introduced, and therefore take a long time. If developing new benchmarks, first check the ASV documentation and in particular ``asv dev`` 

Benchmarks are run against major tagged versions of RADIS. The list of version can be found in [tested_radis_versions.txt](./tested_radis_versions.txt). These tags mostly belong to the [master branch](https://github.com/radis/radis/commits/master). Older versions (< 0.9.21) required manual patches to be able to run the benchmarks. Therefore, support branches were added. See [support/0.9.18](https://github.com/radis/radis/commits/support/0.9.18), [support/0.9.19](https://github.com/radis/radis/commits/support/0.9.19), [support/0.9.21](https://github.com/radis/radis/commits/support/0.9.21), [support/0.9.22](https://github.com/radis/radis/commits/support/0.9.22). 


## Manual performance tests :

- [CPU vs GPU calculations](./TEST1.ipynb)  by @pkj-m
