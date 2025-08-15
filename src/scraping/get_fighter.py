import fetcher
from bs4 import BeautifulSoup
from typing import Optional, Dict,Any

def get_fighter_basic_stats(fighter_url:str) -> Optional[Dict[str,Any]]:
    """
    Fetches and parses basic fighter stats from the fighter profile page.

    Includes stats such as name, height, weight, reach, stance, date of birth, and 
    record at the time of accessing.

    Args:
        fighter_url (str): URL of the fighter profile page.
    Returns:
        dict: Basic fighter stats like name, nickname, height, weight, etc.
        None if the page couldn't be fetched or parsed.
    """
    
    html = fetcher.get_fighter_page(fighter_url)
    if not html:
        print(f"Failed to fetch fighter page: {fighter_url}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # print(soup is not None)

    fighter = {}

    # Find the container div for record and name
    container = soup.find("div", class_="l-page__container")
    
    # Inside it, find the h2 tag with class b-content__title
    title_h2 = container.find("h2", class_="b-content__title")

    # Extract the name and record from spans
    name = title_h2.find("span", class_="b-content__title-highlight").get_text(strip=True)
    record = title_h2.find("span", class_="b-content__title-record").get_text(strip=True)

    print("Name:", name)
    print("Record:", record)

get_fighter_basic_stats("http://ufcstats.com/fighter-details/4461d7e47375a895")
