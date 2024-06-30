"""
Analytical model creator.

Use Tim ML and TTim to create an equivalent model.
"""

import timml as tml
import ttim

from base_data import BASE_MODEL_DATA


class ModelPropterty:
    """Container for properties."""


class AnalyticModel:
    """Analytical model using Tim ML and TTim."""

    def __init__(self, base_data=None, extra_data=None, solve=True):
        if base_data is None:
            base_data = BASE_MODEL_DATA.copy()
        if extra_data is not None:
            base_data.update(extra_data)
        self.solve = solve
        self.end_time = 100
        self.geometry_data = self._make_geometry_data(base_data)
        self.aquifer_data = self._make_aquifer_data(base_data)
        self.well_data = self._make_well_data(base_data)
        self.chd_data = self._make_chd_data(base_data)
        self.steady_state_model = self._make_steady_state_model()
        self.transitent_model = self._make_transitent_model()

    @staticmethod
    def _make_geometry_data(base_data):
        geometry_data = ModelPropterty()
        xy_end = base_data['model_width'] + 0.1
        geometry_data.xy_start = 0
        geometry_data.xy_end = xy_end
        geometry_data.z = [base_data['cell_thickness'], 0]
        return geometry_data

    @staticmethod
    def _make_aquifer_data(base_data):
        aquifer_data = ModelPropterty()
        aquifer_data.Saq = 0.2
        aquifer_data.kaq = 10
        return aquifer_data

    def _make_well_data(self, base_data):
        well_data = ModelPropterty()
        xy_end = self.geometry_data.xy_end
        well_data.x = xy_end // 2
        well_data.y = xy_end // 2
        well_data.q = -base_data['q']
        well_data.radius = base_data['well_radius']
        well_data.screen_resistance = base_data['well_screen_resistance']
        well_data.caisson_radius = base_data['well_caisson_radius']
        return well_data

    @staticmethod
    def _make_chd_data(base_data):
        chd_data = ModelPropterty()
        chd_data.left = base_data['chd_left']
        chd_data.right = base_data['chd_right']
        return chd_data

    def _make_steady_state_model(self):
        """Create a TimML model."""
        steady_state_ml = tml.ModelMaq(
            kaq=self.aquifer_data.kaq,
            z=self.geometry_data.z,
            npor=self.aquifer_data.Saq,
        )
        tml.HeadLineSink1D(
            steady_state_ml,
            xls=self.geometry_data.xy_start,
            hls=self.chd_data.left,
        )
        tml.HeadLineSink1D(
            steady_state_ml,
            xls=self.geometry_data.xy_end,
            hls=self.chd_data.right,
        )
        if self.solve:
            steady_state_ml.solve(silent=True)
        return steady_state_ml

    def _make_transitent_model(self):
        """Create transient model."""
        ml = ttim.ModelMaq(
            kaq=self.aquifer_data.kaq,
            z=self.geometry_data.z,
            Saq=self.aquifer_data.Saq,
            phreatictop=True,
            tmin=1e-3,
            tmax=self.end_time,
            porll=self.aquifer_data.Saq,
            timmlmodel=self.steady_state_model,
        )
        xy_start = self.geometry_data.xy_start
        xy_end = self.geometry_data.xy_end
        well_x = self.well_data.x
        well_y = self.well_data.y
        # upper_wall
        ttim.LeakyLineDoublet(
            ml, x1=xy_start, x2=xy_end, y1=xy_end, y2=xy_end, label='upper_wall'
        )
        # lower_wall
        ttim.LeakyLineDoublet(
            ml,
            x1=xy_start,
            x2=xy_end,
            y1=xy_start,
            y2=xy_start,
            label='lower_wall',
        )
        # rb_left
        ttim.HeadLineSink(
            ml,
            x1=xy_start,
            x2=xy_start,
            y1=xy_start,
            y2=xy_end,
            tsandh=[(0, 0)],
            label='rb_left',
        )
        # rb_right
        ttim.HeadLineSink(
            ml,
            x1=xy_end,
            x2=xy_end,
            y1=xy_start,
            y2=xy_end,
            tsandh=[(0, 0)],
            label='rb_right',
        )
        # well
        ttim.Well(
            ml,
            well_x,
            well_y,
            rw=self.well_data.radius,
            res=self.well_data.screen_resistance,
            rc=self.well_data.caisson_radius,
            tsandQ=[(0, self.well_data.q)],
            label='well',
        )
        if self.solve:
            ml.solve(silent=True)
        return ml

    def get_well_head(self, x_offset=0.25):
        """Get well heads."""
        model = self.transitent_model
        well_x = self.well_data.x
        well_y = self.well_data.y
        end_time = self.end_time
        well = model.elementdict['well']
        result = {
            'head_inside_well': well.headinside(end_time)[0, 0],
            'well_cell_head': model.head(well_x, well_y, end_time)[0, 0],
            'well_offset_head': model.head(well_x + x_offset, well_y, end_time)[
                0, 0
            ],
        }
        return result

    def plot_contour(self):
        """PLot contur at las time step."""
        xy_start = self.geometry_data.xy_start
        xy_end = self.geometry_data.xy_end
        self.transitent_model.contour(
            win=[xy_start, xy_end, xy_start, xy_end],
            ngr=40,
            t=self.end_time,
            labels=True,
            decimals=1,
        )
