from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Optional

import requests


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0 Safari/537.36"
)


@dataclass
class URLCheckResult:
    url: str
    status: str
    detail: str


def check_url_status(
    url: str,
    retries: int = 3,
    min_delay: float = 1.2,
    max_delay: float = 2.0,
    timeout: int = 15,
    verify_ssl: bool = True,
    session: Optional[requests.Session] = None,
) -> URLCheckResult:
    """
    Check a URL and return a categorized result.
    """
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    requester = session or requests.Session()

    for attempt in range(retries + 1):
        try:
            response = requester.get(
                url,
                allow_redirects=True,
                timeout=timeout,
                headers=headers,
                stream=True,
                verify=verify_ssl,
            )
            code = response.status_code
            retry_after_header = response.headers.get("Retry-After")
            response.close()

            if code == 200:
                return URLCheckResult(url, "Working", "200 OK")
            if code == 202:
                return URLCheckResult(url, "Accepted", "202 Accepted")
            if code == 404:
                return URLCheckResult(url, "Broken-404", "404 Not Found")
            if code == 429:
                retry_after = int(retry_after_header) if retry_after_header and retry_after_header.isdigit() else 3 ** max(attempt, 1)
                if attempt < retries:
                    time.sleep(retry_after)
                    continue
                return URLCheckResult(url, "Rate Limited", "429 Too Many Requests")
            if 400 <= code < 500:
                return URLCheckResult(url, "Client Error", f"{code} Client Error")
            if 500 <= code < 600:
                return URLCheckResult(url, "Server Error", f"{code} Server Error")

            return URLCheckResult(url, "Other", str(code))

        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(random.uniform(min_delay, max_delay))
                continue
            return URLCheckResult(url, "Broken", "Timeout")

        except requests.exceptions.ConnectionError as e:
            if "10054" in str(e) and attempt < retries:
                time.sleep(random.uniform(min_delay, max_delay))
                continue
            return URLCheckResult(url, "Broken", f"ConnectionError: {e}")

        except requests.exceptions.RequestException as e:
            return URLCheckResult(url, "Broken", f"Exception: {e}")

        finally:
            time.sleep(random.uniform(min_delay, max_delay))

    return URLCheckResult(url, "Broken", "No response after retries")