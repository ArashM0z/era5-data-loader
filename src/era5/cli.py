"""CLI: era5-fetch (CDS API) and offline subsetting."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import yaml

from era5.loader import BBox, load_era5, subset


def fetch_main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path,
                   help="YAML with cdsapi parameters")
    p.add_argument("--input", type=Path,
                   help="local NetCDF/Zarr to subset (skips CDS download)")
    p.add_argument("--bbox", nargs=4, type=float,
                   metavar=("S", "N", "W", "E"),
                   help="bounding box")
    p.add_argument("--time-start", type=str)
    p.add_argument("--time-end", type=str)
    p.add_argument("--variables", nargs="+")
    p.add_argument("--out", type=Path, required=True,
                   help="output NetCDF path")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args(argv)
    logging.basicConfig(level=args.log_level,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    if args.config and not args.input:
        cfg = yaml.safe_load(args.config.read_text())
        try:
            import cdsapi
        except ImportError as e:
            raise SystemExit("install era5-loader[cds] to use the CDS API") from e
        client = cdsapi.Client()
        client.retrieve(cfg["dataset"], cfg["request"], str(args.out))
        return 0

    if not args.input:
        raise SystemExit("provide --input or --config")
    ds = load_era5(args.input, variables=args.variables)
    bbox = BBox(*args.bbox) if args.bbox else None
    time_range = ((args.time_start, args.time_end)
                  if args.time_start and args.time_end else None)
    out = subset(ds, bbox=bbox, time_range=time_range)
    out.to_netcdf(args.out)
    logging.info("wrote %s", args.out)
    return 0
