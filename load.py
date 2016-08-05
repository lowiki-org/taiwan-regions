#!/usr/bin/env python

import os
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from localwiki.regions.models import Region, RegionSettings
from django.contrib.auth.models import User

town_shp = os.path.join(os.path.dirname(__file__),
                        'town-SHP/Town_MOI_1041215_UTF8.shp')
ds = DataSource(town_shp)

admins = []
for username in ['pm5', 'superbil', 'dongpo']:
    try:
        admin = User.objects.get(username=username)
        admins.append(admin)
    except User.DoesNotExist:
        pass

mapping = {
    'full_name': 'NFULLNAME',
    'slug': 'SLUG',
    'geom': 'POLYGON',
}


def clear_region(slug):
    for i in range(10):
        regions = Region.objects.filter(slug__startswith=unicode(i))
        regions.delete()


def run(verbose=True):
    lm = LayerMapping(
        Region, town_shp, mapping, transform=True, encoding="utf-8")
    lm.save(strict=True, verbose=verbose)
    for feat in ds[0]:
        print(feat.get(mapping['slug']))
        rg = Region.objects.get(slug__iexact=feat.get(mapping['slug']))
        rg.populate_region()

        rs = RegionSettings.objects.get(region__slug__iexact=feat.get(mapping['slug']))
        rs.admins.add(*admins)
        rs.default_language = u'zh'
        rs.save()
