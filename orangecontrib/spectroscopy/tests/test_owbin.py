import numpy as np
import Orange
from Orange.widgets.tests.base import WidgetTest
from orangecontrib.spectroscopy.widgets.owbin import OWBin


class TestOWBin(WidgetTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mosaic = Orange.data.Table("agilent/5_mosaic_agg1024.dmt")

    def setUp(self):
        self.widget = self.create_widget(OWBin)

    def test_load_unload(self):
        # just to load the widget (it has no inputs)
        pass

    def test_bin(self):
        self.send_signal(OWBin.Inputs.data, self.mosaic)
        self.widget.bin_sqrt = 2
        self.widget.commit()
        m = self.get_output(OWBin.Outputs.bindata)
        np.testing.assert_equal(len(m.X), len(self.mosaic.X) / 2**2)
        x_coords = self.mosaic[:, "map_x"].metas[0:4, 0]
        x_coords_binned = np.array([x_coords[0:2].mean(), x_coords[2:4].mean()])
        np.testing.assert_equal(m[:, "map_x"].metas[0:2, 0], x_coords_binned)
        y_coords = self.mosaic[:, "map_y"].metas[::4, 0]
        y_coords_binned = np.array([y_coords[0:2].mean(), y_coords[2:4].mean(),
                                    y_coords[4:6].mean(), y_coords[6:8].mean()])
        np.testing.assert_equal(m[:, "map_y"].metas[::2, 0], y_coords_binned)

    def test_invalid_bin(self):
        self.send_signal(OWBin.Inputs.data, self.mosaic)
        self.widget.bin_sqrt = 3
        self.widget.commit()
        self.assertTrue(self.widget.Error.invalid_block.is_shown())
        self.assertIsNone(self.get_output(OWBin.Outputs.bindata))

    def test_invalid_axis(self):
        data = self.mosaic.copy()
        data.metas[:, 0] = np.nan
        self.send_signal(OWBin.Inputs.data, data)
        self.assertTrue(self.widget.Error.invalid_axis.is_shown())
        self.send_signal(OWBin.Inputs.data, None)
        self.assertFalse(self.widget.Error.invalid_axis.is_shown())