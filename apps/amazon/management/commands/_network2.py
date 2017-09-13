"""Provide a tor-enabled asyncio network client."""


import asyncio
import aiohttp
import aiosocks
import time
from aiosocks.connector import ProxyConnector, ProxyClientRequest


USER_AGENT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36'
}


throttle = asyncio.Semaphore(5)


class AnonymousClient:
    _last_sanity_check = 0
    last_ip_address = ""
    _updating_ip = False

    def __init__(self):
        self._session = aiohttp.ClientSession(
            connector=ProxyConnector(remote_resolve=True),
            request_class=ProxyClientRequest,
            headers=USER_AGENT_HEADERS)

    async def get(self, url, params=None):
        async with throttle:
            await self._sanity_check()
            try:
                async with self._session.get(
                    url, proxy='socks5://127.0.0.1:9050', params=params
                ) as resp:
                    return await resp.text()
            except aiohttp.ClientConnectionError as e:
                print("Client Connection Error", e)  # connection problem
            except aiosocks.SocksError:
                print("Socks Error")  # communication problem
            return None

    async def _sanity_check(self):
        """ Update the IP address we're using as a proxy for reference. """
        if time.time() - self._last_sanity_check < 10 or self._updating_ip:
            return  # We've done this too recently

        self._last_sanity_check = time.time()
        self._updating_ip = True
        # noinspection PyBroadException
        try:
            async with self._session.get(
                'https://icanhazip.com', proxy='socks5://127.0.0.1:9050'
            ) as resp:
                response = await resp.text()
            self.last_ip_address = response.strip()
        except Exception:
            pass
        self._updating_ip = False

    def cleanup(self):
        self._session.close()


if __name__ == '__main__':
    client = AnonymousClient()
    loop = asyncio.get_event_loop()
    all5 = asyncio.gather(
        client.get("https://icanhazip.com"),
        client.get("https://icanhazip.com"),
        client.get("https://icanhazip.com"),
        client.get("https://icanhazip.com"),
        client.get("https://icanhazip.com"),
    )
    responses = loop.run_until_complete(all5)
    print(responses)
    loop.close()
    client.cleanup()
