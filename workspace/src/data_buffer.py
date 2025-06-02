from collections import deque
import pandas as pd
from sklearn.preprocessing import StandardScaler

class DataBuffer:
    def __init__(self, max_size=1000, feature_extractor = lambda c, p: c):
        self.max_size = max_size
        self.feature_extractor = feature_extractor
        self._buffer = deque(maxlen=max_size)
        self._feature_buffer = deque(maxlen=max_size)

    def add(self, data):
        previous_data = self._buffer[-1] if len(self._buffer) > 0 else None
        if len(self._feature_buffer) > 1:
            previous_data['previous_mid_price'] = self._feature_buffer[-1]['previous_mid_price']
        self._buffer.append(data)
        self._feature_buffer.append(self.feature_extractor(data, previous_data=previous_data))
    
    def get_df(self):
        df = pd.DataFrame(self._feature_buffer)
        return df
    
    def get_normalized_df(self):
        if not self._buffer:
            return []
        scaler = StandardScaler()
        norm_df = self.get_df().copy()
        norm_df[norm_df.columns] = scaler.fit_transform(norm_df[norm_df.columns])
        return norm_df
    
    def __len__(self):
        return len(self._buffer)