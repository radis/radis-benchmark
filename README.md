# radis-benchmark

Performance Benchmarks for [RADIS](http://radis.github.io/) 

[![asv](http://img.shields.io/badge/benchmarked%20by-asv-blue.svg?style=flat)](https://radis.github.io/radis-benchmark/)

## Automatic benchmarks 

Benchmarks can be found in [benchmarks/benchmarks.py](./benchmarks/benchmarks.py)

Benchmarks are executed with [Airspeed Velocity](https://asv.readthedocs.io/en/stable/#). 
Results: 🔗 https://radis.github.io/radis-benchmark/

Run the benchmarks :

```
asv run HASHFILE:tested_commit_hash.txt -e
asv publish
asv preview
``` 

Benchmarks are executed many times. Some involve calculations of 1+ millions of lines, before the LDM method was introduced, and therefore take a long time. If developing new benchmarks, first check the ASV documentation and in particular ``asv dev`` 

Benchmarks are run against major tagged versions of RADIS. The list of version can be found in [tested_radis_versions.txt](./tested_radis_versions.txt). These tags mostly belong to the [master branch](https://github.com/radis/radis/commits/master). Older versions (< 0.9.21) required manual patches to be able to run the benchmarks. Therefore, support branches were added. See [support/0.9.18](https://github.com/radis/radis/commits/support/0.9.18), [support/0.9.19](https://github.com/radis/radis/commits/support/0.9.19), [support/0.9.21](https://github.com/radis/radis/commits/support/0.9.21), [support/0.9.22](https://github.com/radis/radis/commits/support/0.9.22). 

*Note : for asv to work using the version directly ([tested_radis_versions](./tested_radis_versions.txt) ) did not work. The commit hash ([tested_commit_hash](./tested_commit_hash.txt)) had to be used instead. A quick way to generate the commit hash of each version tag is to run the following command in the radis (not radis-benchmark) git repository (where the initial sed deals with line returns on Windows, and will change nothing on Unix).* 

```
 sed 's/\r//' tested_radis_versions.txt | xargs -I % git rev-list -n 1 % > tested_commit_hash.txt
```

*Note 2 : once you have run the test locally, you can upload them directly on the [🔗 online website](https://radis.github.io/radis-benchmark/) by running `asv gh-pages`


## Manual performance tests :

- [CPU vs GPU calculations](./manual_benchmarks/cpu_gpu_benchmark.ipynb)  by @pkj-m
