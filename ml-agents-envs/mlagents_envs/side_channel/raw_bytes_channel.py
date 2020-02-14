from mlagents_envs.side_channel.side_channel import SideChannel, ReservedChannelId
from typing import List


class RawBytesChannel(SideChannel):
    """
    This is an example of what the SideChannel for raw bytes exchange would
    look like. Is meant to be used for general research purpose.
    """

    def __init__(self, channel_id):
        self._received_messages = []
        ReservedChannelId.assert_is_raw_bytes_channel(channel_id)
        super().__init__(channel_id)

    def on_message_received(self, data: bytes) -> None:
        """
        Is called by the environment to the side channel. Can be called
        multiple times per step if multiple messages are meant for that
        SideChannel.
        """
        self._received_messages.append(data)

    def get_and_clear_received_messages(self) -> List[bytearray]:
        """
        returns a list of bytearray received from the environment.
        """
        result = list(self._received_messages)
        self._received_messages = []
        return result

    def send_raw_data(self, data: bytearray) -> None:
        """
        Queues a message to be sent by the environment at the next call to
        step.
        """
        super().queue_message_to_send(data)
