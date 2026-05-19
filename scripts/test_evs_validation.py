"""
Test Script: Validate FHIR/CDA Documents using eHDSI Gazelle EVS

This script tests validation of documents against the discovered eHDSI Gazelle
EVS validators using SOAP web services.

Usage:
    python scripts/test_evs_validation.py
    python scripts/test_evs_validation.py --document examples/patient_summary.xml
    python scripts/test_evs_validation.py --validator "eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)"
"""

import os
import sys
import argparse
import base64
from zeep import Client
from zeep.exceptions import Fault
from datetime import datetime
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment
load_dotenv()

# Discovered WSDL endpoints
CDA_WSDL = 'https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
XDS_WSDL = 'https://gazelle.ehdsi.eu/XDStarClient-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
SAML_WSDL = 'https://gazelle.ehdsi.eu/gazelle-xua-jar/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'

# Default validators to test
DEFAULT_VALIDATORS = [
    'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',  # Latest comprehensive
    'eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.1.0)',  # Structure only
    'HL7 - CDA Release 2',  # Basic CDA R2
]


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


def list_available_validators(wsdl_url):
    """List all validators available at the given WSDL endpoint"""
    print_section(f"Listing validators from: {wsdl_url}")
    
    try:
        client = Client(wsdl_url)
        validators = client.service.getListOfValidators()
        
        print(f"✓ Found {len(validators)} validators:\n")
        for i, validator in enumerate(validators, 1):
            print(f"{i:3d}. {validator}")
        
        return validators
    except Exception as e:
        print(f"✗ Error listing validators: {str(e)}")
        return []


def validate_document(document_path, validator_name, wsdl_url=CDA_WSDL):
    """
    Validate a document against the specified validator
    
    Args:
        document_path: Path to XML document
        validator_name: Name of validator to use
        wsdl_url: WSDL endpoint URL
    
    Returns:
        Validation result XML
    """
    print_section(f"Validating: {os.path.basename(document_path)}")
    print(f"Validator: {validator_name}")
    print(f"WSDL: {wsdl_url}")
    
    try:
        # Read document with proper encoding handling
        # Try UTF-8 first, fall back to Latin-1/Windows-1252 if that fails
        try:
            with open(document_path, 'rb') as f:
                xml_content = f.read()
        except Exception as e:
            print(f"✗ Error reading file: {str(e)}")
            return None
        
        # Create SOAP client
        client = Client(wsdl_url)
        
        # Encode to base64 for transmission
        base64_content = base64.b64encode(xml_content).decode('utf-8')
        
        print("\n⏳ Submitting validation request...")
        
        # Call validation service
        result = client.service.validateBase64Document(
            base64Document=base64_content,
            validator=validator_name
        )
        
        print("✓ Validation completed")
        
        # Save raw XML for debugging
        try:
            debug_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(debug_dir, exist_ok=True)
            
            debug_file = os.path.join(debug_dir, 'gazelle_last_response.xml')
            with open(debug_file, 'w', encoding='utf-8') as f:
                if hasattr(result, 'text'):
                    f.write(result.text)
                else:
                    f.write(str(result))
            print(f"📝 Debug: Raw XML saved to {debug_file}")
        except Exception as e:
            print(f"⚠️  Could not save debug XML: {e}")
        
        # Parse results into structured format
        parsed_results = parse_validation_result(result)
        
        # Add Gazelle web UI URL for manual validation (to get persistent reports)
        # Determine base URL from WSDL
        if 'ehds.gazelle-platform.net' in wsdl_url:
            gazelle_web_url = 'https://ehds.gazelle-platform.net/evs/home.seam'
        else:
            gazelle_web_url = 'https://gazelle.ehdsi.eu/evs/home.seam'
        
        parsed_results['gazelle_web_url'] = gazelle_web_url
        parsed_results['validator_name'] = validator_name
        
        return parsed_results
        
    except Fault as e:
        print(f"\n✗ SOAP Fault: {e.message}")
        print(f"   Code: {e.code}")
        if hasattr(e, 'detail'):
            print(f"   Detail: {e.detail}")
        return None
        
    except FileNotFoundError:
        print(f"✗ Document not found: {document_path}")
        return None
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        return None


def parse_validation_result(result_xml):
    """
    Parse Gazelle XML validation results into structured format
    
    Args:
        result_xml: XML validation result from EVS
    
    Returns:
        dict: Structured validation results with errors, warnings, info
    """
    try:
        # Convert result to string if needed
        if hasattr(result_xml, 'text'):
            xml_string = result_xml.text
        else:
            xml_string = str(result_xml)
        
        # Parse XML
        root = ET.fromstring(xml_string)
        
        # Initialize results structure
        results = {
            'errors': [],
            'warnings': [],
            'information': [],
            'status': 'unknown',
            'raw_xml': xml_string,
            'metadata': {}  # Add metadata section
        }
        
        # Define namespaces - Gazelle uses multiple formats
        namespaces = {
            'svrl': 'http://purl.oclc.org/dsdl/svrl',
            'report': 'http://gazelle.ihe.net/report',
            '': ''  # Handle no namespace
        }
        
        # Extract validation status
        status_elem = root.find('.//*[@name="status"]') or root.find('.//status')
        if status_elem is not None:
            results['status'] = status_elem.text or status_elem.get('value', 'unknown')
        
        # Check for overall PASSED/FAILED status
        for result_elem in root.findall('.//Result'):
            if result_elem.text in ['PASSED', 'FAILED']:
                results['status'] = result_elem.text
                break
        
        # METHOD 0A: Parse MDAValidation format (Wave 7/9 validators)
        mda_validation = root.find('.//MDAValidation')
        if mda_validation is not None:
            # Parse errors
            for error_elem in mda_validation.findall('.//Error'):
                test_elem = error_elem.find('.//Test')
                location_elem = error_elem.find('.//Location')
                description_elem = error_elem.find('.//Description')
                
                error_data = {
                    'test': test_elem.text if test_elem is not None and test_elem.text else '',
                    'location': location_elem.text if location_elem is not None and location_elem.text else '',
                    'diagnostics': description_elem.text if description_elem is not None and description_elem.text else 'Error found',
                    'details': {}
                }
                results['errors'].append(error_data)
            
            # Parse warnings
            for warning_elem in mda_validation.findall('.//Warning'):
                test_elem = warning_elem.find('.//Test')
                location_elem = warning_elem.find('.//Location')
                description_elem = warning_elem.find('.//Description')
                
                warning_data = {
                    'test': test_elem.text if test_elem is not None and test_elem.text else '',
                    'location': location_elem.text if location_elem is not None and location_elem.text else '',
                    'diagnostics': description_elem.text if description_elem is not None and description_elem.text else 'Warning found',
                    'details': {}
                }
                results['warnings'].append(warning_data)
            
            # Parse notes/info
            for note_elem in mda_validation.findall('.//Note'):
                test_elem = note_elem.find('.//Test')
                location_elem = note_elem.find('.//Location')
                description_elem = note_elem.find('.//Description')
                
                note_data = {
                    'test': test_elem.text if test_elem is not None and test_elem.text else '',
                    'location': location_elem.text if location_elem is not None and location_elem.text else '',
                    'diagnostics': description_elem.text if description_elem is not None and description_elem.text else 'Note',
                    'details': {}
                }
                results['information'].append(note_data)
        
        # Extract ValidationResultsOverview metadata
        overview = root.find('.//ValidationResultsOverview')
        if overview is not None:
            metadata = {}
            
            # Extract all fields from overview
            for child in overview:
                metadata[child.tag] = child.text
            
            results['metadata'] = metadata
            
            # Update status from overview if available
            if 'ValidationTestResult' in metadata:
                results['status'] = metadata['ValidationTestResult']
        
        # METHOD 0B: Parse XSDMessage format (Gazelle detailedResult)
        for xsd_msg in root.findall('.//XSDMessage'):
            severity_elem = xsd_msg.find('.//Severity')
            message_elem = xsd_msg.find('.//Message')
            line_elem = xsd_msg.find('.//lineNumber')
            col_elem = xsd_msg.find('.//columnNumber')
            
            if message_elem is not None and message_elem.text:
                location_parts = []
                if line_elem is not None and line_elem.text:
                    location_parts.append(f"Line {line_elem.text}")
                if col_elem is not None and col_elem.text:
                    location_parts.append(f"Column {col_elem.text}")
                
                error_data = {
                    'diagnostics': message_elem.text.strip(),
                    'location': ', '.join(location_parts) if location_parts else '',
                    'test': '',
                    'details': {}
                }
                
                # Determine severity
                severity = severity_elem.text.lower() if severity_elem is not None and severity_elem.text else 'error'
                if 'error' in severity:
                    results['errors'].append(error_data)
                elif 'warning' in severity or 'warn' in severity:
                    results['warnings'].append(error_data)
                else:
                    results['information'].append(error_data)
        
        # METHOD 1: Parse SVRL format (Schematron)
        for assertion in root.findall('.//{http://purl.oclc.org/dsdl/svrl}failed-assert'):
            error_data = {
                'test': assertion.get('test', ''),
                'location': assertion.get('location', ''),
                'diagnostics': '',
                'details': []
            }
            
            # Extract diagnostic text
            text_elem = assertion.find('{http://purl.oclc.org/dsdl/svrl}text')
            if text_elem is not None and text_elem.text:
                error_data['diagnostics'] = text_elem.text.strip()
            
            # Extract diagnostic reference if text is empty
            if not error_data['diagnostics']:
                diag_ref = assertion.find('{http://purl.oclc.org/dsdl/svrl}diagnostic-reference')
                if diag_ref is not None and diag_ref.text:
                    error_data['diagnostics'] = diag_ref.text.strip()
            
            if error_data['diagnostics']:  # Only add if we have a message
                # Categorize by severity
                test_lower = error_data['test'].lower()
                diag_lower = error_data['diagnostics'].lower()
                
                if 'error' in test_lower or 'shall' in diag_lower:
                    results['errors'].append(error_data)
                elif 'warning' in test_lower or 'should' in diag_lower:
                    results['warnings'].append(error_data)
                else:
                    results['information'].append(error_data)
        
        # METHOD 2: Parse ModelBasedValidationReport format
        for counter_item in root.findall('.//counterItem'):
            message = counter_item.find('.//message')
            location = counter_item.find('.//location')
            level = counter_item.find('.//level')
            
            if message is not None and message.text:
                error_data = {
                    'diagnostics': message.text.strip(),
                    'location': location.text.strip() if location is not None and location.text else '',
                    'test': '',
                    'details': []
                }
                
                # Determine severity from level
                level_text = level.text.lower() if level is not None and level.text else ''
                if 'error' in level_text or level_text == 'e':
                    results['errors'].append(error_data)
                elif 'warning' in level_text or level_text == 'w':
                    results['warnings'].append(error_data)
                else:
                    results['information'].append(error_data)
        
        # METHOD 3: Parse generic report format
        for item in root.findall('.//item'):
            message_elem = item.find('.//message')
            path_elem = item.find('.//path')
            severity_elem = item.find('.//severity')
            
            if message_elem is not None and message_elem.text:
                error_data = {
                    'diagnostics': message_elem.text.strip(),
                    'location': path_elem.text.strip() if path_elem is not None and path_elem.text else '',
                    'test': '',
                    'details': []
                }
                
                severity = severity_elem.text.lower() if severity_elem is not None and severity_elem.text else 'error'
                if 'error' in severity:
                    results['errors'].append(error_data)
                elif 'warning' in severity:
                    results['warnings'].append(error_data)
                else:
                    results['information'].append(error_data)
        
        # METHOD 4: Iterate all elements looking for common patterns
        if not results['errors'] and not results['warnings']:
            for elem in root.iter():
                tag_lower = elem.tag.lower().replace('{http://purl.oclc.org/dsdl/svrl}', '').replace('{http://gazelle.ihe.net/report}', '')
                
                # Look for elements with error/warning/info in tag name
                if ('error' in tag_lower or 'failed' in tag_lower) and elem.text and len(elem.text.strip()) > 2:
                    results['errors'].append({
                        'diagnostics': elem.text.strip(),
                        'location': elem.get('location', '') or elem.get('path', ''),
                        'test': elem.get('test', ''),
                        'details': dict(elem.attrib)
                    })
                elif 'warning' in tag_lower and elem.text and len(elem.text.strip()) > 2:
                    results['warnings'].append({
                        'diagnostics': elem.text.strip(),
                        'location': elem.get('location', '') or elem.get('path', ''),
                        'test': elem.get('test', ''),
                        'details': dict(elem.attrib)
                    })
        
        # If still no results, save raw XML for debugging
        if not results['errors'] and not results['warnings'] and not results['information']:
            results['errors'].append({
                'diagnostics': 'Unable to parse validation results. Check Full Response tab for raw XML.',
                'location': '',
                'test': '',
                'details': {}
            })
        
        return results
        
    except Exception as e:
        print(f"\n⚠️  Error parsing XML: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'errors': [{'diagnostics': f'XML parsing failed: {str(e)}', 'location': '', 'test': ''}],
            'warnings': [],
            'information': [],
            'status': 'parse_error',
            'raw_xml': str(result_xml) if result_xml else ''
        }
        if warnings:
            print("\n⚠️  WARNINGS:")
            for i, warning in enumerate(warnings[:5], 1):  # Show first 5
                message = warning.find('.//message') or warning
                print(f"{i}. {message.text if hasattr(message, 'text') else str(message)}")
        
        # Overall result
        if len(errors) == 0:
            print("\n✅ VALIDATION PASSED")
        else:
            print(f"\n❌ VALIDATION FAILED ({len(errors)} errors)")
        
    except ET.ParseError as e:
        print(f"\n⚠️  Could not parse validation result XML: {e}")
        print("\nRaw result:")
        print(str(result_xml)[:500])  # Print first 500 chars
    except Exception as e:
        print(f"\n⚠️  Error parsing results: {str(e)}")
        print("\nRaw result:")
        print(str(result_xml)[:500])


def test_about_service(wsdl_url=CDA_WSDL):
    """Test the 'about' method to verify service connectivity"""
    print_section("Testing service connectivity")
    print(f"WSDL: {wsdl_url}")
    
    try:
        client = Client(wsdl_url)
        about_info = client.service.about()
        print(f"\n✓ Service is accessible")
        print(f"\nAbout:")
        print(about_info)
        return True
    except Exception as e:
        print(f"\n✗ Service unavailable: {str(e)}")
        return False


def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description='Test eHDSI Gazelle EVS validation services')
    parser.add_argument('--document', '-d', help='Path to XML document to validate')
    parser.add_argument('--validator', '-v', help='Validator name to use')
    parser.add_argument('--list-validators', '-l', action='store_true', help='List available validators')
    parser.add_argument('--wsdl', default=CDA_WSDL, help='WSDL endpoint URL')
    
    args = parser.parse_args()
    
    print_header(f"eHDSI Gazelle EVS Validation Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test service connectivity
    if not test_about_service(args.wsdl):
        print("\n⚠️  Service connectivity test failed. Check network connection.")
        return 1
    
    # List validators if requested
    if args.list_validators:
        list_available_validators(args.wsdl)
        return 0
    
    # Validate document if provided
    if args.document:
        if not args.validator:
            print("\n⚠️  No validator specified. Using default:")
            print(f"    {DEFAULT_VALIDATORS[0]}")
            args.validator = DEFAULT_VALIDATORS[0]
        
        validate_document(args.document, args.validator, args.wsdl)
    
    else:
        # Interactive mode: list validators and prompt for selection
        print("\n" + "="*80)
        print("No document specified. Available options:")
        print("="*80)
        print("\n1. List available validators (-l)")
        print("2. Validate a document (-d <path> -v <validator>)")
        print("\nExample commands:")
        print(f"  python {sys.argv[0]} -l")
        print(f"  python {sys.argv[0]} -d examples/patient_summary.xml -v \"eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)\"")
        print("\nFor help:")
        print(f"  python {sys.argv[0]} --help")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
