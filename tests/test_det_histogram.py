import pytest
import numpy as np
from histograms.det_histogram import DetHistogram


class TestDetHistogram:
    @pytest.fixture(autouse=True)
    def prepare(self):
        self.NOT_USED = -1
        self.pulse_time = 1234
        self.tof_range = (0, 10)
        self.det_range = (0, 19)
        self.num_dets = 20
        self.width = 5
        self.data = np.array([x for x in range(self.det_range[1] + 1)])
        self.hist = DetHistogram("topic", self.tof_range, self.det_range, self.width)

    def test_if_width_is_not_multiple_of_detector_range_then_throws(self):
        width = 5
        det_range = (0, 23)

        with pytest.raises(Exception):
            DetHistogram("topic", self.tof_range, det_range, width)

    def test_starting_from_non_zero_detector_okay_if_width_is_multiple_of_detector_range(
        self
    ):
        width = 5
        det_range = (2, 21)

        DetHistogram("topic", self.tof_range, det_range, width)

    def test_on_construction_histogram_is_uninitialised(self):
        assert self.hist.x_edges is not None
        assert self.hist.shape == (20,)
        assert len(self.hist.x_edges) == 21
        assert self.hist.x_edges[0] == self.data[0]
        assert self.hist.x_edges[-1] == 19
        assert self.hist.data.sum() == 0

    def test_adding_data_to_initialised_histogram_new_data_is_added(self):
        self.hist.add_data(self.pulse_time, [], self.data)
        first_sum = self.hist.data.sum()

        # Add the data again
        self.hist.add_data(self.pulse_time, [], self.data)

        # Sum should be double
        assert self.hist.data.sum() == first_sum * 2

    def test_adding_data_outside_initial_bins_is_ignored(self):
        self.hist.add_data(self.pulse_time, [], self.data)
        first_sum = self.hist.data.sum()
        x_edges = self.hist.x_edges[:]

        # Add data that is outside the edges
        new_data = np.array([x + self.num_dets + 1 for x in range(self.num_dets)])
        self.hist.add_data(self.pulse_time, [], new_data)

        # Sum should not change
        assert self.hist.data.sum() == first_sum
        # Edges should not change
        assert np.array_equal(self.hist.x_edges, x_edges)

    def test_adding_data_of_specific_shape_is_captured(self):
        data = [12, 12, 13, 13, 13, 14, 14]
        self.hist.add_data(self.pulse_time, [], data)

        assert self.hist.data.sum() == len(data)
        assert self.hist.data[12] == 2
        assert self.hist.data[13] == 3
        assert self.hist.data[14] == 2

    def test_if_no_id_supplied_then_defaults_to_empty_string(self):
        assert self.hist.identifier == ""

    def test_id_supplied_then_is_set(self):
        example_id = "abcdef"
        hist = DetHistogram(
            "topic1", self.tof_range, self.det_range, self.width, identifier=example_id
        )
        assert hist.identifier == example_id

    def test_only_data_with_correct_source_is_added(self):
        hist = DetHistogram(
            "topic", self.tof_range, self.det_range, self.width, source="source1"
        )

        hist.add_data(self.pulse_time, [], self.data, source="source1")
        hist.add_data(self.pulse_time, [], self.data, source="source1")
        hist.add_data(self.pulse_time, [], self.data, source="OTHER")

        assert hist.data.sum() == 38

    def test_clearing_histogram_data_clears_histogram(self):
        self.hist.add_data(self.pulse_time, [], self.data)

        self.hist.clear_data()

        assert self.hist.data.sum() == 0

    def test_after_clearing_histogram_can_add_data(self):
        self.hist.add_data(self.pulse_time, [], self.data)
        self.hist.clear_data()

        self.hist.add_data(self.pulse_time, [], self.data)

        assert self.hist.shape == (self.num_dets,)
        assert self.hist.data.sum() == 19

    def test_adding_empty_data_does_nothing(self):
        self.hist.add_data(self.pulse_time, [], [])

        assert self.hist.data.sum() == 0

    def test_histogram_keeps_track_of_last_pulse_time_processed(self):
        self.hist.add_data(1234, [], self.data)
        self.hist.add_data(1235, [], self.data)
        self.hist.add_data(1236, [], self.data)

        assert self.hist.last_pulse_time == 1236
