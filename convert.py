import argparse

import topojson as tp
import shapefile

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("shapefile", help="shapefile to convert")
    p.add_argument("dest", help="name of the topojson file to output")
    args = p.parse_args()
    print(args.shapefile, args.dest)

    data = shapefile.Reader(args.shapefile)
    topo = tp.Topology(data)
    open(args.dest, "w").write(topo.to_json())
