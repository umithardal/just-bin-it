from deserialisation import deserialise


class EventSource:
    def __init__(self, consumer):
        """
        Constructor.

        :param consumer: The underlying consumer.
        """
        if consumer is None:
            raise Exception("Event source must have a consumer")
        self.consumer = consumer

    def get_data(self):
        """
        Get the latest data from the consumer.

        :return: The list of data.
        """
        data = []
        msgs = self.consumer.get_new_messages()

        # Unwrap the messages from a topic based dict into a list
        for topic, records in msgs.items():
            for i in records:
                data.append(deserialise(i.value))
        return data