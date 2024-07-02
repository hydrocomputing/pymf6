"""Analytic well in one cell."""

from math import sqrt

import numpy as np
import timml as tml
import ttim

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
        self.corner_coords = {
            name.split('_', 1)[-1]: value
            for name, value in self.xys.items()
            if name.startswith('corner')
        }

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
        corner_xys['corner_top_left'] = (left, top)
        corner_xys['corner_top'] = (center_x, top)
        corner_xys['corner_top_right'] = (right, top)
        corner_xys['corner_right'] = (right, center_y)
        corner_xys['corner_bot_right'] = (right, bot)
        corner_xys['corner_bot'] = (center_x, bot)
        corner_xys['corner_bot_left'] = (left, bot)
        corner_xys['corner_left'] = (left, center_y)
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
        distances['left'] = (center_x - corner_left_x, corner_left_x - left_x)
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

    def calc_well_head(self, well_q):
        """Calculate well head analytically."""
        xy, hls = self._make_xy_hls(border_heads=self.border_heads,
                                    coords=self.corner_coords)
        steady_state_model = self._make_steady_state_model(
            aquifer_properties=self.aquifer_properties,
            center_head=self.neighbor_heads['center'],
            center_coords=self.xys['cell_center'],
            xy=xy,
            hls=hls
        )
        tsandh = [(0, 0)] * len(hls)
        end_time = 1
        transient_model, well =  self._make_transient_model(
            aquifer_properties=self.aquifer_properties,
            well_coords=self.xys['cell_center'],
            end_time=end_time,
            xy=xy,
            tsandh=tsandh,
            well_q=well_q,
            steady_state_model=steady_state_model,
        )
        return transient_model, well.headinside(end_time)[0, 0]

    @staticmethod
    def _make_xy_hls(border_heads, coords):
        border_names = list(border_heads)
        border_names.append(border_names[0])
        xy = []
        hls = []
        for name in border_names:
            x, y = coords[name][0], coords[name][1]
            xy.append((x, y))
            hls.append(border_heads[name])
        return xy, hls

    @staticmethod
    def _make_steady_state_model(
        aquifer_properties,
        xy,
        hls,
        center_head,
        center_coords,
        delta=0.1,
    ):
        """Create a TimML model for initial conditions."""
        model = tml.ModelMaq(
            kaq=aquifer_properties['kaq'],
            z=aquifer_properties['z'],
            npor=aquifer_properties['ss'],
        )
        tml.HeadLineSinkString(
            model,
            xy=xy,
            hls=hls,
            order=5,
        )
        tml.HeadLineSink(
            model,
            x1=center_coords[0] - delta,
            y1=center_coords[1],
            x2=center_coords[0] + delta,
            y2=center_coords[1],
            hls=center_head,
        )
        model.solve(silent=True)
        return model

    @staticmethod
    def _make_transient_model(
            aquifer_properties,
            well_coords,
            end_time,
            xy,
            tsandh,
            well_q,
            steady_state_model,
        ):
        """Create a TTim model."""
        model = ttim.ModelMaq(
            aquifer_properties['kaq'],
            z=aquifer_properties['z'],
            Saq=aquifer_properties['ss'],
            phreatictop=True,
            tmin=1e-3,
            tmax=end_time,
            porll=aquifer_properties['ss'],
            timmlmodel=steady_state_model,
        )
        ttim.HeadLineSinkString(
            model,
            xy=xy,
            tsandh=tsandh,
        )
        well = ttim.Well(
            model,
            xw=well_coords[0],
            yw=well_coords[1],
            rw=0.3,
            res=0,
            rc=0,
            tsandQ=[(0, well_q)],
            label='well',
        )
        model.solve(silent=True)

        return model, well
