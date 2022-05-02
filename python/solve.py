"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from pathlib import Path
from typing import Callable, Dict

from instance import Instance
from solution import Solution
from point import Point
from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def cover_matrix(instance):
    # 0 = not covered; 1 = covered/ not city
    # init matrix to all 1s
    side = instance.grid_side_length
    mat = [[1 for x in range(side)] for y in range(side)]
    # set coords of cities to 0
    cities = instance.cities
    for c in cities:
        x = c.x 
        y = c.y
        mat[x][y] = 0
    return mat 

def will_cover(cities, mat, tow, r):
    cov_cities = []
    for c in cities:
        if mat[c.x][c.y] == 0:
            dis = Point.distance_obj(c, tow)
            if (dis <= r):
                cov_cities.append(c)
    return cov_cities
                
def update_matrix(mat, cities):
    # uptdate cities that will be covered to 1 in matrix
    for c in cities:
        mat[c.x][c.y] = 1
    return mat

def solve_greedy(instance: Instance) -> Solution:
    # create matrix for whether city is covered or not
    mat = cover_matrix(instance)
    side = instance.grid_side_length
    towers = []
    uncovered = len(instance.cities)
    # loop through matrix, finding tower placement that covers most uncovered cities
    # continue until all cities are covered
    while uncovered > 0:
        # towers.append(Point(100, 100))
        max_cities = []
        max_tower = Point(0, 0)
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                tower = Point(i, j)
                covered = will_cover(instance.cities, mat, tower, instance.coverage_radius)
                if len(covered) > len(max_cities):
                    max_cities = covered
                    max_tower = tower

        mat = update_matrix(mat, max_cities)
        towers.append(max_tower)
        uncovered -= len(max_cities)
    return Solution(instance=instance, towers=towers)


SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "greedy": solve_greedy
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
