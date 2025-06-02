def extract_features(data, previous_data=None, top_n=5):
    """
    Extract features from the given data.
    :param data: The current data (dict) containing 'mid_price', 'bids', and 'asks'.
    :param previous_data: The previous data (dict) for calculating changes (optional).
    :param top_n: The number of top levels to consider for weighted averages and depth imbalance.
    :return: A dictionary of extracted features.
    """
    features = {}

    # Extract current data
    mid_price = data.get("mid_price")
    bids = data.get("bids", [])
    asks = data.get("asks", [])

    # Best Bid and Ask
    best_bid = bids[0]["price"] if bids else None
    best_ask = asks[0]["price"] if asks else None
    features["best_bid"] = best_bid
    features["best_ask"] = best_ask

    # Spread and Mid Price
    if best_bid is not None and best_ask is not None:
        spread = best_ask - best_bid
    else:
        spread = None
    features["spread"] = spread
    features["mid_price"] = mid_price

    # Best Bid Volume and Best Ask Volume
    best_bid_volume = bids[0]["size"] if bids else None
    best_ask_volume = asks[0]["size"] if asks else None
    features["best_bid_volume"] = best_bid_volume
    features["best_ask_volume"] = best_ask_volume

    # Spread Weighted Volume Ratio
    if best_bid_volume and best_ask_volume:
        features["spread_weighted_volume_ratio"] = best_bid_volume / best_ask_volume
    else:
        features["spread_weighted_volume_ratio"] = None

    # Total Bid and Ask Volumes (Top N Levels)
    total_bid_volume = sum(bid["size"] for bid in bids[:top_n])
    total_ask_volume = sum(ask["size"] for ask in asks[:top_n])
    features["total_bid_volume"] = total_bid_volume
    features["total_ask_volume"] = total_ask_volume

    # Order Imbalance
    features["order_imbalance"] = total_bid_volume - total_ask_volume

    # Changes in Best Bid/Ask Prices and Volumes
    if previous_data:
        previous_mid_price = previous_data.get("mid_price")
        previous_bids = previous_data.get("bids", [])
        previous_asks = previous_data.get("asks", [])

        features["previous_mid_price"] = previous_mid_price

        previous_best_bid = previous_bids[0]["price"] if previous_bids else None
        previous_best_ask = previous_asks[0]["price"] if previous_asks else None
        previous_best_bid_volume = previous_bids[0]["size"] if previous_bids else None
        previous_best_ask_volume = previous_asks[0]["size"] if previous_asks else None

        # Best Bid/Ask Changes
        features["best_bid_change"] = best_bid - previous_best_bid if best_bid and previous_best_bid else None
        features["best_ask_change"] = best_ask - previous_best_ask if best_ask and previous_best_ask else None

        # Best Bid/Ask Volume Changes
        features["best_bid_volume_change"] = best_bid_volume - previous_best_bid_volume if best_bid_volume and previous_best_bid_volume else None
        features["best_ask_volume_change"] = best_ask_volume - previous_best_ask_volume if best_ask_volume and previous_best_ask_volume else None

        # Best Bid/Ask Volume Difference Change
        if best_bid_volume and best_ask_volume and previous_best_bid_volume and previous_best_ask_volume:
            features["best_bid_ask_volume_diff_change"] = (best_bid_volume - best_ask_volume) - (previous_best_bid_volume - previous_best_ask_volume)
        else:
            features["best_bid_ask_volume_diff_change"] = None

        # Order Imbalance Change
        previous_order_imbalance = sum(bid["size"] for bid in previous_bids[:top_n]) - sum(ask["size"] for ask in previous_asks[:top_n])
        features["order_imbalance_change"] = (total_bid_volume - total_ask_volume) - previous_order_imbalance

        # Mid Price Acceleration
        if mid_price and previous_mid_price and previous_data.get("previous_mid_price", None):
            features["mid_price_acceleration"] = mid_price - 2 * previous_mid_price + previous_data.get("previous_mid_price", None)
        else:
            features["mid_price_acceleration"] = None

        # Total Volume Acceleration
        previous_total_bid_volume = sum(bid["size"] for bid in previous_bids[:top_n])
        previous_total_ask_volume = sum(ask["size"] for ask in previous_asks[:top_n])
        if total_bid_volume and total_ask_volume and previous_total_bid_volume and previous_total_ask_volume:
            features["total_volume_acceleration"] = (total_bid_volume + total_ask_volume) - 2 * (previous_total_bid_volume + previous_total_ask_volume)
        else:
            features["total_volume_acceleration"] = None

        # Bid/Ask Ratio Change
        previous_bid_ask_ratio = previous_total_bid_volume / previous_total_ask_volume if previous_total_ask_volume != 0 else None
        current_bid_ask_ratio = total_bid_volume / total_ask_volume if total_ask_volume != 0 else None
        if previous_bid_ask_ratio and current_bid_ask_ratio:
            features["bid_ask_ratio_change"] = current_bid_ask_ratio - previous_bid_ask_ratio
        else:
            features["bid_ask_ratio_change"] = None

        # Spread-to-Mid Ratio Change
        previous_spread_to_mid_ratio = (previous_best_ask - previous_best_bid) / previous_mid_price if previous_best_bid and previous_best_ask and previous_mid_price else None
        current_spread_to_mid_ratio = spread / mid_price if spread and mid_price else None
        if previous_spread_to_mid_ratio and current_spread_to_mid_ratio:
            features["spread_to_mid_ratio_change"] = current_spread_to_mid_ratio - previous_spread_to_mid_ratio
        else:
            features["spread_to_mid_ratio_change"] = None

    else:
        features["best_bid_change"] = None
        features["best_ask_change"] = None
        features["best_bid_volume_change"] = None
        features["best_ask_volume_change"] = None
        features["best_bid_ask_volume_diff_change"] = None
        features["order_imbalance_change"] = None
        features["mid_price_acceleration"] = None
        features["total_volume_acceleration"] = None
        features["bid_ask_ratio_change"] = None
        features["spread_to_mid_ratio_change"] = None

    # Weighted Average Prices for Top N Levels
    def weighted_average(prices):
        total_volume = sum(item["size"] for item in prices[:top_n])
        if total_volume == 0:
            return None
        return sum(item["price"] * item["size"] for item in prices[:top_n]) / total_volume

    features["weighted_avg_bid"] = weighted_average(bids)
    features["weighted_avg_ask"] = weighted_average(asks)

    # Depth Imbalance Index
    bid_weighted_sum = sum((i + 1) * bid["size"] for i, bid in enumerate(bids[:top_n]))
    ask_weighted_sum = sum((i + 1) * ask["size"] for i, ask in enumerate(asks[:top_n]))
    features["depth_imbalance_index"] = (bid_weighted_sum - ask_weighted_sum) / (bid_weighted_sum + ask_weighted_sum) if (bid_weighted_sum + ask_weighted_sum) != 0 else None

    # Center of Mass for Top N Levels
    def center_of_mass(prices):
        total_volume = sum(item["size"] for item in prices[:top_n])
        if total_volume == 0:
            return None
        return sum((i + 1) * item["size"] for i, item in enumerate(prices[:top_n])) / total_volume

    features["bid_center_of_mass"] = center_of_mass(bids)
    features["ask_center_of_mass"] = center_of_mass(asks)

    return features