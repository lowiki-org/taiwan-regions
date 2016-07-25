#!/usr/bin/env python

import os
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from localwiki.regions.models import Region, RegionSettings
from django.contrib.auth.models import User

town_shp = os.path.join(os.path.dirname(__file__),
                        'town-SHP/town_103cap_UTF8.shp')
ds = DataSource(town_shp)
admins = [User.objects.get(username=username) for username in ['pm5', 'superbil', 'dongpo']]
mapping = {
    'full_name': 'D_NAME103',
    'slug': 'nTOWN',
    'geom': 'POLYGON',
}


def clear(verbose=True):
    for i in range(10):
        regions = Region.objects.filter(slug__startswith=unicode(i))
        regions.delete()


def run(verbose=True):
    lm = LayerMapping(
        Region, town_shp, mapping, transform=True, encoding="utf-8")
    lm.save(strict=True, verbose=verbose)
    for feat in ds[0]:
        rg = Region.objects.get(slug=feat.get('nTOWN'))
        rg.populate_region()

        rs = RegionSettings.objects.get(region__slug=feat.get('nTOWN'))
        rs.admins.add(*admins)
        rs.default_language = u'zh'
        rs.save()
