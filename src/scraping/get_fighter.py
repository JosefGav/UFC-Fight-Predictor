from . import fetcher
from bs4 import BeautifulSoup
from typing import Optional, Dict,Any
from datetime import datetime
import re





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

    fighter_info = {} 

    # Find the container div for record and name
    container = soup.find_all("div", class_="l-page__container")[1]
    
    # Inside it, find the h2 tag with class b-content__title
    title_h2 = container.find("h2", class_="b-content__title")
    if not title_h2:
        print("Title container not found")
        return None

    # Extract the name and record from spans
    name = title_h2.find("span", class_="b-content__title-highlight").get_text(strip=True)
    record = title_h2.find("span", class_="b-content__title-record").text.split()[1].strip()

    fighter_info["name"] = name
    fighter_info["record"] = record

    # print("Name:", name)
    # print("Record:", record)

    stats_div = container.find("div", class_="b-fight-details b-fight-details_margin-top")
    if not stats_div:
        print("Stats container not found")
        return None
    
    info_box = stats_div.find("div", class_="b-list__info-box")
    if not info_box:
        print("Info box not found")
        return None

    stats_list = info_box.find("ul", class_="b-list__box-list")
    if not stats_list:
        print("Stats list not found")
        return None

    basic_stats = stats_list.find_all("li", class_="b-list__box-list-item")

    for li in basic_stats:
        label = li.find("i", class_="b-list__box-item-title")
        if label:
            key = label.get_text(strip=True).rstrip(':').lower()  # e.g. "Height", "Weight"
            # Remove label text from li text to get the value
            value = li.get_text(strip=True).replace(label.get_text(strip=True), '').strip()
            if value and "-" not in value:
                fighter_info[key] = value
            else:
                fighter_info[key] = None


    # Parse the original string into a datetime object
    dob_str = fighter_info.get("dob")
    if dob_str is not None:
        fighter_info["dob"] = datetime.strptime(dob_str, '%b %d, %Y').strftime('%d/%m/%Y')
    else:
        fighter_info["dob"] = None

    weight = fighter_info.get("weight")
    if weight is not None:
        fighter_info["weight"] = int(weight.split()[0])
    else:
        fighter_info["weight"] = None


    reach = fighter_info.get("reach")
    if reach is not None:
        fighter_info["reach"] = int(reach.strip("\""))
    else:
        fighter_info["reach"] = None


    height = fighter_info.get("height")
    if height is not None:
        match = re.match(r"(\d+)'\s*(\d+)\"", fighter_info.get("height")) 
        feet = int(match.group(1))
        inches = int(match.group(2))

        fighter_info["height"]  = feet * 12 + inches
    else:
        fighter_info["height"]  = None

    # print(fighter_info)

    return fighter_info


if __name__ == "__main__":
    get_fighter_basic_stats("http://ufcstats.com/fighter-details/a6c2f5381d575920")

