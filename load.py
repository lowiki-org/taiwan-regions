#!/usr/bin/env python

import os
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from localwiki.regions.models import Region, RegionSettings
from localwiki.pages.models import Page
from django.contrib.auth.models import User
from django.utils.translation import activate, get_language

activate('zh')

town_shp = os.path.join(os.path.dirname(__file__),
                        'village-SHP/Village_NLSC_1050219_UTF8.shp')
# town_shp = os.path.join(os.path.dirname(__file__),
                        # 'test-SHP/test_village_UTF8.shp')
ds = DataSource(town_shp)

admins = []
for username in ['pm5', 'superbil', 'dongpo']:
    try:
        admin = User.objects.get(username=username)
        admins.append(admin)
    except User.DoesNotExist:
        pass

mapping = {
    'full_name': 'FULLNAME',
    'slug': 'NVILL',
    'geom': 'POLYGON',
}


def clear_region(region=None, slug=None):
    if region == None and slug != None:
        region = Region.objects.get(slug__iexact=slug)
    if region != None:
        region.page_set.all().delete()
    else:
        Page.objects.all().delete()


def run(verbose=True):
    try:
        lm = LayerMapping(
            Region, town_shp, mapping, transform=True, encoding="utf-8")
        lm.save(strict=True, verbose=verbose)
    except:
        print "There are already regions.  Giving up importing regions."

    for feat in ds[0]:
        rg = Region.objects.get(slug__iexact=feat.get(mapping['slug']))
        rg.populate_region()

        rs = RegionSettings.objects.get(region__slug__iexact=feat.get(mapping['slug']))
        rs.admins.add(*admins)
        rs.default_language = u'zh'
        rs.save()
