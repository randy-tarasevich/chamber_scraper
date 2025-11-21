# Chamber of Commerce Business Scraper

> Automated web scraping tool to identify Connecticut businesses without websites from Chamber of Commerce directories

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

**chamber_scraper.py** is a Python-based web scraper designed to extract business listings from Connecticut Chamber of Commerce member directories and identify which businesses don't have websites. Perfect for web developers, marketers, and sales professionals looking to generate leads for web development services.

### Key Features

- ✅ **Automated Multi-Level Crawling** - Navigates through chamber directories, categories, and individual business pages
- ✅ **Smart Website Detection** - Distinguishes real business websites from social media profiles
- ✅ **Comprehensive Data Extraction** - Captures business name, category, phone, address, email, and website status
- ✅ **Polite Scraping** - Includes rate limiting to respect server resources
- ✅ **CSV Export** - Clean, organized output ready for CRM import or spreadsheet analysis
- ✅ **Progress Tracking** - Real-time console output with status indicators

## 📋 Table of Contents

- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Configuration](#configuration)
- [Data Fields](#data-fields)
- [Legal & Ethical Considerations](#legal--ethical-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🔧 How It Works

The scraper uses a **3-level crawling process**:

### Level 1: Chamber Directory
- Fetches the main chamber directory page
- Identifies all business categories (Restaurants, Home Services, Professional Services, etc.)
- Queues each category for processing

### Level 2: Category Pages
- Visits each category page
- Extracts all business member links within that category
- Queues each business for detailed scraping

### Level 3: Business Details
- Visits individual business chamber profile pages
- Extracts comprehensive information using intelligent pattern matching
- Determines website presence/absence
- Stores data for export

### Intelligent Data Extraction

The scraper employs multiple extraction methods:

- **Phone Numbers**: Regex pattern matching for various formats `(860) 123-4567`, `860-123-4567`, etc.
- **Addresses**: Pattern recognition for Connecticut addresses with ZIP codes
- **Email Addresses**: Standard email regex validation
- **Website URLs**: Smart filtering that excludes:
  - Social media links (Facebook, Instagram, LinkedIn, Twitter)
  - Chamber internal links
  - Email/telephone links
  - Image hosting URLs

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install beautifulsoup4 requests
```

### Clone Repository

```bash
git clone https://github.com/yourusername/chamber-scraper.git
cd chamber-scraper
```

## 💻 Usage

### Basic Usage

Run the scraper with default settings:

```bash
python3 chamber_scraper.py
```

### Customize Target Chambers

Edit the `chambers` list in the `main()` function to add or modify target chambers:

```python
chambers = [
    {
        'name': 'Old Saybrook Chamber',
        'url': 'https://business.goschamber.com/list'
    },
    {
        'name': 'Clinton Chamber',
        'url': 'https://business.clintonchamber.org/list'
    },
    {
        'name': 'Madison Chamber',
        'url': 'https://business.madisonchamber.com/list'
    }
]
```

### Expected Runtime

- Small chamber (50-100 businesses): ~2-5 minutes
- Medium chamber (100-300 businesses): ~5-15 minutes  
- Large chamber (300+ businesses): ~15-30 minutes

## 📊 Output

### CSV File Structure

The scraper generates `chamber_businesses.csv` with the following structure:

| business_name | chamber | category | phone | address | email | website | has_website | description | chamber_url | scraped_date |
|--------------|---------|----------|-------|---------|-------|---------|-------------|-------------|-------------|--------------|
| ABC Plumbing | Old Saybrook | Home Services | (860) 555-0100 | 123 Main St, Old Lyme, CT 06371 | info@abc.com | | No | Full service plumbing... | https://... | 2025-11-21 |

### Console Output

Real-time progress tracking:

```
============================================================
Scraping: Old Saybrook Chamber
============================================================
Found 24 categories

  Category: Home Services
    Found 15 businesses
      ABC Plumbing: ❌ NO WEBSITE
      XYZ Heating: ✅ Has website
      ...

============================================================
Saved 287 businesses to chamber_businesses.csv
Businesses WITHOUT websites: 143
Businesses WITH websites: 144
============================================================
```

## ⚙️ Configuration

### Adjust Scraping Speed

Modify delays in the code to be more or less aggressive:

```python
# Between categories (default: 1 second)
time.sleep(1)

# Between businesses (default: 0.5 seconds)
time.sleep(0.5)
```

### Change Output Location

Modify the output path in the `main()` function:

```python
scraper.save_to_csv('/your/custom/path/output.csv')
```

## 📁 Data Fields

| Field | Description | Example |
|-------|-------------|---------|
| `business_name` | Business name | "Joe's Pizza" |
| `chamber` | Chamber of Commerce name | "Old Saybrook Chamber" |
| `category` | Business category | "Restaurants" |
| `phone` | Contact phone number | "(860) 555-1234" |
| `address` | Physical address | "123 Main St, Old Lyme, CT 06371" |
| `email` | Contact email | "info@joespizza.com" |
| `website` | Business website URL | "https://joespizza.com" or empty |
| `has_website` | Boolean indicator | "Yes" or "No" |
| `description` | Business description (truncated to 200 chars) | "Family-owned pizza restaurant..." |
| `chamber_url` | Link to chamber profile | "https://business.chamber.org/..." |
| `scraped_date` | Date of scraping | "2025-11-21" |

## ⚖️ Legal & Ethical Considerations

### Terms of Service

Before using this scraper:

1. **Review the target website's Terms of Service** and `robots.txt`
2. **Ensure compliance** with local and federal laws (CFAA, GDPR, etc.)
3. **Respect rate limits** and server resources
4. **Use data responsibly** - for legitimate business purposes only

### Best Practices

- ✅ Include respectful delays between requests (already implemented)
- ✅ Use a descriptive User-Agent string
- ✅ Don't circumvent authentication or paywalls
- ✅ Respect `robots.txt` directives
- ✅ Don't overload servers with concurrent requests
- ✅ Store and handle scraped data securely

### Intended Use Cases

This tool is designed for:
- Lead generation for web development services
- Market research and competitive analysis
- Business directory compilation
- Academic research on local business web presence

**Not intended for:**
- Spamming or unsolicited marketing at scale
- Reselling scraped data
- Any illegal or unethical purposes

## 🐛 Troubleshooting

### Network Errors

**Problem**: `HTTPSConnectionPool... Max retries exceeded`

**Solutions**:
- Check internet connection
- Verify target URLs are accessible
- Check if your IP is rate-limited or blocked
- Add longer delays between requests

### No Data Extracted

**Problem**: Scraper runs but finds no businesses

**Solutions**:
- Verify the chamber website structure hasn't changed
- Check CSS selectors and regex patterns
- Ensure target chamber uses compatible platform (ChamberMaster/GrowthZone)
- Print HTML content to debug extraction logic

### Incomplete Data

**Problem**: Some fields are empty when they shouldn't be

**Solutions**:
- Website structure may have changed - inspect HTML manually
- Adjust regex patterns for data extraction
- Add debug print statements to see what's being captured

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Ideas for Contributions

- Support for additional chamber platforms (Wild Apricot, Novi, etc.)
- Multi-threaded scraping for faster performance
- Database storage option (SQLite, PostgreSQL)
- Web-based UI for configuration
- API endpoint wrapper
- Export to additional formats (JSON, Excel)
- Email validation and enrichment
- Duplicate detection and merging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Randy** - Shoreline Web Solutions  
- Website: [Your Website]
- Location: Old Lyme, Connecticut

## 🙏 Acknowledgments

- Built for Connecticut shoreline business community
- Inspired by the need for better local business web presence
- Thanks to the Python web scraping community

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Email: [your-email@example.com]
- Connect via Shoreline United Networking (S.U.N.)

---

**⚠️ Disclaimer**: This tool is provided for educational and legitimate business purposes. Users are responsible for ensuring their use complies with all applicable laws, regulations, and website terms of service. Always obtain permission before scraping websites and respect robots.txt directives.

---

**Made with ☕ in Connecticut** | Helping local businesses get online since 2025
