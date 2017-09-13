"""
Steps:

1. Get Amazon Categories
2. Get Amazon Products in Categories
3. Get Amazon Fees: https://amzscout.net/api/v1/landing/fees?asin=B0002JT0XW&domain=COM
4. Get estimated sales volume
5. Precalculate aggregate statistics

Ideally this happens in a way where it can be resumed if canceled
"""
