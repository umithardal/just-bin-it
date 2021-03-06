from unittest.mock import patch

import pytest

from just_bin_it.endpoints.sources import HistogramSource
from tests.doubles.consumer import StubConsumer

TEST_MESSAGE = b"this is a byte message"
INVALID_FB = b"this is an invalid fb message"


class TestHistogramSource:
    @pytest.fixture(autouse=True)
    def prepare(self):
        pass

    def test_if_no_consumer_supplied_then_raises(self):
        with pytest.raises(Exception):
            HistogramSource(None)

    def test_if_no_new_messages_then_no_data(self):
        mock_consumer = StubConsumer(["broker1"], ["topic1"])
        mock_consumer.add_messages([])
        hs = HistogramSource(mock_consumer)
        data = hs.get_new_data()
        assert len(data) == 0

    @patch("just_bin_it.endpoints.sources.deserialise_hs00", return_value=TEST_MESSAGE)
    def test_if_five_new_messages_on_one_topic_then_data_has_five_items(
        self, mock_method
    ):
        mock_consumer = StubConsumer(["broker1"], ["topic1"])
        mock_consumer.add_messages([TEST_MESSAGE] * 5)
        hs = HistogramSource(mock_consumer)

        data = hs.get_new_data()
        _, _, message = data[0]

        assert len(data) == 5
        assert message == TEST_MESSAGE

    def test_deserialising_invalid_fb_does_not_throw(self):
        mock_consumer = StubConsumer(["broker1"], ["topic1"])
        mock_consumer.add_messages([INVALID_FB])
        hs = HistogramSource(mock_consumer)

        hs.get_new_data()
