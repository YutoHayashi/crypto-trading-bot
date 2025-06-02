## Operation Log

### 2025/06/03 1.2h (\-4678)

#### Model used
| Q-Network |
| --- |
| trained_model_minus_profit_1.pth |

#### Issues
- Error in log output.
- The data to be input into QNet now is normalized, including future data, so it will not work in a real environment. Methods of normalization/standardization need to be considered.
- One transaction amount is too much 0.01 -> 0.001 is appropriate? (It seems difficult to determine the transaction amount in a reinforcement learning model, so I thought fixed with a small transaction amount would be better)
- Orders in one side may be duplicated.
- Since there is no interval between the order and execution, and the basic order cancellation cannot be completed in time, can we eliminate it from the possible actions the agent can take?
- Sometimes the bot gets stuck with a position.
- 