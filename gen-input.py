#!/bin/env python3
'''
Generate random input for the routers. See `io_schema.md`.
Requirements:
    - python3 3.8.2
    - python3-pip 20.0.2
    $ pip3 install --user numpy
For help: python gen-input.py --help
Example: python gen-input.py -d 2 -h 50,100 -w 100,10000 -n 100 -v 5 > inputs/test1.json
'''
import argparse
import json
import random
import sys
from argparse import RawTextHelpFormatter

import numpy as np


def rand_from_str(s: str) -> int:
    # s = '1,2' or s = '1'
    s = [int(x) for x in s.split(',')]
    if len(s) == 2:
        return random.randint(*s)
    else:
        return s[0]


def parse_args():
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-w', default='2,50',
                        help='width, a number or a range "start,end"')
    parser.add_argument('-h', default='2,50',
                        help='height, a number or a range "start,end"')
    parser.add_argument('-v', default='2',
                        help='VIAs, a number or a range "start,end"')
    parser.add_argument('-n',
                        help='destination cells, a number or a range "start,end"')
    parser.add_argument('-d', type=int, default=2,
                        choices=(1, 2), help='layers')
    args = parser.parse_args()

    args.w = rand_from_str(args.w)
    args.h = rand_from_str(args.h)
    args.v = rand_from_str(args.v)

    if args.n is None:
        args.n = random.randint(1, args.h*args.w-1-args.v)
    else:
        args.n = rand_from_str(args.n)

    assert args.w > 0 and args.h > 0 and args.d > 0 and args.n > 0, 'all numbers must be non negative'
    assert args.n <= (args.w * args.h) - 1,\
        'cant fit the number of destination cells'
    assert args.v <= (args.w * args.h) - 1 - args.n,\
        f'no avaialable area for {args.v} VIAs, only have {(args.w * args.h) - 1 - args.n}'

    return args


def write_out(grid: list, src_coor: list, dest_coor: list):
    json.dump({
        "grid": grid,
        "src_coor": src_coor,
        "dest_coor": dest_coor
    }, sys.stdout)


def rand_coord(d, h, w):
    return [
        random.randint(0, d-1),
        random.randint(0, h-1),
        random.randint(0, w-1)
    ]


def add_vias(grid, v, h, w, src_coor, dest_coor):
    for i in range(v):
        placed = False
        while not placed:
            via_coor_x = random.randint(0, w-1)
            via_coor_y = random.randint(0, h-1)
            if not ([0, via_coor_y, via_coor_x] == src_coor or [1, via_coor_y, via_coor_x] == src_coor or
                    [0, via_coor_y, via_coor_x] in dest_coor or [1, via_coor_y, via_coor_x] in dest_coor):
                grid[0, via_coor_y, via_coor_x] = 2
                grid[1, via_coor_y, via_coor_x] = 2
                placed = True

    return grid


def clear_obstacle(a: [int], grid):
    grid[a[0]][a[1]][a[2]] = 0
    return grid


def rand_dest_coords(args):
    coords = []
    for _ in range(args.n):
        while True:
            coord = rand_coord(args.d, args.h, args.w)
            if coord not in coords:
                break

        coords.append(coord)

    return coords


if __name__ == "__main__":
    args = parse_args()

    grid = np.random.randint(2, size=(args.d, args.h, args.w), dtype='uint8')
    src_coor = rand_coord(args.d, args.h, args.w)
    dest_coor = rand_dest_coords(args)
    if args.d > 1:
        grid = add_vias(grid, args.v, args.h, args.w, src_coor, dest_coor)

    grid = clear_obstacle(src_coor, grid)
    for a in dest_coor:
        grid = clear_obstacle(a, grid)

    write_out(grid.tolist(), src_coor, dest_coor)
