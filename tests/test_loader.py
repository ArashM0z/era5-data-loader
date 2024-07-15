from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from era5.loader import BBox, load_era5, regrid_to, subset


def _make_era5(path: Path) -> Path:
    times = pd.date_range("2024-01-01", periods=4, freq="6h")
    lats = np.array([60.0, 50.0, 40.0])      # descending, ERA5 convention
    lons = np.array([-130.0, -100.0, -70.0])
    t2m = np.random.default_rng(0).normal(280, 5, (4, 3, 3)).astype(np.float32)
    ds = xr.Dataset(
        {"t2m": (("time", "latitude", "longitude"), t2m)},
        coords={"time": times, "latitude": lats, "longitude": lons},
    )
    out = path / "era5.nc"
    ds.to_netcdf(out)
    return out


def test_load_era5_renames_to_lat_lon(tmp_path):
    p = _make_era5(tmp_path)
    ds = load_era5(p)
    assert "lat" in ds.coords and "lon" in ds.coords


def test_subset_by_bbox_returns_inside_only(tmp_path):
    p = _make_era5(tmp_path)
    ds = load_era5(p)
    bbox = BBox(south=45.0, north=55.0, west=-120.0, east=-80.0)
    out = subset(ds, bbox=bbox)
    assert (out.lat <= 55.0).all() and (out.lat >= 45.0).all()


def test_subset_by_time_range(tmp_path):
    p = _make_era5(tmp_path)
    ds = load_era5(p)
    out = subset(ds, time_range=("2024-01-01T00:00", "2024-01-01T12:00"))
    assert out.sizes["time"] == 2 or out.sizes["time"] == 3


def test_bbox_validates_input():
    with pytest.raises(ValueError):
        BBox(south=10.0, north=10.0, west=0.0, east=1.0)


def test_missing_variable_raises(tmp_path):
    p = _make_era5(tmp_path)
    with pytest.raises(KeyError):
        load_era5(p, variables=["nope"])


def test_regrid_to_changes_resolution(tmp_path):
    p = _make_era5(tmp_path)
    ds = load_era5(p)
    out = regrid_to(ds, lats=np.linspace(40, 60, 5),
                    lons=np.linspace(-130, -70, 5))
    assert out.sizes["lat"] == 5
    assert out.sizes["lon"] == 5
