# Library imports with explanations:
import requests        # HTTP library - sends requests to websites (like clicking a link)
from bs4 import BeautifulSoup  # HTML parser - reads and navigates HTML code from websites
import pandas as pd    # Data analysis library - creates tables/spreadsheets for our data
import time           # Built-in Python library - lets us add delays between requests
from typing import List, Dict  # Type hints - helps specify what data types functions expect

class UFCScraper:
    def __init__(self):
        # Constructor - runs when we create a new UFCScraper object
        # Store the main UFC Stats website URL so we can reuse it
        self.base_url = "http://ufcstats.com"
        
        # Headers make our scraper look like a real browser visiting the site
        # Without this, some websites might block our requests
        # This specific User-Agent string pretends we're using Chrome on Windows
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Get and parse a webpage"""
        try:
            # requests.get() is like typing a URL in your browser and hitting enter
            # We pass our headers to make it look like a real browser visit
            response = requests.get(url, headers=self.headers)
            
            # raise_for_status() checks if the request worked (status code 200 = success)
            # If there was an error (404, 500, etc.), it raises an exception
            response.raise_for_status()
            
            # BeautifulSoup takes the HTML content and makes it easy to search through
            # 'html.parser' tells it how to interpret the HTML code
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            # If anything goes wrong (no internet, website down, etc.), print error
            # RequestException catches all possible request-related errors
            print(f"Error fetching {url}: {e}")
            return None  # Return None so other functions know something went wrong
    
    
    def get_recent_events(self, limit: int = None) -> List[Dict]:
        """Scrape recent UFC events - FIXED VERSION"""
        
        # Create empty list to store our event data
        events = []
        page = 1  # start on page 1
        
        # Continue until we have enough events OR hit the limit of pages
        # while len(events) < limit: only if there is a limit
        while True:
            if limit is not None and len(events) >= limit:
                break
            print(f"Scraping page {page}...")
            
            # Build the URL for the completed events page
            if page == 1:
                events_url = f"{self.base_url}/statistics/events/completed"
            else:
                events_url = f"{self.base_url}/statistics/events/completed?page={page}"
            
            # Use our get_page method to fetch and parse the events page
            soup = self.get_page(events_url)
            
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
                            if limit is not None and len(events) >= limit:
                                print(f"Reached limit of {limit} events - stopping")
                                break
                                
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
        
        # Return only the number of events requested
        return events[:limit]
    
    def get_fight_details(self, fight_url: str) -> Dict:
        """Scrape individual fight details"""
        # Use our get_page method to fetch and parse a specific fight page
        soup = self.get_page(fight_url)
        
        # Check if the page loaded successfully
        if not soup:
            return {}  # Return empty dictionary if page failed to load
        
        # Create empty dictionary to store all the fight information
        # This will hold things like fighter names, stats, winner, method of victory, etc.
        fight_data = {}
        
        # TODO: Parse fight statistics
        # This is where you'll extract fighter stats, winner, etc.
        # You'll search through the soup to find specific HTML elements
        # containing the fight data you need
        
        return fight_data  # Return the dictionary with all fight info
    
    def scrape_recent_fights(self, num_events: int = 3):
        """Main method to scrape recent fight data"""
        # Print status message so user knows what's happening
        print(f"Starting to scrape {num_events} recent events...")
        
        # Get the list of recent events using our get_recent_events method
        events = self.get_recent_events(num_events)
        
        # Create empty list to store all fights from all events
        # This will be our final dataset
        all_fights = []
        
        # Loop through each event we found
        # 'for event in events' means "do this for each event in our list"
        for event in events:
            # Add a 1-second delay between requests to be respectful to the website
            # Without delays, we might get blocked for making requests too quickly
            time.sleep(1)
            
            # Print which event we're currently processing
            # .get('name', 'Unknown') safely gets the 'name' key from the event dictionary
            # If 'name' doesn't exist, it returns 'Unknown' instead of crashing
            print(f"Processing event: {event.get('name', 'Unknown')}")
            
            # TODO: Get fights for this event
            # You'll need to visit the event page and find all the fight links
            
            # TODO: Process each fight
            # For each fight link, call get_fight_details() and add to all_fights list
        
        # Return the complete list of all fights from all events
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
    soup = scraper.get_page(events_url)
    
    
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


    thing = scraper.get_recent_events(50)

    if thing:
        print("sucessfully viewed recent fights")
        UFCScraper.print_events(thing)
    else:
        print("something went wrong")

