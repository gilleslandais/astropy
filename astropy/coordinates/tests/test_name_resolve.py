# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
This module contains tests for the name resolve convenience module.
"""

import time
import urllib.request

import numpy as np
import pytest
from pytest_remotedata.disable_internet import no_internet

from astropy import units as u
from astropy.config import paths
from astropy.coordinates.name_resolve import (
    NameResolveError,
    _parse_response,
    get_icrs_coordinates,
    sesame_database,
    sesame_url,
)
from astropy.coordinates.sky_coordinate import SkyCoord
from astropy.utils.data import get_cached_urls

_cached_ngc3642 = {}
_cached_ngc3642["simbad"] = """# NGC 3642    #Q22523669
#=S=Simbad (via url):    1
%@ 503952
%I.0 NGC 3642
%C.0 LIN
%C.N0 15.15.01.00
%J 170.5750583 +59.0742417 = 11:22:18.01 +59:04:27.2
%V z 1593 0.005327 [0.000060] D 2002LEDA.........0P
%D 1.673 1.657 75 (32767) (I) C 2006AJ....131.1163S
%T 5 =32800000 D 2011A&A...532A..74B
%#B 140


#====Done (2013-Feb-12,16:37:11z)===="""

_cached_ngc3642["vizier"] = """# NGC 3642    #Q22523677
#=V=VizieR (local):    1
%J 170.56 +59.08 = 11:22.2     +59:05
%I.0 {NGC} 3642



#====Done (2013-Feb-12,16:37:42z)===="""

_cached_ngc3642["all"] = """# ngc3642    #Q2779348
#=Si=Simbad, all IDs (via url):    1    41ms
%@ 503952
%I.0 NGC 3642
%C.0 LIN
%J 170.57458768232000 +59.07452101151000 = 11:22:17.90 +59:04:28.2
%J.E [0.2819 0.3347 90] A 2020yCat.1350....0G
%P -1.821 -0.458 [0.343 0.402 90] A 2020yCat.1350....0G
%X 0.4854 [0.3776] A 2020yCat.1350....0G
%V v 1583 5.3E-03 [1] D 2016A&A...595A.118V
%D 5.01 4.27 (O) D 2003A&A...412...45P
%T SA =2D800900 C 2019MNRAS.488..590B
%#B 203

#====Done (2024-Feb-15,11:26:16z)====
"""

_cached_castor = {}
_cached_castor["all"] = """# castor    #Q2779274
#=Si=Simbad, all IDs (via url):    1     0ms (from cache)
%@ 983633
%I.0 * alf Gem
%C.0 **
%J 113.649471640 +31.888282216 = 07:34:35.87 +31:53:17.8
%J.E [34.72 25.95 90] A 2007A&A...474..653V
%P -191.45 -145.19 [3.95 2.95 0] A 2007A&A...474..653V
%X 64.12 [3.75] A 2007A&A...474..653V
%V v 5.40 1.8E-05 [0.5] A 2006AstL...32..759G
%S A1V+A2Vm =0.0000D200.0030.0110000000100000 E ~
%#B 260



#====Done (2024-Feb-15,11:25:36z)===="""

_cached_castor["simbad"] = """# castor    #Q22524495
#=S=Simbad (via url):    1
%@ 983633
%I.0 NAME CASTOR
%C.0 **
%C.N0 12.13.00.00
%J 113.649471640 +31.888282216 = 07:34:35.87 +31:53:17.8
%J.E [34.72 25.95 0] A 2007A&A...474..653V
%P -191.45 -145.19 [3.95 2.95 0] A 2007A&A...474..653V
%X 64.12 [3.75] A 2007A&A...474..653V
%S A1V+A2Vm =0.0000D200.0030.0110000000100000 C 2001AJ....122.3466M
%#B 179


#====Done (2013-Feb-12,17:00:39z)===="""


@pytest.mark.remote_data
def test_names():
    # First check that sesame is up
    if (
        urllib.request.urlopen("https://cdsweb.unistra.fr/cgi-bin/nph-sesame").getcode()
        != 200
    ):
        pytest.skip(
            "SESAME appears to be down, skipping test_name_resolve.py:test_names()..."
        )

    # "all" choice should ask for SIMBAD, then NED, then Vizier: "SNV" in the url
    with pytest.raises(
        NameResolveError,
        # avoid hard-coding an exact url as it might depend on external state
        match=r"Unable to find coordinates for name 'm87h34hhh' using http.*SNV.*",
    ):
        get_icrs_coordinates("m87h34hhh")

    try:
        icrs = get_icrs_coordinates("NGC 3642")
    except NameResolveError:
        ra, dec = _parse_response(_cached_ngc3642["all"])
        icrs = SkyCoord(ra=float(ra) * u.degree, dec=float(dec) * u.degree)

    icrs_true = SkyCoord(ra="11h 22m 18.014s", dec="59d 04m 27.27s")

    # use precision of only 1 decimal here and below because the result can
    # change due to Sesame server-side changes.
    np.testing.assert_almost_equal(icrs.ra.degree, icrs_true.ra.degree, 1)
    np.testing.assert_almost_equal(icrs.dec.degree, icrs_true.dec.degree, 1)

    try:
        icrs = get_icrs_coordinates("castor")
    except NameResolveError:
        ra, dec = _parse_response(_cached_castor["all"])
        icrs = SkyCoord(ra=float(ra) * u.degree, dec=float(dec) * u.degree)

    icrs_true = SkyCoord(ra="07h 34m 35.87s", dec="+31d 53m 17.8s")
    np.testing.assert_almost_equal(icrs.ra.degree, icrs_true.ra.degree, 1)
    np.testing.assert_almost_equal(icrs.dec.degree, icrs_true.dec.degree, 1)


@pytest.mark.remote_data
def test_name_resolve_cache(tmp_path):
    target_name = "castor"
    (temp_cache_dir := tmp_path / "cache").mkdir()
    with paths.set_temp_cache(temp_cache_dir):
        assert not get_cached_urls()  # sanity check
        icrs = get_icrs_coordinates(target_name, cache=True)
        urls = get_cached_urls()
        assert len(urls) == 1
        assert any(map(urls[0].startswith, sesame_url.get()))
        # Try reloading coordinates, now should just reload cached data:
        with no_internet():
            assert get_icrs_coordinates(target_name, cache=True) == icrs
        assert get_cached_urls() == urls


def test_names_parse():
    # a few test cases for parsing embedded coordinates from object name
    test_names = [
        "CRTS SSS100805 J194428-420209",
        "MASTER OT J061451.7-272535.5",  # codespell:ignore ot
        "2MASS J06495091-0737408",
        "1RXS J042555.8-194534",
        "SDSS J132411.57+032050.5",
        "DENIS-P J203137.5-000511",
        "2QZ J142438.9-022739",
        "CXOU J141312.3-652013",
    ]
    for name in test_names:
        sc = get_icrs_coordinates(name, parse=True)


@pytest.mark.remote_data
@pytest.mark.parametrize(
    ("name", "db_dict"), [("NGC 3642", _cached_ngc3642), ("castor", _cached_castor)]
)
def test_database_specify(name, db_dict):
    # First check that at least some sesame mirror is up
    for url in sesame_url.get():
        if urllib.request.urlopen(url).getcode() == 200:
            break
    else:
        pytest.skip(
            "All SESAME mirrors appear to be down, skipping "
            "test_name_resolve.py:test_database_specify()..."
        )

    for db in db_dict.keys():
        with sesame_database.set(db):
            icrs = SkyCoord.from_name(name)

        time.sleep(1)
