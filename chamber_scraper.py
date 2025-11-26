#!/usr/bin/env python3
"""
Chamber of Commerce Business Scraper - Unified Version
Scrapes business listings from CT shoreline chamber directories

Usage:
  python3 chamber_scraper.py                    # Use default chambers
  python3 chamber_scraper.py [name] [url] ...   # Use custom chambers
  python3 chamber_scraper.py --help             # Show help
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
from datetime import datetime
import os
import sys

class ChamberScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.businesses = []
        
    def scrape_chamber_list(self, base_url, chamber_name):
        """
        Scrape the main category list page
        """
        print(f"\n{'='*60}")
        print(f"Scraping: {chamber_name}")
        print(f"{'='*60}")
        
        try:
            response = self.session.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all category links
            category_links = soup.find_all('a', href=re.compile(r'/list/ql/'))
            
            print(f"Found {len(category_links)} categories")
            
            for link in category_links:
                category_name = link.text.strip()
                category_url = urljoin(base_url, link['href'])
                
                print(f"\n  Category: {category_name}")
                self.scrape_category(category_url, chamber_name, category_name)
                
                # Be polite - don't hammer the server
                time.sleep(1)
                
        except Exception as e:
            print(f"Error scraping {chamber_name}: {e}")
    
    def scrape_category(self, category_url, chamber_name, category_name):
        """
        Scrape all businesses in a category
        """
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all business links
            business_links = soup.find_all('a', href=re.compile(r'/list/member/'))
            
            print(f"    Found {len(business_links)} businesses")
            
            for link in business_links:
                business_url = urljoin(category_url, link['href'])
                self.scrape_business(business_url, chamber_name, category_name)
                time.sleep(0.5)  # Be polite
                
        except Exception as e:
            print(f"    Error scraping category {category_name}: {e}")
    
    def scrape_business(self, business_url, chamber_name, category_name):
        """
        Scrape individual business details
        """
        try:
            response = self.session.get(business_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract business name (usually in h1 or title)
            business_name = soup.find('h1')
            if business_name:
                business_name = business_name.text.strip()
            else:
                business_name = soup.title.text.strip() if soup.title else "Unknown"
            
            # Extract description
            about_section = soup.find(string=re.compile(r'About Us', re.IGNORECASE))
            description = ""
            if about_section:
                parent = about_section.find_parent()
                if parent:
                    description = parent.get_text(strip=True)
            
            # Extract contact info
            phone = self.extract_phone(soup)
            address = self.extract_address(soup)
            email = self.extract_email(soup)
            
            # Look for website link
            website = self.extract_website(soup)
            
            business_data = {
                'business_name': business_name,
                'chamber': chamber_name,
                'category': category_name,
                'phone': phone,
                'address': address,
                'email': email,
                'website': website,
                'has_website': 'Yes' if website else 'No',
                'description': description[:200] if description else "",  # Limit description length
                'chamber_url': business_url,
                'scraped_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.businesses.append(business_data)
            
            status = "❌ NO WEBSITE" if not website else "✅ Has website"
            print(f"      {business_name}: {status}")
            
        except Exception as e:
            print(f"      Error scraping business: {e}")
    
    def extract_phone(self, soup):
        """Extract phone number from page"""
        # Look for phone patterns
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        text = soup.get_text()
        match = re.search(phone_pattern, text)
        return match.group(0) if match else ""
    
    def extract_address(self, soup):
        """Extract address from page"""
        # Look for address patterns (simplified)
        address_text = ""
        # Try to find address in common patterns
        for text in soup.stripped_strings:
            if re.search(r'\d+\s+\w+.*,\s*CT\s*\d{5}', text):
                address_text = text
                break
        return address_text
    
    def extract_email(self, soup):
        """Extract email from page"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        text = soup.get_text()
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def extract_website(self, soup):
        """Extract website URL from page"""
        # Look for links that might be websites (not social media)
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Skip internal links, social media, and email
            if any(x in href.lower() for x in ['facebook.com', 'twitter.com', 'instagram.com', 
                                                 'linkedin.com', 'mailto:', 'tel:', 
                                                 'business.', 'chambermaster.blob']):
                continue
            # Look for external http/https links
            if href.startswith('http') and not any(x in href for x in ['goschamber.com', 'clintonchamber.org', 'easternchamberct.org', 'mysticchamber.org', 'crvchamber.org']):
                return href
        return ""
    
    def save_to_csv(self, filename='chamber_businesses.csv'):
        """Save scraped data to CSV"""
        if not self.businesses:
            print("No businesses to save!")
            return
        
        fieldnames = ['business_name', 'chamber', 'category', 'phone', 'address', 
                     'email', 'website', 'has_website', 'description', 
                     'chamber_url', 'scraped_date']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.businesses)
        
        print(f"\n{'='*60}")
        print(f"Saved {len(self.businesses)} businesses to {filename}")
        
        # Print summary
        no_website = sum(1 for b in self.businesses if not b['website'])
        print(f"Businesses WITHOUT websites: {no_website}")
        print(f"Businesses WITH websites: {len(self.businesses) - no_website}")
        print(f"{'='*60}")


def get_default_chambers():
    """Return the default list of chambers to scrape"""
    return [
        {
            'name': 'Old Saybrook Chamber',
            'url': 'https://business.goschamber.com/list'
        },
        {
            'name': 'Eastern CT Chamber of Commerce',
            'url': 'https://business.easternchamberct.org/list'
        },
        {
            'name': 'Mystic Chamber',
            'url': 'https://business.mysticchamber.org/list'
        },
        {
            'name': 'CT River Valley Chamber',
            'url': 'https://business.crvchamber.org/list'
        }
    ]


def print_usage():
    """Print usage instructions"""
    print("""
Chamber of Commerce Scraper - Unified Version

USAGE:
  # Use default chambers (Old Saybrook, Eastern CT, Mystic, CT River Valley):
  python3 chamber_scraper.py

  # Use custom chambers:
  python3 chamber_scraper.py [chamber_name] [chamber_url] [chamber_name2] [chamber_url2] ...

  # Specify output file:
  python3 chamber_scraper.py --output my_results.csv

  # Combine options:
  python3 chamber_scraper.py --output results.csv "Madison Chamber" "https://business.madisonchamber.com/list"

EXAMPLES:
  # Use defaults:
  python3 chamber_scraper.py

  # Scrape one custom chamber:
  python3 chamber_scraper.py "Clinton Chamber" "https://business.clintonchamber.org/list"

  # Scrape multiple custom chambers:
  python3 chamber_scraper.py "Clinton" "https://business.clintonchamber.org/list" "Madison" "https://business.madisonchamber.com/list"

  # Custom output file with defaults:
  python3 chamber_scraper.py --output my_businesses.csv

OPTIONS:
  --help, -h        Show this help message
  --output FILE     Specify output CSV filename (default: chamber_businesses.csv)
  --list-defaults   Show the default chambers that will be scraped

DEFAULT CHAMBERS:
  1. Old Saybrook Chamber (Old Saybrook, Westbrook area)
  2. Eastern CT Chamber of Commerce (Waterford, New London, Groton, Stonington)
  3. Mystic Chamber (Mystic, Stonington area)
  4. CT River Valley Chamber (Glastonbury, Rocky Hill, Wethersfield, Cromwell)

NOTES:
  - If no chambers specified, defaults are used
  - Chamber names and URLs must be provided in pairs
  - URLs should point to the /list page of the chamber directory
  - Output file will be created in the current directory
""")


def main():
    """Main scraper function"""
    # Check for help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
        return
    
    # Check for list-defaults flag
    if '--list-defaults' in sys.argv:
        print("\nDefault Chambers:")
        print("="*60)
        for i, chamber in enumerate(get_default_chambers(), 1):
            print(f"{i}. {chamber['name']}")
            print(f"   URL: {chamber['url']}")
        print("="*60)
        return
    
    # Check for output filename
    output_file = 'chamber_businesses.csv'
    args = sys.argv[1:]  # Skip script name
    
    if '--output' in args:
        try:
            output_index = args.index('--output')
            output_file = args[output_index + 1]
            # Remove these from args
            args.pop(output_index)
            args.pop(output_index)
        except (IndexError, ValueError):
            print("Error: --output requires a filename")
            return
    
    scraper = ChamberScraper()
    
    # Parse command line arguments for chambers
    chambers = []
    
    if len(args) == 0:
        # Use default chambers
        print("Using default chambers...")
        chambers = get_default_chambers()
    elif len(args) % 2 != 0:
        print("Error: Chamber names and URLs must be provided in pairs")
        print("Example: python3 chamber_scraper.py 'Chamber Name' 'https://...' 'Chamber Name 2' 'https://...'")
        print("\nRun with --help for more information")
        return
    else:
        # Parse chamber name/URL pairs
        for i in range(0, len(args), 2):
            chambers.append({
                'name': args[i],
                'url': args[i + 1]
            })
    
    print("="*60)
    print("Chamber of Commerce Scraper")
    print("="*60)
    print(f"\nChambers to scrape: {len(chambers)}")
    for chamber in chambers:
        print(f"  - {chamber['name']}")
    print(f"\nOutput file: {output_file}")
    print("\nThis will take several minutes - please be patient!")
    
    # Scrape each chamber
    for chamber in chambers:
        scraper.scrape_chamber_list(chamber['url'], chamber['name'])
    
    # Save results to specified output file
    output_path = os.path.join(os.getcwd(), output_file)
    scraper.save_to_csv(output_path)
    
    print(f"\n✅ Scraping complete!")
    print(f"Check {output_path} for results")


if __name__ == "__main__":
    main()
