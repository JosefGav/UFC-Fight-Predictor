from typing import Optional

from bs4 import BeautifulSoup
try:
    from .get_fight import get_fight_stats
    from . import fetcher
except:
    from get_fight import get_fight_stats
    import fetcher

def get_event_fights(url,*,date:str,location:str) -> Optional[list[dict]]:
    """
    Fetch fight data for a specific UFC event based on date and location.

    Function assumes the date and location is the same as that found on the event url.

    Args:
        url (str): The URL to the event on ufcstats.com
        date (str): The date of the event to filter (format eg: ' August 09, 2025').
        location (str): The location of the event (e.g., 'Las Vegas, Nevada, USA').

    Returns:
        Optional[list[dict]]: A list of fight dictionaries for the matching event,
        or None if given invalid url.
    """
    
    dt = date
    lc = location

    html = fetcher.get_event_page(url)
    if not html:
        print(f"Failed to fetch event page: {url}")
        return None

    event_soup = BeautifulSoup(html, "html.parser")

    # Use the CSS selector to find the tbody element
    tbody = event_soup.select_one(
        "body > section > div > div > table > tbody"
    )


    a_tags = tbody.find_all("a", class_="b-flag b-flag_style_green")
    a_tags_strange = tbody.find_all("a", class_="b-flag b-flag_style_bordered") # a tags of fights that dont have a winner/loser


    fight_urls = []

    for i,tag in enumerate(a_tags):
        fight_urls.append(tag.get("href"))

    for i,tag in enumerate(a_tags_strange):
        if (i%2==0): # every other as each two links in a row are copies of each other
            fight_urls.append(tag.get("href"))

    fights = []

    for i, f_url in enumerate(fight_urls):
        print(str(i+1)+"/"+str(len(fight_urls))+" fights")
        fights.append(get_fight_stats(f_url,location=lc,date=dt))


    print("completed searching event")

    return fights

    

if __name__ == "__main__":
    #get_event_fights("http://www.ufcstats.com/event-details/f2c934689243fe4e", date="August 02, 2025",location="Las Vegas, Nevada, USA")
    fights = get_event_fights("http://ufcstats.com/event-details/de277a4abcfeea46", date="June 14, 2025",location="Atlanta, Georgia, USA")