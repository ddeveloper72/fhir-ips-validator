"""
Fetch and parse Gazelle EVS public validation logs.

Tries to extract CDA documents from public validation logs.

Usage:
    python scripts/fetch_gazelle_logs.py
"""

import os
import sys
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json

load_dotenv()

EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')
EVS_API_KEY = os.getenv('EVS_API_KEY')


def print_header(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def fetch_validation_logs():
    """Fetch CDA validation logs"""
    print_header("Fetching Gazelle CDA Validation Logs")
    
    # URL from the discovered link
    logs_url = f"{EVS_BASE_URL}/evs/cda/allLogs.seam?standard=10"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    if EVS_API_KEY:
        headers['X-API-Key'] = EVS_API_KEY
    
    print(f"Fetching: {logs_url}\n")
    
    try:
        response = requests.get(logs_url, headers=headers, timeout=30, verify=True)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            # Save HTML
            html_file = Path('logs') / 'gazelle_all_logs.html'
            html_file.parent.mkdir(exist_ok=True)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Saved HTML to: {html_file}")
            
            return response.text
        else:
            print(f"❌ Failed to fetch logs")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def parse_validation_logs(html_content):
    """Parse validation logs HTML"""
    print_header("Parsing Validation Logs")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for tables with validation results
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables\n")
    
    validations = []
    
    for table_idx, table in enumerate(tables, 1):
        print(f"Table {table_idx}:")
        print(f"  Class: {table.get('class', [])}")
        print(f"  ID: {table.get('id', 'N/A')}")
        
        # Get all rows
        rows = table.find_all('tr')
        print(f"  Rows: {len(rows)}")
        
        # Look for header row
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            print(f"  Headers: {headers}")
        else:
            # Try first row as headers
            first_row = rows[0] if rows else None
            if first_row:
                headers = [cell.get_text(strip=True) for cell in first_row.find_all(['th', 'td'])]
                print(f"  First row (possible headers): {headers}")
        
        # Parse data rows
        data_start = 1 if headers else 0
        
        for row_idx, row in enumerate(rows[data_start:data_start + 20], 1):  # Check first 20
            cells = row.find_all(['td', 'th'])
            if cells and len(cells) >= 3:  # Valid data row
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Check if this row has an OID (validation entry)
                first_cell = cell_texts[0] if cell_texts else ''
                
                # OIDs start with numbers and dots
                if re.match(r'^\d+\.\d+\.\d+', first_cell):
                    if row_idx <= 10:  # Show first 10 validation entries
                        print(f"    Row {row_idx}: {cell_texts}")
                    
                    # Look for the first link (should be the OID link to report)
                    links = row.find_all('a')
                    if links:
                        first_link = links[0]
                        href = first_link.get('href', '')
                        text = first_link.get_text(strip=True)
                        
                        if href and text:
                            if row_idx <= 10:
                                print(f"      Report link: {text} -> {href}")
                            
                            validation_data = {
                                'oid': text,
                                'date': cell_texts[1] if len(cell_texts) > 1 else '',
                                'validator': cell_texts[4] if len(cell_texts) > 4 else '',
                                'status': cell_texts[6] if len(cell_texts) > 6 else '',
                                'report_url': href,
                                'cells': cell_texts
                            }
                            
                            validations.append(validation_data)
        
        if len(rows) > data_start + 5:
            print(f"    ... and {len(rows) - data_start - 5} more rows")
        
        print()
    
    # Look for any direct XML or document links
    all_links = soup.find_all('a')
    xml_links = [link for link in all_links if '.xml' in str(link.get('href', '')).lower()]
    
    if xml_links:
        print(f"Found {len(xml_links)} XML file links:")
        for link in xml_links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  - {text}: {href}")
    
    # Look for download or view buttons
    download_links = soup.find_all('a', text=re.compile(r'download|view|details', re.IGNORECASE))
    
    if download_links:
        print(f"\nFound {len(download_links)} download/view links:")
        for link in download_links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  - {text}: {href}")
    
    print(f"\nTotal validation entries found: {len(validations)}")
    
    return validations


def main():
    """Main function"""
    # Fetch logs
    html = fetch_validation_logs()
    
    if html:
        # Parse logs
        validations = parse_validation_logs(html)
        
        # Save parsed data
        if validations:
            output_file = Path('logs') / 'parsed_validations.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(validations, f, indent=2)
            print(f"\n✅ Saved parsed data to: {output_file}")
        
        print_header("Next Steps")
        print("1. Review the saved HTML file: logs/gazelle_all_logs.html")
        print("2. Look for validation entries with 'PASSED' status")
        print("3. Find links to view or download validated CDA documents")
        print("\nOr, log in to Gazelle manually:")
        print("1. Go to: https://gazelle.ehdsi.eu/evs/cda/allLogs.seam?standard=10")
        print("2. Log in with your credentials")
        print("3. Find your passed validations")
        print("4. Download the CDA XML documents")
        print("5. Save them to examples/ directory")
    else:
        print("\n❌ Could not fetch validation logs")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
