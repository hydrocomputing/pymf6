"""Bulding MF6 basis model with `flopy`
"""

from copy import deepcopy
from pathlib import Path

from matplotlib import pyplot as plt
import matplotlib as mpl
import flopy
import flopy.mf6 as mf6


class BaseModel:
    """A base model that can run allone or can be modified.

    Modify by:

    1. Providing a diffrent `data` dictionary with model
    2. Overriding or adding new `make_xxx` methods

    Hint: Read the MODFLOW 6 manual for the package names such as `DIS``
          or `OC`.
    """
    #  pylint: disable-msg=too-many-instance-attributes
    def __init__(
            self, name, data, sim_path=Path('.simulations',),
            exe_name='mf6'):
        self.name = name
        self.sim_path = sim_path / name
        self._budget_file = f'{name}.bud'
        self._head_file = f'{name}.hds'
        self.data = data
        self.sim = sim = mf6.MFSimulation(
            sim_name=name, sim_ws=str(self.sim_path), exe_name=exe_name)
        self.gwf = mf6.ModflowGwf(sim, modelname=name, save_flows=True)

    def make_tdis(self, data=None):
        """Create data for `TDIS` package
        """
        if data is None:
            data = self.data['tdis']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.tdis = mf6.ModflowTdis(self.sim, **self._clean_time_data(data))

    def make_ims(self, data=None):
        """Create data for `IMS` package
        """
        if data is None:
            data = self.data['ims']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.ims = mf6.ModflowIms(self.sim, **self._clean_solver_data(data))

    def make_dis(self, data=None):
        """Create data for `DIS` package
        """
        if data is None:
            data = self.data['dis']
        #  pylint: disable-msg=attribute-defined-outside-init
        self._mf6_dis_data = self._clean_dis_data(data)
        self.dis = mf6.ModflowGwfdis(self.gwf, **self._mf6_dis_data)

    def make_ic(self, data=None):
        """Create data for `IC` package
        """
        if data is None:
            data = self.data['ic']
        #  pylint: disable-msg=invalid-name, attribute-defined-outside-init
        self.ic = mf6.ModflowGwfic(self.gwf, **self._clean_init_data(data))

    def make_npf(self, data=None):
        """Create data for `NPF` package
        """
        if data is None:
            data = self.data['npf']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.npf = mf6.ModflowGwfnpf(
            self.gwf,
            save_specific_discharge=True,
            **self._clean_npf_data(data))

    def make_oc(self):
        """Create data for `OC` package
        """
        #  pylint: disable-msg=invalid-name, attribute-defined-outside-init
        self.oc = mf6.ModflowGwfoc(
            self.gwf,
            budget_filerecord=self._budget_file,
            head_filerecord=self._head_file,
            saverecord=[('HEAD', 'ALL'), ('BUDGET', 'ALL')])

    def make_sto(self, data=None):
        """Create data for `STO` package
        """
        if data is None:
            data = self.data['sto']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.sto = mf6.ModflowGwfsto(
            self.gwf, save_flows=True, **self._clean_sto_data(data))

    def make_rch(self, data=None):
        """Create data for `RCH`(a) package
        """
        if data is None:
            data = self.data['rch']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.rch = mf6.ModflowGwfrcha(
            self.gwf, **self._clean_recharge_data(data))

    def make_chd(self, data=None):
        """Create data for `CHD` package
        """
        if not hasattr(self, '_mf6_dis_data'):
            self.make_dis()
        if data is None:
            data = self.data['chd']
        #  pylint: disable-msg=attribute-defined-outside-init
        self.chd = mf6.ModflowGwfchd(
            self.gwf,
            **self._clean_chd_data(data, self._mf6_dis_data))

    def make_wel(self, data=None):
        """Create data for `WEL`package
        """
        if data is None:
            data = self.data['wel']
        self.wel = mf6.ModflowGwfwel(
            self.gwf,
            boundnames=True,
            save_flows=True,
            **self._clean_wel_data(data))

    @staticmethod
    def _clean_solver_data(solver_data):
        solver_mf6 = deepcopy(solver_data)
        solver_mf6['complexity'] = solver_mf6['complexity'].upper()
        return solver_mf6

    @staticmethod
    def _clean_time_data(time_data):
        time_converters = {'s': 1, 'd': 86400}
        multiplier = 1
        time_mf6 = deepcopy(time_data)
        time_mf6['time_units'] = time_mf6['time_units'].upper()
        time_mf6['nper'] = len(time_mf6['stress_periods'])
        periods = time_mf6['perioddata'] = []
        for period in time_mf6['stress_periods']:
            periods.append((period['lenght'] * time_converters[period['unit']],
                            period['lenght'],
                            multiplier))
        del time_mf6['stress_periods']
        return time_mf6

    @staticmethod
    def _clean_dis_data(dis):
        dis_mf6 = deepcopy(dis)
        dis_mf6['delr'] = dis['len_x'] / dis['ncol']
        dis_mf6['delc'] = dis['len_y'] / dis['nrow']
        dis_mf6['botm'] = [dis['upper_bot'], dis['lower_bot']]
        for name in ['len_x', 'len_y', 'upper_bot', 'lower_bot']:
            del dis_mf6[name]
        dis_mf6['length_units'] = dis_mf6['length_units'].upper()
        return dis_mf6

    @staticmethod
    def _clean_init_data(init):
        init_mf6 = deepcopy(init)
        init_mf6['strt'] = init_mf6['initial_head']
        del init_mf6['initial_head']
        return init_mf6

    @staticmethod
    def _clean_npf_data(npf_data):
        sat_mapping = {'variable': 1, 'constant': 0, 'compute': -1}
        npf_mf6 = deepcopy(npf_data)
        npf_mf6['icelltype'] = [
            sat_mapping[sat_type] for sat_type in npf_mf6['sat_thickness']]
        npf_mf6['k'] = npf_mf6['k_h']
        npf_mf6['k33'] = npf_mf6['k_v']
        for name in ['sat_thickness', 'k_h', 'k_v']:
            del npf_mf6[name]
        return npf_mf6

    @staticmethod
    def _clean_sto_data(sto_data):
        sto_mf6 = deepcopy(sto_data)
        con_mapping = {'convertable': 1, 'confined': 0}
        sto_mf6['iconvert'] = [
            con_mapping[con_type] for con_type in sto_mf6['convert']]
        del sto_mf6['convert']
        return sto_mf6

    @staticmethod
    def _clean_recharge_data(recharge_data):
        rch_mf6 = deepcopy(recharge_data)
        # year mm/a --> m/s 31.5e6 s/a
        rch_mf6['recharge'] = rch_mf6['recharge'] / 3.15e10
        return rch_mf6

    @staticmethod
    def _clean_chd_data(constant_head_data, clean_dis_data):
        chd_mf6 = deepcopy(constant_head_data)
        chd_mf6['stress_period_data'] = {}
        for iper, period in enumerate(chd_mf6['stress_periods']):
            heads = []
            for layer in range(clean_dis_data['nlay']):
                for row in range(clean_dis_data['nrow']):
                    heads.append(((layer, row, 0), period['h_west']))
                    last_pos = clean_dis_data['ncol'] - 1
                    heads.append(((layer, row, last_pos), period['h_east']))
            chd_mf6['stress_period_data'][iper] = heads
        chd_mf6['maxbound'] = len(chd_mf6['stress_period_data'])
        del chd_mf6['stress_periods']
        return chd_mf6

    def _clean_wel_data(self, wel_data):
        keys = list(wel_data.keys())
        wel = {}
        wel['maxbound'] = len(keys)
        stress_periods = range(len(wel_data[keys[0]]['rates']))
        empty = flopy.mf6.ModflowGwfwel.stress_period_data.empty
        stresses = empty(
            self.gwf, maxbound=wel['maxbound'], boundnames=True,
            stress_periods=stress_periods)
        for period in range(len(stresses)):
            for index, well in enumerate(wel_data.values()):
                stresses[period][index] = (
                    well['coords'],
                    well['rates'][period],
                    well['name']
                )
        wel['stress_period_data'] = stresses
        return wel

    def write_simulation(self):
        """Write the MF6 input files.
        """
        names = list(self.data.keys())
        names.append('oc')
        for name in names:
            if not hasattr(self, name):
                getattr(self, f'make_{name}')()
        self.sim.write_simulation()

    def run_simulation(self):
        """Run the MF6 simulation.
        """
        self.sim.run_simulation()

    def plot_head(self, show=False, save=True, layers=2):
        """Plot the head.
        """
        head_path = self.sim_path / self._head_file
        head = flopy.utils.HeadFile(str(head_path)).get_data()
        vmin = head.min()
        vmax = head.max()

        fig, axes = plt.subplots(nrows=layers, ncols=1,
                                 sharex=True, sharey=True)
        for layer, ax in enumerate(axes.flat):
            pmv = flopy.plot.PlotMapView(self.gwf, layer=layer, ax=ax)
            head_plot = pmv.plot_array(head, vmin=vmin, vmax=vmax)

        cax, kw = mpl.colorbar.make_axes([ax for ax in axes.flat])
        plt.colorbar(head_plot, cax=cax, **kw)
        if save:
            plt.savefig(f'{self.name}.png')
