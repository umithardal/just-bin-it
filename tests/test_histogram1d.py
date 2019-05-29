import pytest
import numpy as np
from histograms.histogram1d import Histogram1d


class TestHistogram1d:
    @pytest.fixture(autouse=True)
    def prepare(self):
        self.pulse_time = 1234
        self.num_bins = 5
        self.range = (0, 5)
        self.data = np.array([x for x in range(self.num_bins)])
        self.hist = Histogram1d("topic1", self.num_bins, self.range)

    def test_on_construction_histogram_is_initialised_empty(self):
        assert self.hist.x_edges is not None
        assert self.hist.shape == (self.num_bins,)
        assert len(self.hist.x_edges) == self.num_bins + 1
        assert self.hist.x_edges[0] == self.data[0]
        assert self.hist.x_edges[-1] == 5

    def test_adding_data_to_histogram_adds_data(self):
        self.hist.add_data(self.pulse_time, self.data)
        first_sum = sum(self.hist.data)

        # Add the data again
        self.hist.add_data(self.pulse_time, self.data)

        # Sum should be double
        assert sum(self.hist.data) == first_sum * 2

    def test_adding_data_outside_initial_bins_is_ignored(self):
        self.hist.add_data(self.pulse_time, self.data)
        first_sum = sum(self.hist.data)
        x_edges = self.hist.x_edges[:]

        # Add data that is outside the edges
        new_data = np.array([x + self.num_bins + 1 for x in range(self.num_bins)])
        self.hist.add_data(self.pulse_time, new_data)

        # Sum should not change
        assert sum(self.hist.data) == first_sum
        # Edges should not change
        assert np.array_equal(self.hist.x_edges, x_edges)

    def test_adding_preprocessing_step_affects_data_histogrammed(self):
        # Only add data if pulse time is even.
        def _preprocess_step(pulse_time, tofs, det_ids):
            if pulse_time % 2 == 0:
                return pulse_time, tofs, det_ids
            else:
                return pulse_time, np.zeros(0), det_ids

        self.hist = Histogram1d(
            "topic1", self.num_bins, self.range, preprocessor=_preprocess_step
        )
        self.hist.add_data(3, self.data)

        # As pulse time is odd no data should be added.
        assert sum(self.hist.data) == 0

    def test_throwing_preprocessing_step_is_handled(self):
        def _preprocess(pulse_time, x):
            raise Exception("Preprocessing failed.")

        self.hist = Histogram1d("topic1", self.num_bins, self.range, _preprocess)
        self.hist.add_data(self.pulse_time, self.data)

    def test_only_data_with_correct_source_is_added(self):
        hist = Histogram1d("topic1", self.num_bins, self.range, source="source1")

        hist.add_data(self.pulse_time, self.data, source="source1")
        hist.add_data(self.pulse_time, self.data, source="source1")
        hist.add_data(self.pulse_time, self.data, source="OTHER")

        assert sum(hist.data) == 10

    def test_if_roi_function_supplied_then_outside_data_ignored(self):
        # Ignore outside ROI
        def _create_mask(pulse_time, tofs, det_ids):
            mask = []
            for det in det_ids:
                if det in [3, 4]:
                    mask.append(0)
                else:
                    mask.append(1)
            return mask

        hist = Histogram1d("topic1", self.num_bins, self.range, roi=_create_mask)

        det_ids = np.array([x for x in range(self.num_bins)])

        hist.add_data(self.pulse_time, self.data, det_ids)

        assert sum(hist.data) == 2

    def test_clearing_histogram_data_clears_histogram(self):
        self.hist.add_data(self.pulse_time, self.data)

        self.hist.clear_data()

        assert sum(self.hist.data) == 0

    def test_after_clearing_histogram_can_add_data(self):
        self.hist.add_data(self.pulse_time, self.data)
        self.hist.clear_data()

        self.hist.add_data(self.pulse_time, self.data)

        assert self.hist.shape == (self.num_bins,)
        assert sum(self.hist.data) == 5

    def test_adding_empty_data_does_nothing(self):
        self.hist.add_data(self.pulse_time, [])

        assert sum(self.hist.data) == 0

    def test_histogram_keeps_track_of_last_pulse_time_processed(self):
        self.hist.add_data(1234, self.data)
        self.hist.add_data(1235, self.data)
        self.hist.add_data(1236, self.data)

        assert self.hist.last_pulse_time == 1236
