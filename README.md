# ERA5 Data Loader

xarray-based loader for ERA5-Land hourly reanalysis with bounding-box +
time-range subsetting and a simple bilinear regridder.

## What's in the box

- `load_era5(path, variables=…)` — opens NetCDF or Zarr, renames the
  `latitude`/`longitude`/`time` coordinates to the conventional
  `lat`/`lon`/`time`, and (optionally) selects variables.
- `subset(ds, bbox=…, time_range=…)` — slices in space (handles
  descending-latitude conventions used by ERA5) and time.
- `regrid_to(ds, lats, lons)` — bilinear interpolation onto an explicit
  target grid (e.g. a FIRMS pixel grid).
- `era5-fetch` CLI — either subsets a local file or, with `--config`
  and the `[cds]` extra, hits the Copernicus CDS API via `cdsapi`.

## Quickstart

```bash
pip install -e ".[dev]"
# offline subset
era5-fetch --input data/era5.nc \
           --bbox 49 60 -139 -110 \
           --time-start 2024-06-01 --time-end 2024-08-31 \
           --variables t2m u10 v10 \
           --out data/era5_west.nc
```

## CDS download config

```yaml
dataset: reanalysis-era5-land
request:
  variable: [2m_temperature, 10m_u_component_of_wind]
  year: [2024]
  month: [6, 7, 8]
  day: [1, 2, 3]
  area: [60, -139, 49, -110]   # [N, W, S, E]
  format: netcdf
```

## Layout

```
src/era5/
├── loader.py   # load + subset + regrid
└── cli.py      # era5-fetch (CDS download + offline subset)
tests/          # rename, bbox, time-range, validation, regrid
```
