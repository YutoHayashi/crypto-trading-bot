from collections import deque

class DataBuffer:
    """
    A service that provides a buffer to store data with a maximum size.
    When the buffer reaches its maximum size, the oldest data is discarded.
    """
    max_size: int
    buffer: deque

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)

    def append(self, data) -> None:
        """
        Appends data to the buffer. If the buffer exceeds its maximum size, the oldest data is removed.
        :param data: The data to be appended to the buffer.
        """
        self.buffer.append(data)

    def __len__(self):
        return len(self.buffer)