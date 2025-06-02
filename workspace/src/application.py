from logging import getLogger
import numpy as np
from data_buffer import DataBuffer
from agent import Agent, Actions
from q_net import QNet
from extract_features import extract_features
from bitflyer_client import BitflyerClient

class Application:
    symbol = "FX_BTC_JPY"
    order_quantity = 0.01
    window_size = 1000
    observation_size = 30
    action_size = len(Actions)

    buy_order_id = None
    sell_order_id = None
    buy_order = None # price
    sell_order = None # price
    buy_position = 0.0 # 0.0 or order_quantity
    sell_position = 0.0 # 0.0 or order_quantity

    data_buffer = None
    agent = None
    exchange_client = None

    transaction_logger = None
    action_logger = None

    def __init__(self):
        self.data_buffer = DataBuffer(
            max_size=self.window_size,
            feature_extractor=extract_features
        )
        self.agent = Agent(
            qnet=QNet,
            model_path='src/trained_model.pth',
            observation_size=self.observation_size,
            action_size=self.action_size
        )
        self.exchange_client = BitflyerClient()

        self.transaction_logger = getLogger("Transaction")
        self.action_logger = getLogger("Action")

    def call(self, data, channel):
        if channel == f"lightning_board_snapshot_{self.symbol}":
            self.data_buffer.add(data)

            if (len(self.data_buffer) == self.window_size):
                df = self.data_buffer.get_df()
                best_bid = df['best_bid'].iloc[-1]
                best_ask = df['best_ask'].iloc[-1]

                # Get the normalized DataFrame from the data buffer
                norm_df = self.data_buffer.get_normalized_df()

                # Ensure the current state has the correct shape
                current_features = norm_df.iloc[-1].values.astype(np.float32)

                # Calculate additional parameters (not normalized)
                buy_order_divergence = (
                    1 / abs(best_bid - self.buy_order)
                    if self.buy_order and best_bid != self.buy_order
                    else 0
                )
                sell_order_divergence = (
                    1 / abs(best_ask - self.sell_order)
                    if self.sell_order and best_ask != self.sell_order
                    else 0
                )

                current_state = np.concatenate(
                    [
                        current_features,
                        [
                            self.buy_position,
                            self.sell_position,
                            buy_order_divergence,
                            sell_order_divergence,
                        ],
                    ]
                ).astype(np.float32)
                
                # Get the action from the agent based on the current state
                action = self.agent.get_action(current_state)
                
                # Map the action to the corresponding enum value
                match action:
                    case Actions.DO_NOTHING.value:
                        pass
                    
                    case Actions.BUY_AT_BEST_ASK.value:
                        if self.buy_position == 0.0:
                            # Implement buy at best ask logic
                            if self.buy_order is not None and self.buy_order_id is not None:
                                self.exchange_client.cancel_order(order_id=self.buy_order_id, symbol=self.symbol)
                            
                            self.exchange_client.create_order(
                                symbol=self.symbol,
                                side="buy",
                                size=self.order_quantity,
                                price=best_ask,
                                order_type="limit"
                            )

                    case Actions.SELL_AT_BEST_BID.value:
                        if self.sell_position == 0.0:
                            # Implement sell at best bid logic
                            if self.sell_order is not None and self.sell_order_id is not None:
                                self.exchange_client.cancel_order(order_id=self.sell_order_id, symbol=self.symbol)
                            
                            self.exchange_client.create_order(
                                symbol=self.symbol,
                                side="sell",
                                size=self.order_quantity,
                                price=best_bid,
                                order_type="limit"
                            )
                    
                    case Actions.BUY_AT_BEST_BID.value:
                        if self.buy_position == 0.0:
                            # Implement buy at best bid logic
                            if self.buy_order is not None and self.buy_order_id is not None:
                                self.exchange_client.cancel_order(order_id=self.buy_order_id, symbol=self.symbol)
                            
                            self.exchange_client.create_order(
                                symbol=self.symbol,
                                side="buy",
                                size=self.order_quantity,
                                order_type="market"
                            )
                    
                    case Actions.SELL_AT_BEST_ASK.value:
                        if self.sell_position == 0.0:
                            # Implement sell at best ask logic
                            if self.sell_order is not None and self.sell_order_id is not None:
                                self.exchange_client.cancel_order(order_id=self.sell_order_id, symbol=self.symbol)
                            
                            self.exchange_client.create_order(
                                symbol=self.symbol,
                                side="sell",
                                size=self.order_quantity,
                                order_type="market"
                            )
                    
                    case Actions.CANCEL_BUY_ORDER.value:
                        if self.buy_order is not None and self.buy_order_id is not None:
                            # Implement cancel buy order logic
                            self.exchange_client.cancel_order(order_id=self.buy_order_id, symbol=self.symbol)
                    
                    case Actions.CANCEL_SELL_ORDER.value:
                        if self.sell_order is not None and self.sell_order_id is not None:
                            # Implement cancel sell order logic
                            self.exchange_client.cancel_order(order_id=self.sell_order_id, symbol=self.symbol)
                
                self.action_logger.info("Action taken: %s, Buy Position: %s, Sell Position: %s, Buy Order: %s, Buy Order Id: %s, Sell Order: %s, Sell Order Id", action, self.buy_position, self.sell_position, self.buy_order, self.buy_order_id, self.sell_order, self.sell_order_id)
            
            else:
                self.action_logger.info("Data buffer not full yet, current length: %s", len(self.data_buffer))
        
        elif channel == f"child_order_events":
            if 'event_type' in data and data['event_type'] == 'ORDER':
                order_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
                price = data['price'] if 'price' in data else None
                side = data['side'] if 'side' in data else None
                
                if side == 'BUY':
                    self.buy_order = price
                    self.buy_order_id = order_id
                elif side == 'SELL':
                    self.sell_order = price
                    self.sell_order_id = order_id
                
                if side == 'BUY' and self.buy_position != 0.0:
                    # If there is an existing buy position, cancel the order
                    self.exchange_client.cancel_order(order_id=order_id, symbol=self.symbol)
                elif side == 'SELL' and self.sell_position != 0.0:
                    # If there is an existing sell position, cancel the order
                    self.exchange_client.cancel_order(order_id=order_id, symbol=self.symbol)
                
                self.transaction_logger.info("Order event received, order id: %s, price: %s, side: %s", order_id, price, side)
            
            # If the order execution
            elif 'event_type' in data and data['event_type'] == 'EXECUTION':
                order_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
                
                if order_id == self.buy_order_id:
                    self.buy_order_id = None
                    self.buy_order = None
                    if self.sell_position == 0.0:
                        self.buy_position = self.order_quantity
                    else:
                        self.sell_position = 0.0
                elif order_id == self.sell_order_id:
                    self.sell_order_id = None
                    self.sell_order = None
                    if self.buy_position == 0.0:
                        self.sell_position = self.order_quantity
                    else:
                        self.buy_position = 0.0
                
                self.transaction_logger.info("Order execution event received, order id: %s", order_id)
            
            elif 'evnet_type' in data and data['event_type'] == 'CANCEL':
                order_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
                
                if order_id == self.buy_order_id:
                    self.buy_order_id = None
                    self.buy_order = None
                elif order_id == self.sell_order_id:
                    self.sell_order_id = None
                    self.sell_order = None
                
                self.transaction_logger.info("Order cancel event received, order id: %s", order_id)
            
            elif 'event_type' in data and data['event_type'] == 'ORDER_FAILED':
                self.transaction_logger.error("Order failed event received, order id: %s", data.get('child_order_acceptance_id', 'Unknown'))

            elif 'event_type' in data and data['event_type'] == 'CANCEL_FAILED':
                self.transaction_logger.error("Order cancel failed event received, order id: %s", data.get('child_order_acceptance_id', 'Unknown'))