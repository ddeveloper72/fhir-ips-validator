"""
Analyze SOAP response to find validation result OID
Goal: Extract OID from SOAP response to construct report URL automatically
"""

import xml.etree.ElementTree as ET
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_evs_validation import validate_document

def analyze_soap_response_structure():
    """Analyze a SOAP response to find the validation result OID"""
    print("=" * 80)
    print("🔍 ANALYZING SOAP RESPONSE FOR VALIDATION RESULT OID")
    print("=" * 80)
    
    # Perform a test validation to get fresh response
    wsdl_url = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
    test_file = 'examples/2-5678-W7_PS.xml'
    validator = 'HL7 - CDA Release 2'
    
    print(f"\n📋 Performing test validation:")
    print(f"   File: {test_file}")
    print(f"   Validator: {validator}")
    print(f"   Platform: EHDS Gazelle")
    
    result = validate_document(test_file, validator, wsdl_url)
    
    print(f"\n✅ Validation complete!")
    print(f"   Status: {result.get('status', 'Unknown')}")
    
    # Read the saved raw XML response
    raw_xml_file = 'logs/gazelle_last_response.xml'
    
    if not os.path.exists(raw_xml_file):
        print(f"\n❌ Raw XML file not found: {raw_xml_file}")
        return None
    
    print(f"\n📄 Reading raw SOAP response from: {raw_xml_file}")
    
    with open(raw_xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    print(f"   Size: {len(xml_content)} bytes")
    
    # Parse XML
    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        print(f"❌ Failed to parse XML: {e}")
        return None
    
    # Explore the XML structure
    print(f"\n{'='*80}")
    print("XML STRUCTURE ANALYSIS")
    print(f"{'='*80}")
    
    print(f"\nRoot element: {root.tag}")
    print(f"Root attributes: {root.attrib}")
    
    # Look for OID-like attributes and elements
    print(f"\n{'─'*80}")
    print("Searching for OID patterns...")
    print(f"{'─'*80}")
    
    oids_found = []
    
    def search_for_oids(element, path=""):
        """Recursively search for OID patterns"""
        current_path = f"{path}/{element.tag.split('}')[-1]}"
        
        # Check attributes for OID patterns
        for attr, value in element.attrib.items():
            if 'oid' in attr.lower() or (isinstance(value, str) and value.startswith('1.3.6.1.4.1.12559')):
                oids_found.append({
                    'path': current_path,
                    'attr': attr,
                    'value': value,
                    'type': 'attribute'
                })
        
        # Check element text for OID patterns
        if element.text and element.text.strip():
            text = element.text.strip()
            if text.startswith('1.3.6.1.4.1.12559'):
                oids_found.append({
                    'path': current_path,
                    'attr': 'text',
                    'value': text,
                    'type': 'element'
                })
        
        # Check for specific interesting elements
        tag_name = element.tag.split('}')[-1].lower()
        if any(keyword in tag_name for keyword in ['validation', 'result', 'report', 'id', 'reference']):
            if element.text and element.text.strip():
                oids_found.append({
                    'path': current_path,
                    'attr': 'text',
                    'value': element.text.strip(),
                    'type': 'interesting_element'
                })
        
        # Recurse
        for child in element:
            search_for_oids(child, current_path)
    
    search_for_oids(root)
    
    if oids_found:
        print(f"\n✅ Found {len(oids_found)} potential OID references:\n")
        for i, oid_info in enumerate(oids_found, 1):
            print(f"{i}. Path: {oid_info['path']}")
            print(f"   Type: {oid_info['type']}")
            print(f"   {oid_info['attr']}: {oid_info['value']}")
            print()
    else:
        print(f"\n⚠️ No obvious OID patterns found")
    
    # Look for ValidationResultsOverview and nearby elements
    print(f"\n{'─'*80}")
    print("Looking for ValidationResultsOverview section...")
    print(f"{'─'*80}")
    
    for elem in root.iter():
        if 'ValidationResultsOverview' in elem.tag or 'validationresultsoverview' in elem.tag.lower():
            print(f"\n✅ Found: {elem.tag}")
            print(f"   Attributes: {elem.attrib}")
            print(f"   Children:")
            for child in elem:
                child_tag = child.tag.split('}')[-1]
                child_text = child.text.strip() if child.text else ''
                print(f"      {child_tag}: {child_text[:100]}")
            
            # Check parent for OID
            print(f"\n   Checking parent context...")
            # Find parent by searching again (ET doesn't track parents well)
            break
    
    # Print first 2000 chars of raw XML for manual inspection
    print(f"\n{'─'*80}")
    print("Raw XML Preview (first 2000 chars):")
    print(f"{'─'*80}")
    print(xml_content[:2000])
    
    print(f"\n{'─'*80}")
    print("Raw XML Preview (last 1000 chars):")
    print(f"{'─'*80}")
    print(xml_content[-1000:])
    
    # Save OID findings for analysis
    findings_file = 'logs/oid_analysis.txt'
    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SOAP Response OID Analysis\n")
        f.write("="*80 + "\n\n")
        
        if oids_found:
            f.write(f"Found {len(oids_found)} potential OID references:\n\n")
            for i, oid_info in enumerate(oids_found, 1):
                f.write(f"{i}. Path: {oid_info['path']}\n")
                f.write(f"   Type: {oid_info['type']}\n")
                f.write(f"   {oid_info['attr']}: {oid_info['value']}\n\n")
        else:
            f.write("No OID patterns found in SOAP response.\n\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("Full Raw XML:\n")
        f.write("="*80 + "\n\n")
        f.write(xml_content)
    
    print(f"\n💾 Analysis saved to: {findings_file}")
    
    return oids_found

def main():
    oids_found = analyze_soap_response_structure()
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    if oids_found:
        validation_oids = [o for o in oids_found if o['type'] == 'attribute' and 'oid' in o['attr'].lower()]
        
        if validation_oids:
            print(f"\n✅ Found validation result OID(s)!")
            print(f"\nMost likely candidate:")
            print(f"   OID: {validation_oids[0]['value']}")
            print(f"   Location: {validation_oids[0]['path']}")
            
            # Try to construct report URL
            base_url = 'https://ehds.gazelle-platform.net'
            report_url = f"{base_url}/evs/report.seam?oid={validation_oids[0]['value']}"
            
            print(f"\n🌐 Potential Report URL:")
            print(f"   {report_url}")
            print(f"\n   Try opening this URL in your browser to verify!")
        else:
            print(f"\n⚠️ Found OID patterns but none look like validation result OIDs")
    else:
        print(f"\n❌ No validation result OID found in SOAP response")
        print(f"\nPossible reasons:")
        print(f"   1. SOAP API doesn't return validation result OIDs")
        print(f"   2. OID is in a different format than expected")
        print(f"   3. Need to examine raw XML manually")
    
    print(f"\n📝 Next step:")
    print(f"   Check logs/oid_analysis.txt for full details")
    print(f"   Check logs/gazelle_last_response.xml for raw XML")

if __name__ == '__main__':
    main()
