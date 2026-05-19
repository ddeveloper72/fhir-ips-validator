"""
Parse Gazelle EVS validation history from HTML web interface.

Since Gazelle doesn't have a REST API for test results, this script:
1. Fetches validation history HTML pages
2. Parses them to extract test information
3. Downloads CDA documents from passed validations

Usage:
    python scripts/parse_gazelle_validation_history.py
    python scripts/parse_gazelle_validation_history.py --session-cookie "your_session_cookie"
"""

import os
import sys
import re
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment
load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def print_section(title):
    """Print formatted section"""
    print(f"\n{'─'*80}")
    print(f"{title}")
    print(f"{'─'*80}")


def get_session_headers(session_cookie=None):
    """Get HTTP headers with session authentication"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    if session_cookie:
        headers['Cookie'] = session_cookie
    
    if EVS_API_KEY:
        headers['X-API-Key'] = EVS_API_KEY
    
    return headers


def fetch_validation_page(page_url, session_cookie=None):
    """Fetch validation history page"""
    print_section(f"Fetching: {page_url}")
    
    headers = get_session_headers(session_cookie)
    
    try:
        response = requests.get(page_url, headers=headers, timeout=30, verify=True)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Failed to fetch page")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def parse_validation_list(html_content):
    """Parse validation list HTML to extract test information"""
    print_section("Parsing validation list")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    validations = []
    
    # Look for common table structures in Gazelle interface
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    for table_idx, table in enumerate(tables):
        print(f"\nTable {table_idx + 1}:")
        
        # Try to find validation data in table rows
        rows = table.find_all('tr')
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 3:
                # Extract text from cells
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Look for CDA-related validations
                row_text = ' '.join(cell_texts).lower()
                
                if 'cda' in row_text or 'validation' in row_text:
                    # Look for links to validation details or documents
                    links = row.find_all('a')
                    
                    validation_info = {
                        'row_index': row_idx,
                        'cells': cell_texts,
                        'links': []
                    }
                    
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if href:
                            # Make absolute URL if relative
                            if href.startswith('/'):
                                href = f"{EVS_BASE_URL}{href}"
                            
                            validation_info['links'].append({
                                'text': text,
                                'href': href
                            })
                    
                    if validation_info['links'] or 'pass' in row_text or 'success' in row_text:
                        validations.append(validation_info)
                        print(f"  ✅ Found validation: {cell_texts[:3]}")
    
    # Also look for specific Gazelle validation result links
    all_links = soup.find_all('a', href=re.compile(r'validation|cda|document', re.IGNORECASE))
    print(f"\nFound {len(all_links)} validation-related links")
    
    for link in all_links[:10]:  # Show first 10
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  - {text}: {href[:80]}")
    
    print(f"\nTotal validations found: {len(validations)}")
    return validations


def extract_document_links(html_content):
    """Extract direct links to CDA documents"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    doc_links = []
    
    # Look for links that might point to XML documents
    patterns = [
        r'\.xml$',
        r'document.*download',
        r'cda.*download',
        r'validation.*document'
    ]
    
    for pattern in patterns:
        links = soup.find_all('a', href=re.compile(pattern, re.IGNORECASE))
        
        for link in links:
            href = link.get('href', '')
            if href:
                if href.startswith('/'):
                    href = f"{EVS_BASE_URL}{href}"
                
                doc_links.append({
                    'text': link.get_text(strip=True),
                    'url': href
                })
    
    return doc_links


def download_document(url, output_dir='examples', filename=None):
    """Download a document from URL"""
    print(f"\nDownloading: {url}")
    
    headers = get_session_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=True)
        
        if response.status_code == 200:
            # Determine filename
            if not filename:
                # Try to get from Content-Disposition header
                cd = response.headers.get('Content-Disposition', '')
                if 'filename=' in cd:
                    filename = cd.split('filename=')[1].strip('"\'')
                else:
                    # Generate from URL
                    filename = url.split('/')[-1]
                    if not filename.endswith('.xml'):
                        filename = f"{filename}.xml"
            
            # Save document
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            filepath = output_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✅ Saved: {filepath}")
            return str(filepath)
        else:
            print(f"  ❌ Failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Parse Gazelle EVS validation history from web interface'
    )
    parser.add_argument(
        '--session-cookie',
        type=str,
        help='Session cookie from logged-in Gazelle session (for accessing your validations)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='examples',
        help='Output directory for downloaded documents'
    )
    parser.add_argument(
        '--save-html',
        action='store_true',
        help='Save HTML pages for inspection'
    )
    
    args = parser.parse_args()
    
    print_header("Gazelle EVS - Parse Validation History")
    print(f"Base URL: {EVS_BASE_URL}")
    print(f"Output: {args.output}")
    
    if args.session_cookie:
        print(f"Session Cookie: {args.session_cookie[:30]}...")
    else:
        print("⚠️  No session cookie provided - may only see public validations")
        print("\nTo access your private validations:")
        print("1. Go to https://gazelle.ehdsi.eu/evs/home.seam")
        print("2. Log in")
        print("3. Open browser DevTools > Network tab")
        print("4. Refresh page")
        print("5. Copy 'Cookie' header value")
        print("6. Run: python scripts/parse_gazelle_validation_history.py --session-cookie \"<cookie>\"")
    
    # Fetch validation pages
    pages_to_check = [
        f"{EVS_BASE_URL}/evs/validation/validations.seam",
        f"{EVS_BASE_URL}/evs/validation/validationsList.seam",
    ]
    
    all_validations = []
    all_doc_links = []
    
    for page_url in pages_to_check:
        html = fetch_validation_page(page_url, args.session_cookie)
        
        if html:
            # Save HTML for inspection if requested
            if args.save_html:
                html_file = Path('logs') / f"gazelle_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                html_file.parent.mkdir(exist_ok=True)
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"  💾 Saved HTML to: {html_file}")
            
            # Parse validations
            validations = parse_validation_list(html)
            all_validations.extend(validations)
            
            # Extract document links
            doc_links = extract_document_links(html)
            all_doc_links.extend(doc_links)
    
    # Summary
    print_header("Summary")
    print(f"Found {len(all_validations)} validation entries")
    print(f"Found {len(all_doc_links)} document links")
    
    if all_doc_links:
        print("\nDocument links found:")
        for link in all_doc_links[:10]:  # Show first 10
            print(f"  - {link['text']}: {link['url']}")
        
        # Ask to download
        print("\n" + "="*80)
        print("Would you like to download these documents? (y/n)")
        # For now, just show what we found
    
    if not all_validations and not all_doc_links:
        print("\n⚠️  No validation data found")
        print("\nPossible reasons:")
        print("1. You need to be logged in (provide --session-cookie)")
        print("2. The HTML structure has changed")
        print("3. Validation history is empty")
        print("\nManual approach:")
        print("1. Go to: https://gazelle.ehdsi.eu/evs/validation/validations.seam")
        print("2. Log in and navigate to your validation history")
        print("3. Download CDA documents that passed validation")
        print("4. Save them to examples/ directory")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
