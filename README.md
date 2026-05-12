# 🏨 Google Travel Hotel Scraper — Tanzania

A multi-threaded Python scraper for **[Google Travel](https://www.google.com/travel)** that extracts detailed hotel listings from multiple Tanzanian cities. It first collects all listing URLs across paginated search results, then visits each listing to extract a rich set of 22 data fields including amenities, images, check-in/out times, pricing, and verifications.

---

## 📁 Project Structure

```
google-travel-hotel-scraper/
│
├── travel.py            # Main scraper — link collection + data extraction + threading
├── essential.py         # Lightweight standalone Playwright base class (TravelEssentials)
│
└── city_wise_data/      # Per-city CSV output (auto-generated)
│   ├── city1.csv
│   ├── city2.csv
│   ├── city3.csv
│   ├── city4.csv
│   └── city5.csv
└── merge_file.csv         # Aggregated output across all cities (auto-generated)
```

---

## ✨ Features

- **Two-phase scraping per city**: Collects all listing URLs first (with full pagination), then visits each one for deep data extraction.
- **22 data fields per hotel**: Title, address, phone, website, directions, price, rating, reviews, sleep capacity, bedrooms, bathrooms, beds, property size, images, description, check-in/out, amenities, verifications, and other booking sources.
- **Smart amenities fallback**: Tries two different selectors for amenities and filters out "No X" entries automatically.
- **Image URL cleaning**: Strips query parameters from image URLs for clean, direct links.
- **Multi-threaded**: Runs 5 city scrapers in parallel using Python `Thread`, with staggered starts to avoid browser crashes.
- **Dual CSV output**: Saves data both per city (`city_wise_data/<city>.csv`) and in a combined `merge_file.csv`.
- **Configurable headless mode**: `PlaywrightAssistantClass` accepts a `headless` parameter for easy toggling.

---

## 🔧 Requirements

### Python Version
- Python 3.8+

### Dependencies

```bash
pip install playwright pandas
playwright install chromium
```

| Package      | Purpose                              |
|--------------|--------------------------------------|
| `playwright` | Browser automation                   |
| `pandas`     | CSV output management                |

---

## 🚀 Getting Started

### Run the Scraper

```bash
python travel.py
```

The script will:
1. Launch 5 browser threads (one per city), staggered 10 seconds apart.
2. Each thread paginates through all Google Travel hotel search results for its city.
3. After collecting all listing URLs, each thread visits every listing and extracts full hotel data.
4. Results are saved to per-city CSVs and the combined `merge_file.csv`.

---

## ⚙️ Configuration

### Changing Target Cities

Update the URL variables and `Thread` calls at the bottom of `travel.py`:

```python
url6 = "https://www.google.com/travel/search?q=hotels+in+Dar+es+Salaam+tanzania&..."

th6 = Thread(target=handle_multi_threading, args=("Dar es Salaam", url6))
th6.start()
```

**How to get a Google Travel search URL:**
1. Go to [google.com/travel](https://www.google.com/travel)
2. Search for `hotels in <City> Tanzania`
3. Copy the full URL from your browser's address bar.

### Thread Start Delay

```python
time.sleep(10)  # Delay between launching each city thread
```

Increase this on lower-spec machines to avoid memory pressure from simultaneous browser launches.

### Headless Mode

In `travel.py`, `GoogleTravelDataScraper` extends `GoogleTravelLinkScraper` which passes `headless=False` by default. To run without visible browser windows:

```python
class GoogleTravelLinkScraper(PlaywrightAssistantClass):
    def __init__(self):
        PlaywrightAssistantClass.__init__(self, headless=True)  # Change to True
```

---

## 📊 Output Data Format

### `city_wise_data/<City>.csv` and `Tanzania.csv`

| Field                  | Description                                              |
|------------------------|----------------------------------------------------------|
| `Target City`          | City name passed to the thread                           |
| `Title`                | Hotel name                                               |
| `Address`              | Hotel address (from aria-label)                          |
| `Phone`                | Hotel phone number                                       |
| `Website`              | Official website URL                                     |
| `Direction`            | Google Maps directions URL                               |
| `Estimated Price`      | Nightly price estimate                                   |
| `Rating`               | Star rating (e.g., 4.5)                                  |
| `Reviews`              | Number of reviews                                        |
| `Sleeps`               | Maximum guest capacity                                   |
| `Bedrooms`             | Number of bedrooms                                       |
| `Bathrooms`            | Number of bathrooms                                      |
| `Beds`                 | Number of beds                                           |
| `Property Size (sq m)` | Property size in square metres                           |
| `Images`               | Comma-separated cleaned image URLs                       |
| `Description`          | Hotel description text                                   |
| `Check-in`             | Check-in time                                            |
| `Check-out`            | Check-out time                                           |
| `Amenities`            | Comma-separated list of amenities                        |
| `Verifications`        | Comma-separated verifications (e.g., Google verified)    |
| `Other Sources`        | Comma-separated links from other booking platforms       |
| `Listing URL`          | Full Google Travel listing URL                           |

---

## 🏗️ Architecture Overview

```
essential.py
    └── TravelEssentials                      # Lightweight standalone base class
        ├── __init__()                        # Launch Playwright (headless=False)
        ├── extract_single_element()          # Get one element (text or attribute)
        └── extract_multiple_elements()       # Get list of elements

travel.py
    ├── PlaywrightAssistantClass              # Full-featured base browser class
    │   ├── __init__(headless)                # Launch Chromium context
    │   ├── navigate(url)                     # Go to URL + zoom to 25%
    │   ├── extract_single_element()          # Get one element
    │   ├── extract_multiple_elements()       # Get list of elements
    │   ├── click_on_btn()                    # Click element by selector
    │   └── save_into_file(df, city)          # Save to city CSV + Tanzania.csv
    │
    ├── GoogleTravelLinkScraper               # Pagination + link collection
    │   ├── handle_pagination()               # Click "Next" on results page
    │   └── extract_listing_links()           # Collect all hotel listing hrefs
    │
    ├── GoogleTravelDataScraper               # Hotel detail extractor
    │   └── extract_data_points(url, city)    # Extract all 22 fields from listing
    │
    └── handle_multi_threading(city, url)     # Full pipeline for one city:
        ├── Phase 1: Paginate + collect all links
        └── Phase 2: Visit each link + extract + save

    └── 5 Threads launched in parallel (one per Tanzanian city)
```

---

## 🔀 About `essential.py`

`essential.py` contains `TravelEssentials` — a **lightweight, standalone** Playwright base class that mirrors the core extraction methods of `PlaywrightAssistantClass` but without cookie management, stealth, or file I/O. It can be used independently for quick prototyping or as the foundation for other travel scrapers without the full overhead.

Key differences from `PlaywrightAssistantClass`:

| Feature                  | `PlaywrightAssistantClass` | `TravelEssentials` |
|--------------------------|----------------------------|--------------------|
| Cookie support           | ✅                          | ❌                  |
| Stealth mode             | Optional                   | ❌                  |
| File saving              | ✅                          | ❌                  |
| `wait_for_selector`      | ❌                          | ✅                  |
| Headless toggle          | ✅ (parameter)              | ❌ (always False)   |

---

## ⚠️ Notes & Limitations

- Google Travel search URLs contain session-specific parameters — regenerate them if they expire or return no results.
- **Headless is disabled** by default — browser windows will be visible.
- The scraper clicks into the **Photos** and **About** tabs on each listing to extract images and address/phone — these tab clicks add `~2 seconds` per listing.
- Amenities use a two-selector fallback strategy; if both fail, the field will be empty.
- Scraping Google Travel may violate [Google's Terms of Service](https://policies.google.com/terms). Use responsibly.

---

## 📌 Example Usage

```python
# Add a new city
url6 = "https://www.google.com/travel/search?q=hotels+in+Dodoma+tanzania&..."
th6 = Thread(target=handle_multi_threading, args=("Dodoma", url6))
th6.start()
th6.join()
```

---

## 🏷️ Repo Name & Description

**Repo name:** `google-travel-hotel-scraper`

**Description:** `Multi-threaded Python scraper for Google Travel hotel listings — extracts 22 fields per property (price, amenities, images, check-in/out, verifications) across multiple cities using Playwright, with dual CSV output per city and aggregated.`

---

## 👤 Author

**Muhammad Anwaar Rasool**
Automation & Web Scraping Engineer

---

## 📄 License

This project is for educational and personal use only. The author is not responsible for any misuse of this tool.
