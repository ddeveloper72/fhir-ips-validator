"""
Download CDA documents from passed Gazelle validations.

Fetches validation report pages and extracts the CDA XML documents.

Usage:
    python scripts/download_passed_cda_docs.py
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

load_dotenv()

EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')


def print_header(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def fetch_validation_report(report_url):
    """Fetch validation report page"""
    print(f"\nFetching: {report_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    try:
        response = requests.get(report_url, headers=headers, timeout=30, verify=True)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"  ❌ Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def extract_cda_from_report(html_content):
    """Extract CDA XML document from validation report"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for XML content in various places
    
    # 1. Look for <pre> or <code> tags containing XML
    pre_tags = soup.find_all(['pre', 'code'])
    for pre in pre_tags:
        content = pre.get_text()
        if '<?xml' in content and 'ClinicalDocument' in content:
            print(f"  ✅ Found CDA XML in <{pre.name}> tag")
            return content.strip()
    
    # 2. Look for textarea with XML
    textareas = soup.find_all('textarea')
    for textarea in textareas:
        content = textarea.get_text()
        if '<?xml' in content and 'ClinicalDocument' in content:
            print(f"  ✅ Found CDA XML in <textarea>")
            return content.strip()
    
    # 3. Look for divs with specific classes that might contain XML
    xml_divs = soup.find_all('div', class_=re.compile(r'xml|document|content', re.IGNORECASE))
    for div in xml_divs:
        content = div.get_text()
        if '<?xml' in content and 'ClinicalDocument' in content:
            print(f"  ✅ Found CDA XML in <div class='{div.get('class')}'>")
            return content.strip()
    
    # 4. Look for download links
    download_links = soup.find_all('a', href=re.compile(r'download|document|xml', re.IGNORECASE))
    if download_links:
        print(f"  📎 Found {len(download_links)} potential download links:")
        for link in download_links[:5]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"    - {text}: {href}")
        
        # Try to download from the first link
        first_link = download_links[0]
        href = first_link.get('href', '')
        if href:
            if not href.startswith('http'):
                href = f"{EVS_BASE_URL}{href}"
            
            print(f"  🔗 Attempting to download from: {href}")
            try:
                response = requests.get(href, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
                if response.status_code == 200 and 'xml' in response.headers.get('Content-Type', '').lower():
                    print(f"  ✅ Downloaded XML document")
                    return response.text
            except:
                pass
    
    # 5. Check if the entire page might be XML (rare but possible)
    page_text = soup.get_text()
    if page_text.strip().startswith('<?xml') and 'ClinicalDocument' in page_text:
        print(f"  ✅ Entire page is XML document")
        return page_text.strip()
    
    print(f"  ⚠️  Could not find CDA XML in report")
    return None


def save_cda_document(xml_content, oid, validator, output_dir='examples'):
    """Save CDA document to file"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract document info for better filename
    try:
        root = ET.fromstring(xml_content)
        ns = {'cda': 'urn:hl7-org:v3'}
        
        title_elem = root.find('.//cda:title', ns)
        title = title_elem.text if title_elem is not None else 'unknown'
        
        # Clean title for filename
        title_clean = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_').lower()
        
        # Get document type from code
        code_elem = root.find('.//cda:code[@displayName]', ns)
        doc_type = code_elem.get('displayName', 'cda').replace(' ', '_').lower() if code_elem is not None else 'cda'
        
        filename = f"gazelle_passed_{doc_type}_{title_clean[:30]}.xml"
        
    except:
        # Fallback to OID-based filename
        filename = f"gazelle_passed_{oid.split('.')[-1]}.xml"
    
    filepath = output_path / filename
    
    # Save document
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"  ✅ Saved: {filepath}")
        
        # Extract and display metadata
        try:
            root = ET.fromstring(xml_content)
            ns = {'cda': 'urn:hl7-org:v3'}
            
            title_elem = root.find('.//cda:title', ns)
            title = title_elem.text if title_elem is not None else 'Unknown'
            
            code_elem = root.find('.//cda:code', ns)
            code = code_elem.get('displayName', 'Unknown') if code_elem is not None else 'Unknown'
            
            print(f"     Document: {title}")
            print(f"     Type: {code}")
            
        except:
            pass
        
        return str(filepath)
        
    except Exception as e:
        print(f"  ❌ Save error: {e}")
        return None


def main():
    """Main function"""
    print_header("Download CDA Documents from Passed Gazelle Validations")
    
    # Load parsed validations
    parsed_file = Path('logs/parsed_validations.json')
    
    if not parsed_file.exists():
        print("❌ No parsed validations found")
        print("Run: py scripts/fetch_gazelle_logs.py first")
        return 1
    
    with open(parsed_file, 'r') as f:
        validations = json.load(f)
    
    print(f"Found {len(validations)} validation entries\n")
    
    # Filter for passed validations
    passed_validations = []
    
    for val in validations:
        status = val.get('status', '')
        oid = val.get('oid', '')
        report_url = val.get('report_url', '')
        
        if 'DONE_PASSED' in status:
            passed_validations.append(val)
            validator = val.get('validator', 'unknown')
            print(f"✅ Passed: {oid} ({validator[:50]}...)")
    
    print(f"\nFound {len(passed_validations)} PASSED validations")
    
    if not passed_validations:
        print("\n⚠️  No passed validations found")
        return 1
    
    # Download CDA documents from passed validations
    print_header("Downloading CDA Documents")
    
    downloaded = []
    
    for i, val in enumerate(passed_validations[:5], 1):  # Limit to first 5
        print(f"\n[{i}/{min(len(passed_validations), 5)}]")
        
        oid = val.get('oid', '')
        report_url = val.get('report_url', '')
        validator = val.get('validator', 'unknown')
        
        print(f"OID: {oid}")
        print(f"Validator: {validator}")
        
        if not report_url:
            print("  ⏭️  No report URL")
            continue
        
        # Make absolute URL
        if not report_url.startswith('http'):
            report_url = f"{EVS_BASE_URL}{report_url}"
        
        # Fetch report
        html = fetch_validation_report(report_url)
        
        if html:
            # Save report HTML for inspection
            report_file = Path('logs') / f"report_{oid.split('.')[-1]}.html"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  💾 Saved report HTML: {report_file}")
            
            # Extract CDA XML
            xml_content = extract_cda_from_report(html)
            
            if xml_content:
                filepath = save_cda_document(xml_content, oid, validator)
                if filepath:
                    downloaded.append(filepath)
    
    # Summary
    print_header("Summary")
    print(f"✅ Downloaded {len(downloaded)} CDA documents")
    
    if downloaded:
        print("\nFiles saved to:")
        for filepath in downloaded:
            print(f"  - {filepath}")
        
        print(f"\n🎉 You can now use these validated CDA examples!")
        print(f"\nNext steps:")
        print(f"1. Review the documents in examples/")
        print(f"2. Add them to your Streamlit UI example buttons")
        print(f"3. Test validation with Gazelle EVS")
    else:
        print("\n⚠️  Could not download any CDA documents")
        print("\nPossible reasons:")
        print("1. Report pages don't contain inline XML")
        print("2. Documents are behind authentication")
        print("3. Documents use different format/structure")
        print("\nManual approach:")
        print("1. Open the saved report HTML files in logs/")
        print("2. Look for download links or XML content")
        print("3. Download CDA documents manually")
        print("4. Save them to examples/ directory")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
