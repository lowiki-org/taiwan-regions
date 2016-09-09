#!/usr/bin/env python

import os
import time
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from localwiki.regions.models import Region, RegionSettings
from localwiki.pages.models import Page
from localwiki.tags.models import Tag, PageTagSet
from django.contrib.auth.models import User
from django.utils.translation import activate, get_language

activate('zh')

town_shp = os.path.join(os.path.dirname(__file__),
                        'village-SHP/Village_NLSC_1050219_UTF8.shp')
test_shp = os.path.join(os.path.dirname(__file__),
                        'test-regions/Village_NLSC_1050219_UTF8.shp')
ds = None

admins = []
for username in ['pm5', 'superbil', 'dongpo']:
    try:
        admin = User.objects.get(username=username)
        admins.append(admin)
    except User.DoesNotExist:
        pass

mapping = {
    'full_name': 'FULLNAME',
    'slug': 'SLUG',
    'geom': 'POLYGON'
}


def clear_region(region=None, slug=None):
    if region == None and slug != None:
        region = Region.objects.get(slug__iexact=slug)
    if region != None:
        region.page_set.all().delete()
    else:
        Page.objects.all().delete()


def run(dryrun, verbose=False):
    shp_datasource = test_shp if dryrun else town_shp
    ds = DataSource(shp_datasource)
    try:
        lm = LayerMapping(
            Region, shp_datasource, mapping, transform=True, encoding="utf-8")
        lm.save(strict=True, verbose=verbose)
    except:
        print "Already have regions.  Give up importing regions."

    for feat in ds[0]:
        print feat.get(mapping['slug'])
        rg = Region.objects.get(slug__iexact=feat.get(mapping['slug']))
        try:
            rg.populate_region()
        except:
            print "Alread have pages.  Give up populating this region."

        tags = []
        try:
            tag = Tag.objects.get(name=feat.get('NCITYNAME'))
        except:
            tag = Tag(name=feat.get('NCITYNAME'))
            tag.save()
        tags.append(tag)
        try:
            tag = Tag.objects.get(name=feat.get('NCITYNAME') + feat.get('NTOWNNAME'))
        except:
            tag = Tag(name=feat.get('NCITYNAME') + feat.get('NTOWNNAME'))
            tag.save()
        tags.append(tag)

        try:
            fp = Page.objects.get(region=rg, slug__iexact='front page')
        except:
            fp = Page(region=rg, name='Front Page')
            fp.save()
        try:
            tagset = fp.pagetagset
        except:
            tagset = PageTagSet(page=fp, region=rg)
            tagset.save()
        for tag in tags:
            try:
                tagset.tags.add(tag)
            except:
                pass

        rs = RegionSettings.objects.get(region__slug__iexact=feat.get(mapping['slug']))
        rs.admins.add(*admins)
        rs.default_language = u'zh'
        rs.save()

        time.sleep(1)
