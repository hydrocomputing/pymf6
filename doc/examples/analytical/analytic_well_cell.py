"""Analytic well in one cell."""

from math import sqrt

import numpy as np

from pymf6.api import create_mutable_bc


class AnalyticWell:
    """Analytic model of a well inside one MF6 cells."""

    def __init__(self, gwf):
        self.gwf = gwf
        self.cell_coords = self._get_cell_coords(self.gwf)
        self.center_coord = self.cell_coords['center']
        self.aquifer_properties = self._get_cell_properties(
            self.gwf, self.center_coord
        )
        self.xys = self._get_xy_values(self.gwf, self.cell_coords)
        self.distances = self._get_distances(self.xys)

    @staticmethod
    def _get_cell_coords(gwf):
        """Get coordinate of neighboring cells."""
        # layer, row, col
        wel = create_mutable_bc(gwf.wel)
        center_coord = wel.nodelist[0]
        cell_coords = {'center': center_coord}
        cell_coords['left'] = (
            center_coord[0],
            center_coord[1],
            center_coord[2] - 1,
        )
        cell_coords['right'] = (
            center_coord[0],
            center_coord[1],
            center_coord[2] + 1,
        )
        cell_coords['top'] = (
            center_coord[0],
            center_coord[1] + 1,
            center_coord[2],
        )
        cell_coords['bot'] = (
            center_coord[0],
            center_coord[1] - 1,
            center_coord[2],
        )
        cell_coords['bot_left'] = (
            center_coord[0],
            center_coord[1] - 1,
            center_coord[2] - 1,
        )
        cell_coords['bot_right'] = (
            center_coord[0],
            center_coord[1] - 1,
            center_coord[2] + 1,
        )
        cell_coords['top_left'] = (
            center_coord[0],
            center_coord[1] + 1,
            center_coord[2] - 1,
        )
        cell_coords['top_right'] = (
            center_coord[0],
            center_coord[1] + 1,
            center_coord[2] + 1,
        )
        return cell_coords

    @staticmethod
    def _get_cell_properties(gwf, well_coord):
        """Get  properties of well cell."""
        properties = {}
        top = gwf.dis.top.values.__getitem__(well_coord)
        bot = gwf.dis.bot.values.__getitem__(well_coord)
        properties['z'] = [top - bot, 0]
        properties['kaq'] = gwf.npf.k11.values.__getitem__(well_coord)
        properties['ss'] = gwf.sto.ss.values.__getitem__(well_coord)
        properties['sy'] = gwf.sto.sy.values.__getitem__(well_coord)
        return properties

    @staticmethod
    def _get_xy_values(gwf, cell_coords):
        """Calculate xy values for all points."""
        delc = gwf.dis.get_advanced_var('delc')
        dlr = gwf.dis.get_advanced_var('delr')
        xs = np.add.accumulate(delc)
        ys = np.add.accumulate(dlr)
        xys = {}
        for name, coord in cell_coords.items():
            xys['cell_' + name] = (
                (xs[coord[2]] + xs[coord[2] - 1]) / 2,
                (ys[coord[1]] + ys[coord[1] - 1]) / 2,
            )
        center_x, center_y = xys['cell_center']
        half_width = delc[cell_coords['center'][0]] / 2
        half_height = dlr[cell_coords['center'][1]] / 2
        left = center_x - half_width
        right = center_x + half_width
        top = center_y + half_height
        bot = center_y - half_height
        corner_xys = {}
        corner_xys['corner_left'] = (left, center_y)
        corner_xys['corner_top_left'] = (left, top)
        corner_xys['corner_top'] = (center_x, top)
        corner_xys['corner_top_right'] = (right, top)
        corner_xys['corner_right'] = (right, center_y)
        corner_xys['corner_bot_right'] = (right, bot)
        corner_xys['corner_bot'] = (center_x, bot)
        corner_xys['corner_bot_left'] = (left, bot)
        xys.update(corner_xys)
        return xys

    @staticmethod
    def _get_distances(xys):
        """Calculate distances between points for head interpolation."""
        # (from_center, from_outer)
        center_x, center_y = xys['cell_center']
        distances = {}
        left_x, left_y = xys['cell_left']
        top_left_x, top_left_y = xys['cell_top_left']
        top_x, top_y = xys['cell_top']
        corner_left_x, corner_left_y = xys['corner_left']
        corner_top_left_x, corner_top_left_y = xys['corner_top_left']
        corner_top_x, corner_top_y = xys['corner_top']
        corner_top_right_x, corner_top_right_y = xys['corner_top_right']
        top_right_x, top_right_y = xys['cell_top_right']
        corner_right_x, corner_right_y = xys['corner_right']
        right_x, right_y = xys['cell_right']
        bot_right_x, bot_right_y = xys['cell_bot_right']
        corner_bot_x, corner_bot_y = xys['corner_bot']
        corner_bot_right_x, corner_bot_right_y = xys['corner_bot_right']
        bot_x, bot_y = xys['cell_bot']
        corner_bot_left_x, corner_bot_left_y = xys['corner_bot_left']
        bot_left_x, bot_left_y = xys['cell_bot_left']
        distances['left'] = (center_x - corner_left_x, corner_left_x - left_x)
        distances['top_left'] = (
            sqrt(
                (center_x - corner_top_left_x) ** 2
                + (center_y - corner_top_left_y) ** 2
            ),
            sqrt(
                (top_left_x - corner_top_left_x) ** 2
                + (top_left_y - corner_top_left_y) ** 2
            ),
        )
        distances['top'] = (corner_top_y - center_y, top_y - corner_top_y)
        distances['top_right'] = (
            sqrt(
                (corner_top_right_x - center_x) ** 2
                + (corner_top_right_y - center_y) ** 2
            ),
            sqrt(
                (top_right_x - corner_top_right_x) ** 2
                + (top_right_y - corner_top_right_y) ** 2
            ),
        )
        distances['right'] = (
            corner_right_x - center_x,
            right_x - corner_right_x,
        )
        distances['bot_right'] = (
            sqrt(
                (corner_bot_right_x - center_x) ** 2
                + (corner_bot_right_y - center_y) ** 2
            ),
            sqrt(
                (bot_right_x - corner_bot_right_x) ** 2
                + (corner_bot_right_y - bot_right_y) ** 2
            ),
        )
        distances['bot'] = (center_y - corner_bot_y, corner_bot_y - bot_y)
        distances['bot_left'] = (
            sqrt(
                (corner_bot_left_x - center_x) ** 2
                + (corner_bot_left_y - center_y) ** 2
            ),
            sqrt(
                (bot_left_x - corner_bot_left_x) ** 2
                + (corner_bot_left_y - bot_left_y) ** 2
            ),
        )
        return distances

    @property
    def neighbor_heads(self):
        """Heads of neighboring cells."""
        return {
            name: self.gwf.X.__getitem__(coord)
            for name, coord in self.cell_coords.items()
        }

    @property
    def border_heads(self):
        """Interpolated heads at cell border ."""
        # (from_center, from_outer)
        center_head = self.neighbor_heads['center']
        heads = {}
        for name, distance in self.distances.items():
            outer_head = self.neighbor_heads[name]
            heads[name] = (
                center_head * distance[0] + outer_head * distance[1]
            ) / sum(distance)
        return heads
