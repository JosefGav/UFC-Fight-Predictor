# Library imports with explanations:
import requests        # HTTP library - sends requests to websites (like clicking a link)
from bs4 import BeautifulSoup  # HTML parser - reads and navigates HTML code from websites
import pandas as pd    # Data analysis library - creates tables/spreadsheets for our data
import time           # Built-in Python library - lets us add delays between requests
from typing import List, Dict  # Type hints - helps specify what data types functions expect


try:
    # If running as part of a package
    from .event_scraper import get_event_fights
    from . import fetcher
except ImportError:
    # If running directly as a script
    from event_scraper import get_event_fights
    import fetcher

from typing import Union,Optional


class UFCScraper:
    def __init__(self):
        # Constructor - runs when we create a new UFCScraper object
        # Store the main UFC Stats website URL so we can reuse it
        self.base_url = "http://ufcstats.com"
    
    def _get_page(self, url: str) -> BeautifulSoup:
        """Get and parse a webpage"""
        
        html = fetcher.fetch_url(url)
        if not html:
            print(f"Failed to fetch page: {url}")
            return None

        return BeautifulSoup(html, "html.parser")
    
    
    def get_recent_events(self, limit: Union[int,str] = None) -> Optional[List[Dict]]:
        """
        Scrape recent UFC events from the UFC Stats website with flexible limiting.

        Parameters
        ----------
        limit : int or str or None, optional (default=None)
            Controls how many events to scrape or how far back in time to scrape.
            - If int `n`, scrapes up to `n` most recent events (must be > 1).
            - If str (e.g., "up to 2018" or "January 6, 2018"), scrapes all events
            until the given year (exclusive). Year must be >= 1993.
            - If None, scrapes all available events (up to internal page limit).

        Returns
        -------
        List[Dict]
            List of dicts with keys:
            - 'name': event name (str)
            - 'date': event date (str)
            - 'location': event location (str)
            - 'url': event URL (str)
            Returns empty list if no events found or invalid parameter given.
        """
        
        

        # Create empty list to store our event data
        events = []
        page = 1  # start on page 1
        
        limit_is_string = type(limit) is str
        limit_is_int = type(limit) is int
        

    

        if limit_is_int and limit <= 1:
            print("limit must be greater than 1")
            return None
        elif limit_is_string and int(limit.split()[2]) <1993:
            print("limit date must not be older than 1993")
            return None

        # Continue until we have enough events OR hit the limit of pages
        # while len(events) < limit: only if there is a limit
        while True:
            print(f"Scraping page {page}...")
            
            # Build the URL for the completed events page
            if page == 1:
                events_url = f"{self.base_url}/statistics/events/completed"
            else:
                events_url = f"{self.base_url}/statistics/events/completed?page={page}"
            
            # Use our get_page method to fetch and parse the events page
            soup = self._get_page(events_url)
            
            # Check if get_page failed (returned None)
            if not soup:
                print(f"Failed to load page {page} - stopping")
                break
            
            # Track events found on this page BEFORE processing
            events_before = len(events)
            
            # Parse event data from the HTML
            event_rows = soup.find_all('tr', class_='b-statistics__table-row')
            
            # If no event rows found, we've reached the end
            if len(event_rows) <= 1:  # Only header row or no rows
                print(f"No events found on page {page} - reached end of UFC history")
                break
            
            # Loop through each event row (skip the header row)
            for row in event_rows[1:]:  # [1:] skips the first row which is the header
                try:
                    # Find all cells in this row
                    cells = row.find_all('td', class_='b-statistics__table-col')
                    
                    # Make sure we have enough cells
                    if len(cells) >= 2:
                        # Get the event name and URL from the first cell
                        name_date_cell = cells[0]
                        event_link = name_date_cell.find('a')
                        event_date_tag = name_date_cell.find('span')
                        
                        if event_link and event_date_tag:
                            # Extract event information
                            event_name = event_link.text.strip()
                            event_url = event_link.get('href')
                            
                            # Get location from second cell
                            event_location = cells[1].text.strip() 

                            # 
                            event_date = event_date_tag.text.strip()

                            # Stop if we've reached our limit (datewise)
                            if limit is not None and limit_is_string and int(limit.split()[2]) >= int(event_date.split()[2]):
                                print(f"Reached limit of year {limit} events - stopping")
                                return events[1:]
                            
                            # Create a dictionary with all the event info
                            event_data = {
                                'name': event_name,
                                'date': event_date,
                                'location': event_location,
                                'url': event_url
                            }
                            
                            # Add this event to our events list
                            events.append(event_data)
                            
                            # Print progress
                            print(f"Found event #{len(events)}: {event_name} on {event_date}")
                            
                            # Stop if we've reached our limit
                            if limit is not None and type(limit) is int and len(events) >= limit+1:
                                print(f"Reached limit of {limit} events - stopping")
                                return events[1:]
                
                                
                except Exception as e:
                    print(f"Error parsing event row: {e}")
                    continue
            
            # Check if we found any new events on this page
            events_found_this_page = len(events) - events_before
            if events_found_this_page == 0:
                print(f"No new events found on page {page} - reached end")
                break
            
            print(f"Found {events_found_this_page} events on page {page}, total: {len(events)}")
            
            # Move to next page
            page += 1
            
            # Safety check - don't scrape more than 100 pages
            if page > 100:
                print("Reached page limit (100) - stopping for safety")
                break
            
            # Add delay between page requests to be respectful
            time.sleep(1)
        
        # Final summary
        print(f"Found {len(events)} total events across {page-1} pages")
        
        return events[1:]
    
    def get_all_fight_data(self, limit: Union[int,str] = None) -> Optional[List[Dict]]:
        all_fights = []
        
        events = self.get_recent_events(limit)

        if events is None:
            return None
        
        for i, event in enumerate(events):
            event_url = event.get("url")
            event_location = event.get("location")
            event_date = event.get("date")
            print("searching " + event.get("name") + " " +str(i/len(events)*100)+"%")

            fight_card = get_event_fights(event_url,date=event_date,location=event_location)

            all_fights.extend(fight_card) # adds new fights to list
        
        return all_fights


    @staticmethod
    def print_events (events: List[Dict]):
        print("\n" + "="*60)
        print("RECENT UFC EVENTS:")
        print("="*60)
        
        # Pretty print each event
        for i, event in enumerate(events, 1):
            print(f"\nEvent {i}:")
            print(f"  Name: {event['name']}")
            print(f"  Date: {event['date']}")
            print(f"  Location: {event['location']}")
            print(f"  URL: {event['url']}")
# Test the scraper
# This section only runs when you execute this file directly (not when importing it)
if __name__ == "__main__":
    # Create a new instance of our UFCScraper class
    scraper = UFCScraper()
    
    # Define the URL we want to test with
    events_url = "http://ufcstats.com/statistics/events/completed"
    
    # Try to get the events page using our get_page method
    soup = scraper._get_page(events_url)
    
    
    # Check if the page loaded successfully
    if soup:
        # Success! Print a confirmation message
        print("✅ Successfully connected to UFC Stats!")
        
        # Try to get the page title and print it
        # soup.title gets the <title> tag from the HTML
        # The 'if soup.title else' part handles cases where there might be no title tag
        print(f"Page title: {soup.title.text if soup.title else 'No title'}")
    else:
        # Something went wrong - print error message
        print("❌ Failed to connect to UFC Stats")


    # thing = scraper.get_recent_events(". . 1992")
    thing = scraper.get_recent_events(10)


    if thing:
        print("sucessfully viewed recent fights")
        UFCScraper.print_events(thing)
    else:
        print("something went wrong")

