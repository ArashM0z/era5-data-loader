"""ERA5 NetCDF/Zarr loader with bbox + time-range subsetting + regridding."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


@dataclass(frozen=True)
class BBox:
    south: float
    north: float
    west: float
    east: float

    def __post_init__(self) -> None:
        if self.south >= self.north:
            raise ValueError("south must be < north")
        if self.west >= self.east:
            raise ValueError("west must be < east")


def load_era5(path: str | Path,
              *, variables: list[str] | None = None,
              engine: str | None = None) -> xr.Dataset:
    """Open an ERA5 file (NetCDF or Zarr) and optionally select variables.

    Args:
        path: a file path; ``.zarr`` directories open via the zarr engine,
            anything else uses the default netCDF engine.
        variables: optional list of variable names to keep.
        engine: override the xarray engine detection.
    """
    p = Path(path)
    engine = engine or ("zarr" if p.suffix == ".zarr" else None)
    ds = xr.open_dataset(p, engine=engine)
    # ERA5 conventions: rename `time`/`latitude`/`longitude` if needed
    rename = {}
    for cand, target in (("time", "time"), ("latitude", "lat"),
                         ("longitude", "lon")):
        if cand in ds.coords and target not in ds.coords:
            rename[cand] = target
    if rename:
        ds = ds.rename(rename)
    if variables is not None:
        missing = [v for v in variables if v not in ds.data_vars]
        if missing:
            raise KeyError(f"missing variables in dataset: {missing}")
        ds = ds[variables]
    return ds


def subset(ds: xr.Dataset, bbox: BBox | None = None,
           time_range: tuple[str, str] | None = None) -> xr.Dataset:
    """Subset by bbox (lat / lon) and ISO 8601 time range."""
    out = ds
    if bbox is not None:
        out = out.sel(lat=slice(bbox.north, bbox.south),
                      lon=slice(bbox.west, bbox.east))
        if out.sizes.get("lat", 0) == 0:
            # ERA5 latitudes are often descending; fall back to ascending slice
            out = ds.sel(lat=slice(bbox.south, bbox.north),
                         lon=slice(bbox.west, bbox.east))
    if time_range is not None:
        start, end = pd.to_datetime(time_range[0]), pd.to_datetime(time_range[1])
        if start >= end:
            raise ValueError("time_range start must be < end")
        out = out.sel(time=slice(start, end))
    return out


def regrid_to(ds: xr.Dataset, lats: np.ndarray, lons: np.ndarray,
              method: str = "linear") -> xr.Dataset:
    """Interpolate the dataset to the given lat/lon grid."""
    return ds.interp(lat=lats, lon=lons, method=method)
