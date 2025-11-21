#!/usr/bin/env python3
"""
Chamber of Commerce Business Scraper
Scrapes business listings from CT shoreline chamber directories
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
from datetime import datetime

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
            if href.startswith('http') and not any(x in href for x in ['goschamber.com', 'clintonchamber.org']):
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


def main():
    """Main scraper function"""
    scraper = ChamberScraper()
    
    # Define chambers to scrape
    chambers = [
        {
            'name': 'Old Saybrook Chamber',
            'url': 'https://business.goschamber.com/list'
        },
        {
            'name': 'Clinton Chamber',
            'url': 'https://business.clintonchamber.org/list'
        }
    ]
    
    print("Starting Chamber of Commerce Scraper...")
    print("This will take several minutes - please be patient!")
    
    for chamber in chambers:
        scraper.scrape_chamber_list(chamber['url'], chamber['name'])
    
    # Save results
    scraper.save_to_csv('/home/claude/chamber_businesses.csv')
    
    print("\n✅ Scraping complete!")
    print("Check chamber_businesses.csv for results")


if __name__ == "__main__":
    main()
