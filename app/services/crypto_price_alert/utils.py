import requests

COIN_API_URL = "https://api.coingecko.com/api/v3/simple/price"


def get_crypto_price(crypto: str, currency: str = "usd"):
    """Fetches the current price of the cryptocurrency."""
    try:
        response = requests.get(
            COIN_API_URL, params={"ids": crypto, "vs_currencies": currency}, timeout=10
        )
        response.raise_for_status()
        return response.json().get(crypto, {}).get(currency)
    except requests.RequestException as e:
        print(f"Error fetching price for {crypto}: {e}")
        return None


def format_crypto_price(price):
    """Formats the cryptocurrency price according to industry standards."""
    if price is None:
        return "N/A"
    if price >= 1:
        return f"{price:,.2f}"  # 2 decimal places for large numbers
    elif price >= 0.01:
        return f"{price:,.4f}"  # 4 decimal places for medium numbers
    elif price >= 0.0001:
        return f"{price:,.6f}"  # 6 decimal places for cheaper assets
    else:
        return f"{price:,.8f}"  # 8 decimal places for micro-prices
