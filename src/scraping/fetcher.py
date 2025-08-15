import requests
from typing import Optional

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def fetch_url(url: str) -> Optional[str]:
    """Fetch raw HTML content from any URL."""
    url = url.strip() # trim hidden whitespace that might cause error

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_event_page(event_url: str) -> Optional[str]:
    """Fetch the UFC event page HTML.(only if url valid)"""
    if "event-details" not in event_url:
        print(f"Skipped: Invalid event URL: {event_url}")
        return None
    return fetch_url(event_url) 

def get_fight_page(fight_url: str) -> Optional[str]:
    """Fetch the UFC fight details page HTML. (only if url valid)"""
    if "fight-details" not in fight_url:
        print(f"Skipped: Invalid fight URL: {fight_url}")
        return None
    return fetch_url(fight_url)

def get_fighter_page(fighter_url: str) -> Optional[str]:
    """Fetch the UFC fighter profile page HTML. (only if url valid)"""
    if "fighter-details" not in fighter_url:
        print(f"Skipped: Invalid fighter URL: {fighter_url}")
        return None
    return fetch_url(fighter_url)