
# LowalWiki region import script for Taiwan villages


Usage
-----

```
$ source /srv/localwiki/env/bin/activate
$ localwiki-manage shell
>>> import load
>>> load.run(True)      # import test data; ~10 regions
>>> load.run(False)     # import all data; ~8000 regions

# browse data
>>> load.ds[0].geom_type
>>> load.ds[0].srs
>>> load.ds[0].fields
```
