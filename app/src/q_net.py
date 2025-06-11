import torch.nn as nn
import torch.nn.functional as F

class QNet(nn.Module):
    def __init__(self, input_size: int, output_size: int, dropout_rate: float = 0.5):
        super().__init__()
        self.l1 = nn.Linear(input_size, 256)
        self.l2 = nn.Linear(256, 512)
        self.l3 = nn.Linear(512, 256)
        self.l4 = nn.Linear(256, output_size)
        self.dropout = nn.Dropout(p=dropout_rate)
    
    def forward(self, x):
        x = F.relu(self.l1(x))
        x = self.dropout(x)
        x = F.relu(self.l2(x))
        x = self.dropout(x)
        x = F.relu(self.l3(x))
        x = self.l4(x)
        return x