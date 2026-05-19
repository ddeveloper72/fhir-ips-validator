"""
FHIR IPS Bundle Validator - Streamlit Web UI

This is a web interface for validating FHIR bundles and CDA documents using:
- Azure FHIR Service (REST API)
- eHDSI Gazelle (SOAP) - Wave 7-10, Cross-border eHealth
- EHDS Gazelle (SOAP) - Modern HL7 EU standards (IPS, EU-EPS)

STREAMLIT BASICS:
- st.title() = Big heading
- st.write() = Display text/data
- st.sidebar = Left sidebar for controls
- st.file_uploader() = File upload widget
- st.button() = Clickable button
- st.json() = Display JSON prettily
- st.success/error/warning = Colored message boxes
"""

import os
import sys
import json
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv
import time
import traceback
import threading

# Add scripts directory to path so we can import validation functions
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
API_TIMEOUT_SECONDS = 60
CACHE_DURATION_SECONDS = 3600  # 1 hour

# Import validation functions from existing scripts
try:
    from validate_with_azure_fhir import (
        get_azure_fhir_token, 
        validate_with_azure_fhir,
        parse_operation_outcome
    )
    AZURE_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Azure FHIR validation not available: {e}")
    AZURE_AVAILABLE = False

try:
    from validate_with_matchbox import (
        validate_fhir_with_matchbox,
        get_available_profiles,
        detect_resource_type,
        DEFAULT_BUNDLE_PROFILE
    )
    MATCHBOX_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ EHDS Matchbox validation not available: {e}")
    MATCHBOX_AVAILABLE = False

try:
    from test_evs_validation import list_available_validators, validate_document
    from detect_cda_type import detect_cda_type, get_validator_categories
    from zeep import Client
    GAZELLE_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Gazelle EVS validation not available: {e}")
    GAZELLE_AVAILABLE = False


# ============================================================================
# HELPER FUNCTIONS - Validation & Error Handling
# ============================================================================

import re

def validate_required_secrets():
    """
    Validate that all required secrets are configured.
    Returns dict with configuration status and missing keys.
    """
    required_secrets = {
        'azure': ['AZURE_FHIR_BASE_URL', 'AZURE_FHIR_CLIENT_ID', 'AZURE_FHIR_CLIENT_SECRET', 'AZURE_FHIR_TENANT_ID'],
        'ehdsi': ['EVS_API_KEY', 'EVS_BASE_URL'],
        'ehds': ['EHDS_GAZELLE_API_KEY', 'EHDS_GAZELLE_BASE_URL']
    }
    
    status = {}
    missing = {}
    
    for service, keys in required_secrets.items():
        missing_keys = [key for key in keys if not os.getenv(key)]
        status[service] = len(missing_keys) == 0
        if missing_keys:
            missing[service] = missing_keys
    
    return status, missing

def check_api_key_expiry():
    """
    Check if API keys are close to expiry.
    Returns dict with warnings for keys expiring in < 7 days.
    """
    warnings = []
    
    # Check eHDSI key expiry
    ehdsi_expiry = os.getenv('EVS_API_KEY_EXPIRY_DATE')
    if ehdsi_expiry:
        try:
            expiry_date = datetime.strptime(ehdsi_expiry.split()[0], '%m/%d/%y')
            days_until_expiry = (expiry_date - datetime.now()).days
            if days_until_expiry < 7:
                warnings.append(f"eHDSI API key expires in {days_until_expiry} days")
        except:
            pass
    
    # Check EHDS key expiry
    ehds_expiry = os.getenv('EHDS_GAZELLE_API_KEY_EXPIRY_DATE')
    if ehds_expiry:
        try:
            expiry_date = datetime.strptime(ehds_expiry.split()[0], '%m/%d/%y')
            days_until_expiry = (expiry_date - datetime.now()).days
            if days_until_expiry < 7:
                warnings.append(f"EHDS API key expires in {days_until_expiry} days")
        except:
            pass
    
    return warnings

def validate_file_size(file_obj) -> tuple:
    """
    Validate uploaded file size.
    Returns (is_valid: bool, size_bytes: int, error_message: str)
    """
    try:
        # Get file size
        if hasattr(file_obj, 'size'):
            size = file_obj.size
        else:
            content = file_obj.read()
            size = len(content)
            file_obj.seek(0)  # Reset
        
        if size == 0:
            return False, 0, "File is empty. Please upload a valid document."
        
        if size > MAX_FILE_SIZE_BYTES:
            size_mb = size / (1024 * 1024)
            return False, size, f"File too large ({size_mb:.1f}MB). Maximum size is {MAX_FILE_SIZE_MB}MB."
        
        return True, size, ""
    except Exception as e:
        return False, 0, f"Error reading file: {str(e)}"

def validate_json_format(content: str) -> tuple:
    """
    Validate JSON format and structure.
    Returns (is_valid: bool, data: dict, error_message: str)
    """
    try:
        data = json.loads(content)
        
        # Check if it's a FHIR resource
        if not isinstance(data, dict):
            return False, None, "Invalid JSON: Expected a JSON object, got array or primitive."
        
        if 'resourceType' not in data:
            return False, None, "Not a FHIR resource: Missing 'resourceType' field."
        
        return True, data, ""
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format at line {e.lineno}, column {e.colno}: {e.msg}"
    except Exception as e:
        return False, None, f"Error parsing JSON: {str(e)}"

def validate_xml_format(content: str) -> tuple:
    """
    Validate XML format and structure.
    Returns (is_valid: bool, error_message: str)
    """
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        return True, ""
    except ET.ParseError as e:
        return False, f"Invalid XML format at line {e.position[0]}: {e.msg}"
    except Exception as e:
        return False, f"Error parsing XML: {str(e)}"

def compute_file_hash(content: bytes) -> str:
    """
    Compute SHA-256 hash of file content for caching.
    """
    return hashlib.sha256(content).hexdigest()[:16]

def safe_api_call(func, *args, timeout=API_TIMEOUT_SECONDS, **kwargs):
    """
    Wrapper for API calls with timeout and error handling.
    Returns (success: bool, result: any, error_message: str)
    """
    import signal
    
    try:
        # Note: signal.alarm only works on Unix, for cross-platform use threading
        import threading
        
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            return False, None, f"API call timed out after {timeout} seconds. Please try again."
        
        if exception[0]:
            raise exception[0]
        
        return True, result[0], ""
    
    except ConnectionError as e:
        return False, None, f"Network error: Unable to connect to API. Please check your internet connection."
    except TimeoutError as e:
        return False, None, f"Request timed out. The service may be experiencing high load. Please try again."
    except Exception as e:
        error_msg = str(e)
        if 'rate limit' in error_msg.lower() or '429' in error_msg:
            return False, None, "Rate limit exceeded. Please wait 60 seconds before trying again."
        elif 'unauthorized' in error_msg.lower() or '401' in error_msg:
            return False, None, "Authentication failed. Please check your API credentials."
        elif 'forbidden' in error_msg.lower() or '403' in error_msg:
            return False, None, "Access denied. Your API key may have expired or lacks permissions."
        else:
            return False, None, f"API error: {error_msg}"


# ============================================================================
# HELPER FUNCTIONS - Matchbox Response Parsing
# ============================================================================

def parse_matchbox_diagnostic(diagnostics: str) -> dict:
    """
    Parse Matchbox diagnostic messages to extract human-readable information.
    
    Returns dict with:
    - summary: Short human-readable summary
    - details: Detailed explanation
    - fhir_paths: List of FHIR paths mentioned
    - profile_urls: List of profile URLs mentioned
    - sub_issues: List of individual issues if multiple
    """
    result = {
        'summary': '',
        'details': '',
        'fhir_paths': [],
        'profile_urls': [],
        'sub_issues': []
    }
    
    # Extract profile URLs
    profile_pattern = r'http://hl7\.org/fhir/[^\s\)]+(?:\|\d+\.\d+\.\d+)?'
    profile_urls = re.findall(profile_pattern, diagnostics)
    result['profile_urls'] = list(set(profile_urls))  # Unique URLs
    
    # Extract FHIR paths (Bundle.entry[33], resource.value, etc.)
    path_pattern = r'Bundle\.entry\[\d+\](?:\.[a-zA-Z]+)*|resource\.[a-zA-Z]+(?:\[[^\]]+\])?'
    fhir_paths = re.findall(path_pattern, diagnostics)
    result['fhir_paths'] = list(set(fhir_paths))  # Unique paths
    
    # Handle common message types
    if 'does not match any known slice' in diagnostics:
        result['summary'] = 'Element not matching expected slice'
        result['details'] = 'This element doesn\'t match any known slice defined in the profile. This may not be a problem if your use case allows additional elements.'
    
    elif 'Validation for profile' in diagnostics and 'Loaded packages' in diagnostics:
        # Informational message about validation context
        result['summary'] = 'Validation context loaded'
        # Extract profile version
        version_match = re.search(r'profile\s+([^\s]+)\s+\(([^)]+)\)', diagnostics)
        if version_match:
            profile_name = version_match.group(1).split('/')[-1]
            version = version_match.group(2)
            result['details'] = f'Using profile: {profile_name} ({version})'
        else:
            result['details'] = 'Validation configuration loaded successfully'
    
    elif 'Wrong Display Name' in diagnostics:
        # Extract the wrong and correct display names
        wrong_match = re.search(r"Wrong Display Name '([^']+)'", diagnostics)
        correct_match = re.search(r"Valid display is '([^']+)'", diagnostics)
        system_match = re.search(r'for ([^\s]+)\s', diagnostics)
        
        wrong_name = wrong_match.group(1) if wrong_match else 'unknown'
        correct_name = correct_match.group(1) if correct_match else 'unknown'
        system = system_match.group(1).split('/')[-1] if system_match else 'unknown system'
        
        result['summary'] = f'Display name should be "{correct_name}" not "{wrong_name}"'
        result['details'] = f'Terminology: {system}'
    
    elif 'Profile reference' in diagnostics or 'conformsTo' in diagnostics:
        result['summary'] = 'Profile reference mismatch'
        if 'does not match' in diagnostics:
            result['details'] = 'The resource profile reference doesn\'t match the expected profile for this Bundle slice'
        else:
            result['details'] = diagnostics[:200] + '...' if len(diagnostics) > 200 else diagnostics
    
    elif 'provided as bundle param' in diagnostics or 'Validate resource against' in diagnostics:
        result['summary'] = 'Validating nested resource'
        profile_match = re.search(r'profile\s+([^\s]+)', diagnostics)
        if profile_match:
            profile_name = profile_match.group(1).split('/')[-1]
            result['details'] = f'Checking resource against: {profile_name}'
        else:
            result['details'] = 'Nested resource validation in progress'
    
    elif 'value of type' in diagnostics.lower() or 'element does not match' in diagnostics.lower():
        result['summary'] = 'Element type or value mismatch'
        # Try to extract which element
        result['details'] = diagnostics[:300] + '...' if len(diagnostics) > 300 else diagnostics
    
    elif 'pattern' in diagnostics.lower() and 'defined in the profile' in diagnostics:
        result['summary'] = 'Pattern constraint not met'
        result['details'] = diagnostics[:300] + '...' if len(diagnostics) > 300 else diagnostics
    
    else:
        # Generic handling - take first sentence as summary
        sentences = re.split(r'[.!?]\s+', diagnostics)
        first_sentence = sentences[0] if sentences else diagnostics
        result['summary'] = first_sentence[:120] + ('...' if len(first_sentence) > 120 else '')
        result['details'] = diagnostics[:500] + ('...' if len(diagnostics) > 500 else '')
    
    # Split into sub-issues if message contains numbered issues (e.g., "1.) Bundle.entry[33]...")
    issue_pattern = r'\d+\.\)\s+Bundle\.entry\[\d+\]'
    if re.search(issue_pattern, diagnostics):
        # This is a multi-issue message
        parts = re.split(r'(\d+\.\)\s+Bundle\.entry\[\d+\])', diagnostics)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                issue_text = parts[i] + parts[i + 1]
                # Take first 150 chars of each sub-issue
                summary = issue_text[:150] + ('...' if len(issue_text) > 150 else '')
                result['sub_issues'].append(summary)
    
    return result


def render_matchbox_issue(issue: dict, issue_num: int, severity: str, expanded: bool = False):
    """Render a single Matchbox validation issue with improved formatting."""
    code = issue.get('code', 'unknown')
    diagnostics = issue.get('diagnostics', 'No details')
    location = issue.get('expression', issue.get('location', []))
    
    # Parse the diagnostic message
    parsed = parse_matchbox_diagnostic(diagnostics)
    
    # Create expander title
    severity_icon = {
        'error': '❌',
        'warning': '⚠️',
        'information': 'ℹ️'
    }.get(severity, '•')
    
    title = f"{severity_icon} {severity.title()} {issue_num}: {parsed['summary']}"
    
    with st.expander(title, expanded=expanded):
        # Show main details (not the full diagnostic, just parsed details)
        if parsed['details'] != diagnostics:  # If we parsed it nicely
            if severity == 'error':
                st.error(parsed['details'])
            elif severity == 'warning':
                st.warning(parsed['details'])
            else:
                st.info(parsed['details'])
        
        # Show FHIR paths if any
        if parsed['fhir_paths'] and len(parsed['fhir_paths']) <= 5:
            st.markdown("**📍 Affected elements:**")
            for path in parsed['fhir_paths']:
                st.code(path, language=None)
        
        # Show location from issue if available and not redundant
        if location and not parsed['fhir_paths']:
            location_str = ' → '.join(location) if isinstance(location, list) else str(location)
            if location_str:  # Only show if not empty
                st.markdown("**📍 Location:**")
                st.code(location_str, language=None)
        
        # Show profile URLs in a clean way
        if parsed['profile_urls'] and len(parsed['profile_urls']) <= 3:
            st.markdown("**🔗 Related Profiles:**")
            for url in parsed['profile_urls']:
                # Extract just the profile name from URL
                profile_name = url.split('/')[-1].split('|')[0]
                st.caption(f"• {profile_name}")
        
        # Show sub-issues if multiple
        if parsed['sub_issues']:
            st.markdown(f"**📋 {len(parsed['sub_issues'])} related issues detected**")
            for idx, sub in enumerate(parsed['sub_issues'][:5], 1):
                st.caption(f"{idx}. {sub}")
            if len(parsed['sub_issues']) > 5:
                st.caption(f"... and {len(parsed['sub_issues']) - 5} more")
        
        # Technical details in a nested expander (collapsed by default)
        with st.expander("🔧 Technical Details", expanded=False):
            st.markdown(f"**Issue Code:** `{code}`")
            
            if parsed['profile_urls']:
                st.markdown("**Full Profile URLs:**")
                for url in parsed['profile_urls']:
                    st.text(url)
            
            # Full diagnostic message (for debugging)
            st.markdown("**Full Diagnostic Message:**")
            st.text(diagnostics)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
# This sets the page title, icon, and layout
# 'wide' makes it use full screen width
st.set_page_config(
    page_title="FHIR IPS Validator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STARTUP VALIDATION
# ============================================================================
# Check required secrets configuration
config_status, missing_keys = validate_required_secrets()

# Show warnings for missing configurations (don't block app)
if missing_keys:
    st.warning("⚠️ Some validation services are not configured:")
    for service, keys in missing_keys.items():
        st.caption(f"**{service.upper()}**: Missing {', '.join(keys)}")
    st.caption("Add these to your `.streamlit/secrets.toml` or `.env` file to enable all validators.")

# Check API key expiry
expiry_warnings = check_api_key_expiry()
if expiry_warnings:
    for warning in expiry_warnings:
        st.warning(f"⚠️ {warning}")


# ============================================================================
# TITLE & DESCRIPTION
# ============================================================================
st.title("🏥 FHIR IPS Bundle Validator")
st.markdown("""
Validate FHIR R4 International Patient Summary (IPS) bundles and CDA documents using:
- **Azure FHIR Service** - REST API validation with Azure Health Data Services
- **eHDSI Gazelle** - SOAP-based CDA validation for eHDSI Wave 7-10 compliance
- **EHDS Gazelle** - Modern HL7 EU standards (IPS, EU-EPS, EU Base & Core)
""")

st.divider()  # Horizontal line


# ============================================================================
# SIDEBAR - Configuration & Settings
# ============================================================================
# st.sidebar creates a left sidebar for navigation/settings
st.sidebar.header("⚙️ Configuration")

# Check if credentials are configured
azure_configured = bool(os.getenv('AZURE_FHIR_BASE_URL'))
ehdsi_configured = bool(os.getenv('EVS_API_KEY'))
ehds_configured = bool(os.getenv('EHDS_GAZELLE_API_KEY'))

# Show configuration status
st.sidebar.subheader("🔐 Authentication Status")
if azure_configured:
    st.sidebar.success("✅ Azure FHIR configured")
else:
    st.sidebar.warning("⚠️ Azure FHIR not configured")
    st.sidebar.caption("Set AZURE_FHIR_BASE_URL in .env")

if ehdsi_configured:
    st.sidebar.success("✅ eHDSI Gazelle configured")
else:
    st.sidebar.warning("⚠️ eHDSI Gazelle not configured")
    st.sidebar.caption("Set EVS_API_KEY in .env")

if ehds_configured:
    st.sidebar.success("✅ EHDS Gazelle configured")
else:
    st.sidebar.warning("⚠️ EHDS Gazelle not configured")
    st.sidebar.caption("Set EHDS_GAZELLE_API_KEY in .env")

st.sidebar.divider()

# Validator selection - radio button for choosing validator
st.sidebar.subheader("🎯 Select Validator")

# Determine default index based on recommended validator
validator_options = ["Azure FHIR", "EHDS Matchbox (FHIR IPS)", "Gazelle EVS"]
default_index = 0
if st.session_state.get('recommended_validator') in validator_options:
    default_index = validator_options.index(st.session_state['recommended_validator'])

validator_choice = st.sidebar.radio(
    "Choose validation service:",
    options=validator_options,
    index=default_index,
    help="Azure FHIR/Matchbox for FHIR R4 JSON bundles, Gazelle EVS for CDA XML documents"
)

# IPS Profile selector for EHDS Matchbox
ips_profile = None
if validator_choice == "EHDS Matchbox (FHIR IPS)":
    st.sidebar.divider()
    st.sidebar.subheader("📋 IPS Profile")
    
    available_profiles = get_available_profiles()
    
    ips_profile = st.sidebar.selectbox(
        "Choose IPS profile:",
        options=available_profiles,
        index=available_profiles.index(DEFAULT_BUNDLE_PROFILE) if DEFAULT_BUNDLE_PROFILE in available_profiles else 0,
        help="Bundle (IPS) for complete patient summaries, or specific resource profiles for individual FHIR resources"
    )
    
    st.sidebar.info("""
    **IPS Validation** 📋
    - Bundle (IPS): For complete patient summaries
    - Individual profiles: For specific FHIR resources
    - Uses HL7 International Patient Summary standard
    - Validates structure, terminology, and cardinality
    """)

# Platform selection for Gazelle EVS
gazelle_platform = None
validation_mode = None
if validator_choice == "Gazelle EVS":
    st.sidebar.divider()
    st.sidebar.subheader("🌐 Gazelle Platform")
    gazelle_platform = st.sidebar.radio(
        "Choose Gazelle platform:",
        options=["eHDSI Gazelle", "EHDS Gazelle"],
        index=0,
        help="eHDSI for CDA Wave 7-10, EHDS for modern HL7 EU standards"
    )
    
    # Validation mode selector
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Validation Mode")
    validation_mode = st.sidebar.radio(
        "Choose validation strictness:",
        options=["Strict (Recommended)", "Permissive (Basic Structure)"],
        index=0,
        help="""Strict: Full compliance checking with implementation guide-specific validators.
Permissive: Basic CDA R2 structure validation - more lenient, higher pass rate."""
    )
    
    # Show mode explanation
    if validation_mode == "Strict (Recommended)":
        st.sidebar.info("""
        **Strict Mode** 🔍
        - Uses implementation-specific validators (epSOS, eHDSI Wave 7-10)
        - Catches all compliance issues
        - May fail documents with minor issues
        - **Recommended for:** Production validation, conformance testing
        """)
    else:
        st.sidebar.warning("""
        **Permissive Mode** ✅
        - Uses generic HL7 CDA Release 2 validator
        - Checks basic structure only
        - Higher pass rate
        - **Recommended for:** Quick structure checks, development
        
        ⚠️ **Note:** Passing this doesn't guarantee production-readiness
        """)

# Show validator info
if validator_choice == "Azure FHIR":
    st.sidebar.info("""
    **Azure FHIR Service**
    - ✅ FHIR R4 bundles (JSON only)
    - ❌ Cannot validate CDA/XML
    - REST API-based
    - Fast validation (<5 seconds)
    - **Use with:** Diana Ferreira Bundle, Patrick Murphy Bundle
    
    💡 Upload an XML file to auto-switch to Gazelle
    """)
elif validator_choice == "EHDS Matchbox (FHIR IPS)":
    st.sidebar.info("""
    **EHDS Matchbox (IPS Validator)**
    - ✅ FHIR R4 bundles (JSON only)
    - ✅ IPS (International Patient Summary) profiles
    - ✅ HL7 UV IPS 1.1.0 and 2.0.0
    - ❌ Cannot validate CDA/XML
    - REST API-based
    - Fast validation (~10 seconds)
    - **Use with:** Diana Ferreira Bundle, Patrick Murphy Bundle
    
    💡 Upload an XML file to auto-switch to Gazelle EVS
    """)
else:
    if gazelle_platform == "eHDSI Gazelle":
        st.sidebar.info("""
        **eHDSI Gazelle (Original)**
        - ✅ CDA Wave 7-10 validation (XML)
        - ✅ Cross-border eHealth (NCPeH)
        - ✅ eHDSI L1/L3 compliance
        - SOAP-based (10-30 seconds)
        - **URL:** gazelle.ehdsi.eu
        - **Use with:** eHDSI CDAs, Wave 7-10 documents
        
        💡 Upload a JSON file to auto-switch to Azure
        """)
    else:
        st.sidebar.info("""
        **EHDS Gazelle (New)**
        - ✅ HL7 EU standards (IPS, EU-EPS)
        - ✅ CDA validation (XML)
        - ✅ EU Base & Core profiles
        - SOAP-based (10-30 seconds)
        - **URL:** ehds.gazelle-platform.net
        - **Use with:** IPS, EU-EPS, HL7 EU documents
        
        💡 Upload a JSON file to auto-switch to Azure
        """)


# ============================================================================
# MAIN CONTENT AREA - File Upload
# ============================================================================
st.header("📤 Upload Document")

# Initialize session state for loaded files
if 'loaded_file_content' not in st.session_state:
    st.session_state['loaded_file_content'] = None
    st.session_state['loaded_file_name'] = None

# Initialize session state for validator auto-switching
if 'recommended_validator' not in st.session_state:
    st.session_state['recommended_validator'] = 'Azure FHIR'  # Default
if 'show_validator_switch_message' not in st.session_state:
    st.session_state['show_validator_switch_message'] = False

# File uploader widget
# Returns a file-like object when user uploads a file
uploaded_file = st.file_uploader(
    label="Choose a FHIR bundle (JSON) or CDA document (XML)",
    type=['json', 'xml'],  # Accept only JSON and XML files
    help="Upload FHIR R4 IPS bundle (JSON) or CDA document (XML) - validator will auto-select"
)

# Display example file info
with st.expander("📝 Don't have a file? Use our examples"):
    st.write("**FHIR IPS Bundles (JSON)** - for Azure FHIR validation:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Load Diana Ferreira (43 entries)", use_container_width=True, key="diana"):
            # Load example file into session state
            example_path = Path('examples/Diana_Ferreira_bundle.json')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    with col2:
        if st.button("📁 Load Patrick Murphy (11 entries)", use_container_width=True, key="patrick"):
            # Load example file into session state
            example_path = Path('examples/Patrick_Murphy_bundle.json')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    st.divider()
    
    st.write("**CDA Documents (XML)** - for Gazelle EVS validation:")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📄 Diana Ferreira PS", use_container_width=True, key="diana_ps"):
            example_path = Path('examples/Diana_Ferreira_PS.xml')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    with col4:
        if st.button("📄 Patrick Murphy PS", use_container_width=True, key="patrick_ps"):
            example_path = Path('examples/Patrick_Murphy_PS.xml')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    st.write("**Validated Reference (Wave 7):**")
    
    if st.button("✅ 2-5678-W7 PS (PASSED)", use_container_width=True, key="w7_ref", help="Validated on Gazelle - OID: 1.3.6.1.4.1.12559.11.30.4.71007"):
        example_path = Path('examples/2-5678-W7_PS.xml')
        if example_path.exists():
            with open(example_path, 'rb') as f:
                st.session_state['loaded_file_content'] = f.read()
                st.session_state['loaded_file_name'] = example_path.name
            st.success(f"✅ Loaded {example_path.name}")
            st.rerun()
        else:
            st.error(f"❌ File not found: {example_path}")
    
    st.write("**Synthetic CDA Examples:**")
    
    col5, col6 = st.columns(2)
    
    with col5:
        if st.button("📄 Patient Summary CDA", use_container_width=True, key="ps_cda"):
            example_path = Path('examples/patient_summary_cda.xml')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    with col6:
        if st.button("📄 Hospital Discharge CDA", use_container_width=True, key="hd_cda"):
            example_path = Path('examples/hospital_discharge_cda.xml')
            if example_path.exists():
                with open(example_path, 'rb') as f:
                    st.session_state['loaded_file_content'] = f.read()
                    st.session_state['loaded_file_name'] = example_path.name
                st.success(f"✅ Loaded {example_path.name}")
                st.rerun()
            else:
                st.error(f"❌ File not found: {example_path}")
    
    st.caption("💡 Or use the file uploader above to browse and select any file. **Tip:** The validator will auto-switch based on file type (JSON → Azure, XML → Gazelle).")


# ============================================================================
# FILE PROCESSING & VALIDATION
# ============================================================================

# Determine which file to process (uploaded or loaded example)
file_to_process = None
file_name = None

if uploaded_file is not None:
    # User uploaded a file through the widget
    file_to_process = uploaded_file
    file_name = uploaded_file.name
    # Clear any loaded example when new file is uploaded
    st.session_state['loaded_file_content'] = None
    st.session_state['loaded_file_name'] = None
elif st.session_state['loaded_file_content'] is not None:
    # Example file was loaded via button
    from io import BytesIO
    file_to_process = BytesIO(st.session_state['loaded_file_content'])
    file_to_process.name = st.session_state['loaded_file_name']
    file_to_process.size = len(st.session_state['loaded_file_content'])
    file_name = st.session_state['loaded_file_name']

if file_to_process is not None:
    # Auto-switch validator based on file type
    if file_name.endswith('.json'):
        recommended = 'Azure FHIR'
        reason = 'JSON format → Azure FHIR (FHIR R4 bundles)'
    elif file_name.endswith('.xml'):
        recommended = 'Gazelle EVS'
        reason = 'XML format → Gazelle EVS (CDA documents)'
    else:
        recommended = st.session_state.get('recommended_validator', 'Azure FHIR')
        reason = None
    
    # Update recommendation if it changed
    if recommended != st.session_state.get('recommended_validator'):
        st.session_state['recommended_validator'] = recommended
        st.session_state['show_validator_switch_message'] = True
        st.session_state['switch_reason'] = reason
        st.rerun()
    
    # Show auto-switch notification (only once after switch)
    if st.session_state.get('show_validator_switch_message') and reason:
        st.info(f"💡 **Auto-selected:** {reason}")
        st.caption("You can manually change the validator in the sidebar if needed.")
        st.session_state['show_validator_switch_message'] = False
    
    # Show file details
    st.success(f"✅ File loaded: **{file_name}**")
    
    # Display file size
    if hasattr(file_to_process, 'size'):
        st.caption(f"File size: {file_to_process.size:,} bytes")
    else:
        # Fallback for other file-like objects
        try:
            content = file_to_process.read()
            file_to_process.seek(0)  # Reset to beginning
            st.caption(f"File size: {len(content):,} bytes")
        except:
            st.caption("File size: Unknown")
    
    # Add clear button for loaded examples
    if st.session_state['loaded_file_content'] is not None:
        if st.button("🗑️ Clear and upload different file", type="secondary"):
            st.session_state['loaded_file_content'] = None
            st.session_state['loaded_file_name'] = None
            st.rerun()
    
    # Read and parse the file
    try:
        # For JSON files
        if file_name.endswith('.json'):
            file_content = file_to_process.read().decode('utf-8')
            bundle_data = json.loads(file_content)
            
            # Display bundle info
            st.subheader("📋 Bundle Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Resource Type", bundle_data.get('resourceType', 'Unknown'))
            with col2:
                entry_count = len(bundle_data.get('entry', []))
                st.metric("Entries", entry_count)
            with col3:
                bundle_type = bundle_data.get('type', 'Unknown')
                st.metric("Bundle Type", bundle_type)
            
            # Show bundle preview in expandable section
            with st.expander("👁️ Preview Bundle JSON", expanded=False):
                st.json(bundle_data)
        
        else:  # XML files
            file_content = file_to_process.read().decode('utf-8')
            st.info("📄 XML document loaded (CDA format)")
            
            # Try to extract basic info from CDA
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(file_content)
                
                # Extract CDA document info
                col1, col2, col3 = st.columns(3)
                
                # Namespace for CDA
                ns = {'cda': 'urn:hl7-org:v3'}
                
                with col1:
                    title_elem = root.find('.//cda:title', ns)
                    title = title_elem.text if title_elem is not None else 'Unknown'
                    st.metric("Document Type", title)
                
                with col2:
                    code_elem = root.find('.//cda:code[@codeSystem]', ns)
                    if code_elem is not None:
                        code = code_elem.get('displayName', code_elem.get('code', 'Unknown'))
                        st.metric("Code", code)
                    else:
                        st.metric("Code", "Unknown")
                
                with col3:
                    effective_time = root.find('.//cda:effectiveTime[@value]', ns)
                    if effective_time is not None:
                        time_value = effective_time.get('value', 'Unknown')
                        st.metric("Effective Time", time_value[:8] if len(time_value) >= 8 else time_value)
                    else:
                        st.metric("Effective Time", "Unknown")
                
            except Exception as e:
                st.caption(f"Could not parse CDA metadata: {e}")
            
            with st.expander("👁️ Preview XML"):
                st.code(file_content[:2000] + "..." if len(file_content) > 2000 else file_content, language="xml")
        
        st.divider()
        
        # ====================================================================
        # VALIDATION BUTTON & RESULTS
        # ====================================================================
        st.header("🔍 Validation")
        
        # Big validation button
        validate_button = st.button(
            "🚀 Validate Bundle",
            type="primary",  # Makes it blue and prominent
            use_container_width=True
        )
        
        if validate_button:
            # Store validation timestamp
            st.session_state['validation_date'] = datetime.now().isoformat()
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                tmp_file.write(file_content)
                tmp_path = tmp_file.name
            
            try:
                # Show spinner while validating
                with st.spinner(f"⏳ Validating with {validator_choice}..."):
                    
                    # ========================================================
                    # AZURE FHIR VALIDATION
                    # ========================================================
                    if validator_choice == "Azure FHIR":
                        if not AZURE_AVAILABLE:
                            st.error("❌ Azure FHIR validation not available. Check configuration.")
                        elif not file_name.endswith('.json'):
                            st.warning("⚠️ Azure FHIR requires FHIR bundles in JSON format.")
                            st.info("""
                            **Try one of the FHIR bundle examples:**
                            - Diana Ferreira Bundle
                            - Patrick Murphy Bundle
                            
                            Or switch to **Gazelle EVS** validator in the sidebar for CDA/XML documents.
                            """)
                        else:
                            # Call the validation function from our existing script
                            result = validate_with_azure_fhir(tmp_path)
                            
                            if result:
                                st.success("✅ Validation completed!")
                                
                                # Display results in tabs
                                tab1, tab2, tab3 = st.tabs(["📊 Summary", "📄 Full Response", "📥 Download"])
                                
                                with tab1:
                                    # Parse and display validation results
                                    error_count = len(result.get('errors', []))
                                    warning_count = len(result.get('warnings', []))
                                    info_count = len(result.get('information', []))
                                    
                                    # Show summary metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("❌ Errors", error_count)
                                    with col2:
                                        st.metric("⚠️ Warnings", warning_count)
                                    with col3:
                                        st.metric("ℹ️ Info", info_count)
                                    
                                    st.divider()
                                    
                                    # Overall status
                                    if error_count == 0:
                                        st.success("🎉 **Validation passed!** No errors found.")
                                    else:
                                        st.error(f"❌ **Validation failed** - {error_count} error(s) found")
                                    
                                    # Show detailed issues
                                    if error_count > 0:
                                        st.subheader("❌ Errors")
                                        for i, error in enumerate(result['errors'], 1):
                                            code = error.get('code', 'unknown')
                                            diagnostics = error.get('diagnostics', 'No details')
                                            details_text = error.get('details_text', '')
                                            
                                            with st.expander(f"❌ Error {i}: {code}", expanded=True):
                                                # Main diagnostic message
                                                st.error(f"**Issue:** {diagnostics}")
                                                
                                                # Additional details if available
                                                if details_text and details_text != diagnostics:
                                                    st.write(f"**Details:** {details_text}")
                                                
                                                # Show location path
                                                if error.get('expression'):
                                                    st.code(' → '.join(error['expression']), language='text')
                                                    st.caption("📍 FHIR Path to the issue")
                                                
                                                # Show coding details if available
                                                if error.get('details_coding'):
                                                    with st.expander("🔍 Technical Details", expanded=False):
                                                        for coding in error['details_coding']:
                                                            st.json(coding)
                                    
                                    if warning_count > 0:
                                        st.subheader("⚠️ Warnings")
                                        for i, warning in enumerate(result['warnings'], 1):
                                            code = warning.get('code', 'unknown')
                                            diagnostics = warning.get('diagnostics', 'No details')
                                            details_text = warning.get('details_text', '')
                                            
                                            with st.expander(f"⚠️ Warning {i}: {code}"):
                                                # Main diagnostic message
                                                st.warning(f"**Issue:** {diagnostics}")
                                                
                                                # Additional details if available
                                                if details_text and details_text != diagnostics:
                                                    st.write(f"**Details:** {details_text}")
                                                
                                                # Show location path
                                                if warning.get('expression'):
                                                    st.code(' → '.join(warning['expression']), language='text')
                                                    st.caption("📍 FHIR Path to the issue")
                                                
                                                # Show coding details if available
                                                if warning.get('details_coding'):
                                                    with st.expander("🔍 Technical Details", expanded=False):
                                                        for coding in warning['details_coding']:
                                                            st.json(coding)
                                    
                                    if info_count > 0:
                                        with st.expander(f"ℹ️ Information Messages ({info_count})", expanded=False):
                                            for i, info in enumerate(result['information'], 1):
                                                diagnostics = info.get('diagnostics', 'No details')
                                                
                                                # Clean up the message
                                                if diagnostics != 'All OK':
                                                    st.info(f"**{i}.** {diagnostics}")
                                                    
                                                    # Show path if available
                                                    if info.get('expression'):
                                                        st.caption(f"📍 Path: {' → '.join(info['expression'])}")
                                                else:
                                                    st.success(f"**{i}.** {diagnostics}")
                                
                                with tab2:
                                    st.subheader("Full FHIR OperationOutcome")
                                    st.json(result.get('operation_outcome', {}))
                                
                                with tab3:
                                    st.subheader("Download Results")
                                    result_json = json.dumps(result, indent=2)
                                    st.download_button(
                                        label="📥 Download Validation Results (JSON)",
                                        data=result_json,
                                        file_name=f"validation_result_{file_name}",
                                        mime="application/json"
                                    )
                            else:
                                st.error("❌ Validation failed. Check authentication and configuration.")
                    
                    # ========================================================
                    # EHDS MATCHBOX (FHIR IPS) VALIDATION
                    # ========================================================
                    elif validator_choice == "EHDS Matchbox (FHIR IPS)":
                        if not MATCHBOX_AVAILABLE:
                            st.error("❌ EHDS Matchbox validation not available. Check configuration.")
                        elif not file_name.endswith('.json'):
                            st.warning("⚠️ EHDS Matchbox requires FHIR bundles in JSON format.")
                            st.info("""
                            **Try one of the FHIR bundle examples:**
                            - Diana Ferreira Bundle
                            - Patrick Murphy Bundle
                            
                            Or switch to **Gazelle EVS** validator in the sidebar for CDA/XML documents.
                            """)
                        else:
                            # Parse JSON content
                            import json
                            resource = json.loads(file_content)
                            
                            # Call validation function
                            result = validate_fhir_with_matchbox(resource, ips_profile)
                            
                            if result.get('success'):
                                st.success("✅ Validation completed!")
                                
                                # Display results in tabs
                                tab1, tab2, tab3 = st.tabs(["📊 Summary", "📄 Full Response", "📥 Download"])
                                
                                with tab1:
                                    # Parse validation results
                                    error_count = len(result.get('errors', []))
                                    warning_count = len(result.get('warnings', []))
                                    info_count = len(result.get('information', []))
                                    
                                    # Show summary metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("❌ Errors", error_count)
                                    with col2:
                                        st.metric("⚠️ Warnings", warning_count)
                                    with col3:
                                        st.metric("ℹ️ Info", info_count)
                                    
                                    st.divider()
                                    
                                    # Show profile info
                                    st.info(f"📋 **Profile:** {result.get('profile_name')}\n\n🔗 **URL:** `{result.get('profile_url')}`")
                                    
                                    # Overall status
                                    if error_count == 0:
                                        st.success("🎉 **Validation passed!** No errors found.")
                                    else:
                                        st.error(f"❌ **Validation failed** - {error_count} error(s) found")
                                    
                                    # Show detailed issues
                                    if error_count > 0:
                                        st.subheader("❌ Errors")
                                        for i, error in enumerate(result['errors'], 1):
                                            render_matchbox_issue(error, i, 'error', expanded=True)
                                    
                                    if warning_count > 0:
                                        st.subheader("⚠️ Warnings")
                                        for i, warning in enumerate(result['warnings'], 1):
                                            render_matchbox_issue(warning, i, 'warning', expanded=False)
                                    
                                    if info_count > 0:
                                        st.subheader("ℹ️ Information")
                                        # Only show first 3 info messages expanded, rest collapsed
                                        for i, info in enumerate(result['information'], 1):
                                            render_matchbox_issue(info, i, 'information', expanded=(i <= 3))
                                
                                with tab2:
                                    st.subheader("📄 Full OperationOutcome")
                                    st.json(result['raw_response'])
                                
                                with tab3:
                                    # Prepare downloadable JSON
                                    result_json = json.dumps(result['raw_response'], indent=2)
                                    st.download_button(
                                        label="📥 Download Validation Results (JSON)",
                                        data=result_json,
                                        file_name=f"matchbox_validation_{file_name}",
                                        mime="application/json"
                                    )
                            else:
                                st.error(f"❌ Validation failed: {result.get('error_message', 'Unknown error')}")
                    
                    # ========================================================
                    # GAZELLE EVS VALIDATION
                    # ========================================================
                    else:  # Gazelle EVS
                        if not GAZELLE_AVAILABLE:
                            st.error("❌ Gazelle EVS validation not available. Check configuration.")
                        elif not file_name.endswith('.xml'):
                            st.warning("⚠️ Gazelle EVS requires CDA documents in XML format.")
                            st.info("""
                            **Try one of the CDA examples:**
                            - Patient Summary CDA
                            - Hospital Discharge CDA
                            
                            Click the example buttons above to load a CDA document.
                            """)
                        else:
                            try:
                                # Determine WSDL endpoint based on selected platform
                                if gazelle_platform == "EHDS Gazelle":
                                    CDA_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
                                    platform_name = "EHDS Gazelle"
                                else:
                                    CDA_WSDL = 'https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
                                    platform_name = "eHDSI Gazelle"
                                
                                # Get list of available validators FIRST
                                validators = list_available_validators(CDA_WSDL)
                                
                                if validators:
                                    st.success(f"✅ Connected to {platform_name} - {len(validators)} validators available")
                                    
                                    # DEBUG: Show actual WSDL endpoint being used
                                    with st.expander("🔍 Debug Info", expanded=False):
                                        st.code(f"WSDL Endpoint: {CDA_WSDL}", language=None)
                                        st.caption(f"Platform Variable: {gazelle_platform}")
                                        st.caption(f"Platform Name: {platform_name}")
                                    
                                    # Determine validation mode (convert from UI text to simple string)
                                    mode = "strict" if "Strict" in validation_mode else "permissive"
                                    
                                    # NOW detect CDA type with available validators and mode
                                    cda_detection = detect_cda_type(file_content, validators, mode)
                                    
                                    # Show detection results
                                    mode_badge = "🔍 STRICT" if mode == "strict" else "✅ PERMISSIVE"
                                    st.info(f"📋 **Detected Document Type:** {cda_detection['document_type']} | {mode_badge}")
                                    st.caption(f"🎯 Confidence: {cda_detection['confidence'].upper()} | Validation: {cda_detection['validation_level']}")
                                    
                                    if cda_detection.get('match_reason'):
                                        st.caption(f"💡 Match: {cda_detection['match_reason']}")
                                    
                                    # Show platform-specific info
                                    if mode == "permissive":
                                        st.caption("ℹ️ Using generic CDA R2 validator - checks basic structure only")
                                    
                                    if cda_detection.get('template_ids'):
                                        with st.expander("🔍 Template IDs Found", expanded=False):
                                            for tid in cda_detection['template_ids'][:5]:  # Show first 5
                                                st.code(tid, language=None)
                                    
                                    # Create validator selection dropdown
                                    st.subheader("🎯 Select Validator")
                                    
                                    # Check if recommended validator exists in available list
                                    validator_name = cda_detection['recommended_validator']
                                    validator_exists = validator_name in validators
                                    
                                    if not validator_exists and validator_name:
                                        st.warning(f"⚠️ Recommended validator not available on {platform_name}. Using best match instead.")
                                        st.caption(f"Looking for: {validator_name}")
                                    
                                    col_auto, col_manual = st.columns([3, 1])
                                    
                                    with col_auto:
                                        # Recommended validator
                                        help_text = f"Auto-detected based on template IDs (confidence: {cda_detection['confidence']})"
                                        if cda_detection.get('match_reason'):
                                            help_text += f"\n{cda_detection['match_reason']}"
                                        
                                        use_recommended = st.checkbox(
                                            f"✅ Use recommended: **{validator_name}**",
                                            value=True,
                                            help=help_text
                                        )
                                    
                                    if not use_recommended:
                                        # Manual selection
                                        st.markdown("**Or choose manually:**")
                                        st.caption("💡 Match the Wave version to your document (e.g., Wave 7 docs → Wave 7 validator)")
                                        
                                        # Determine default index for selectbox
                                        if validator_exists:
                                            default_index = validators.index(validator_name)
                                        else:
                                            default_index = 0
                                        
                                        # Filter validators by category
                                        selected_validator = st.selectbox(
                                            "Available Validators:",
                                            options=validators,
                                            index=default_index,
                                            help="Choose a specific validator for your document type"
                                        )
                                        validator_name = selected_validator
                                    
                                    # Show selected validator
                                    st.info(f"🔧 **Validating with:** {validator_name}")
                                    
                                    # Validate the document
                                    result = validate_document(tmp_path, validator_name, CDA_WSDL)
                                    
                                    if result:
                                        st.success(f"✅ {platform_name} validation completed!")
                                        
                                        # Display results in tabs (same format as Azure FHIR)
                                        tab1, tab2, tab3 = st.tabs(["📊 Summary", "📄 Full Response", "📥 Download"])
                                        
                                        with tab1:
                                            # Parse and display validation results
                                            error_count = len(result.get('errors', []))
                                            warning_count = len(result.get('warnings', []))
                                            info_count = len(result.get('information', []))
                                            
                                            # Show summary metrics
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("❌ Errors", error_count)
                                            with col2:
                                                st.metric("⚠️ Warnings", warning_count)
                                            with col3:
                                                st.metric("ℹ️ Info", info_count)
                                            
                                            st.divider()
                                            
                                            # Show validation metadata and Gazelle link
                                            if result.get('metadata'):
                                                metadata = result['metadata']
                                                
                                                # Create info box with validation details
                                                st.subheader("📋 Validation Details")
                                                
                                                col_meta1, col_meta2 = st.columns(2)
                                                
                                                with col_meta1:
                                                    if metadata.get('ValidationDate'):
                                                        st.metric("📅 Date", metadata['ValidationDate'])
                                                    if metadata.get('ValidationTime'):
                                                        st.metric("🕐 Time", metadata['ValidationTime'])
                                                
                                                with col_meta2:
                                                    if metadata.get('ValidationEngine'):
                                                        st.metric("🔧 Engine", metadata['ValidationEngine'])
                                                    if metadata.get('ValidationEngineVersion'):
                                                        st.metric("📌 Version", metadata['ValidationEngineVersion'])
                                                
                                                st.caption(f"🎯 Validator: **{result.get('validator_name', 'Unknown')}**")
                                                
                                                # DEBUG: Show which endpoint was actually used
                                                with st.expander("🔍 Validation Endpoint", expanded=False):
                                                    st.code(f"WSDL: {CDA_WSDL}", language=None)
                                                    st.caption(f"Platform: {platform_name}")
                                            
                                            # Add link to Gazelle web UI for persistent reports
                                            if result.get('gazelle_web_url'):
                                                st.info(f"""
                                                🌐 **Want a persistent report?**
                                                
                                                This SOAP validation provides instant results but doesn't generate a permanent web report. 
                                                To get a shareable report URL, visit the Gazelle web interface:
                                                
                                                👉 [{platform_name} Validator]({result['gazelle_web_url']})
                                                
                                                Upload your document there to receive a permanent report link like:
                                                `https://{result['gazelle_web_url'].split('//')[1].split('/')[0]}/evs/report.seam?oid=...`
                                                """)
                                            
                                            st.divider()
                                            
                                            # Overall status - check Gazelle's official result
                                            gazelle_status = result.get('status', 'unknown').upper()
                                            
                                            if gazelle_status == 'PASSED':
                                                if warning_count > 0:
                                                    st.success(f"✅ **Validation PASSED** (with {warning_count} warning(s))")
                                                else:
                                                    st.success("🎉 **Validation PASSED!** No errors or warnings.")
                                            elif error_count == 0:
                                                st.success("🎉 **No errors found!**")
                                                if warning_count > 0:
                                                    st.info(f"ℹ️ Note: {warning_count} warning(s) present")
                                            else:
                                                st.error(f"❌ **Validation failed** - {error_count} error(s) found")
                                            
                                            # Display errors
                                            if error_count > 0:
                                                with st.expander(f"❌ Errors ({error_count})", expanded=True):
                                                    for i, error in enumerate(result['errors'], 1):
                                                        diagnostics = error.get('diagnostics', 'No details')
                                                        st.error(f"**{i}.** {diagnostics}")
                                                        
                                                        # Show location/path if available
                                                        if error.get('location'):
                                                            st.caption(f"📍 Location: {error['location']}")
                                                        
                                                        # Show test constraint if available
                                                        if error.get('test'):
                                                            st.caption(f"🔍 Test: {error['test']}")
                                            
                                            # Display warnings
                                            if warning_count > 0:
                                                with st.expander(f"⚠️ Warnings ({warning_count})", expanded=False):
                                                    for i, warning in enumerate(result['warnings'], 1):
                                                        diagnostics = warning.get('diagnostics', 'No details')
                                                        st.warning(f"**{i}.** {diagnostics}")
                                                        
                                                        # Show location/path if available
                                                        if warning.get('location'):
                                                            st.caption(f"📍 Location: {warning['location']}")
                                                        
                                                        # Show test constraint if available
                                                        if warning.get('test'):
                                                            st.caption(f"🔍 Test: {warning['test']}")
                                            
                                            # Display information messages
                                            if info_count > 0:
                                                with st.expander(f"ℹ️ Information Messages ({info_count})", expanded=False):
                                                    for i, info in enumerate(result['information'], 1):
                                                        diagnostics = info.get('diagnostics', 'No details')
                                                        st.info(f"**{i}.** {diagnostics}")
                                                        
                                                        # Show location if available
                                                        if info.get('location'):
                                                            st.caption(f"📍 Location: {info['location']}")
                                        
                                        with tab2:
                                            st.subheader("Full Gazelle EVS Report")
                                            
                                            # Show structured results
                                            st.json({
                                                'status': result.get('status', 'unknown'),
                                                'validator': validator_name,
                                                'errors': result.get('errors', []),
                                                'warnings': result.get('warnings', []),
                                                'information': result.get('information', [])
                                            })
                                            
                                            # Show raw XML in expander
                                            if result.get('raw_xml'):
                                                with st.expander("📄 Raw XML Report", expanded=False):
                                                    st.code(result['raw_xml'], language='xml')
                                        
                                        with tab3:
                                            st.subheader("Download Results")
                                            
                                            # Prepare downloadable JSON
                                            download_data = {
                                                'file_name': file_name,
                                                'validator': validator_name,
                                                'validation_date': st.session_state.get('validation_date', ''),
                                                'status': result.get('status', 'unknown'),
                                                'summary': {
                                                    'errors': error_count,
                                                    'warnings': warning_count,
                                                    'information': info_count
                                                },
                                                'errors': result.get('errors', []),
                                                'warnings': result.get('warnings', []),
                                                'information': result.get('information', [])
                                            }
                                            
                                            result_json = json.dumps(download_data, indent=2)
                                            st.download_button(
                                                label="📥 Download Validation Results (JSON)",
                                                data=result_json,
                                                file_name=f"gazelle_validation_{file_name.replace('.xml', '')}.json",
                                                mime="application/json"
                                            )
                                            
                                            # Download raw XML report
                                            if result.get('raw_xml'):
                                                st.download_button(
                                                    label="📥 Download Raw XML Report",
                                                    data=result['raw_xml'],
                                                    file_name=f"gazelle_report_{file_name.replace('.xml', '')}.xml",
                                                    mime="application/xml"
                                                )
                                    else:
                                        st.warning("⚠️ Validation completed but no result returned")
                                else:
                                    st.error("❌ Could not retrieve validator list from Gazelle EVS")
                            except Exception as e:
                                st.error(f"❌ Gazelle validation error: {e}")
                                st.exception(e)
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
    
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON file: {e}")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        st.exception(e)  # Show full error traceback

else:
    # Show helpful message when no file is uploaded
    st.info("👆 Upload a FHIR bundle to get started")
    
    st.markdown("""
    ### 🎯 Quick Start
    
    1. **Upload** your FHIR R4 IPS bundle (JSON) or CDA document (XML)
    2. **Select** validator (Azure FHIR or Gazelle EVS) in sidebar
    3. **Choose** Gazelle platform (eHDSI or EHDS) if using Gazelle
    4. **Click** "Validate Bundle" button
    5. **Review** validation results and download report
    
    ### 🌐 Validation Platforms
    
    #### Azure FHIR Service
    - ✅ FHIR R4 bundles (JSON)
    - ✅ REST API validation
    - ✅ Fast (<5 seconds)
    
    #### eHDSI Gazelle (Original)
    - ✅ CDA Wave 7-10 validation
    - ✅ Cross-border eHealth (NCPeH)
    - ✅ eHDSI L1/L3 compliance
    - 🌐 gazelle.ehdsi.eu
    
    #### EHDS Gazelle (New)
    - ✅ HL7 EU IPS validation
    - ✅ EU Patient Summary (EU-EPS)
    - ✅ EU Base & Core profiles
    - 🌐 ehds.gazelle-platform.net
    
    ### 📚 Resources
    
    - [FHIR IPS Documentation](http://hl7.org/fhir/uv/ips/)
    - [Azure Health Data Services](https://azure.microsoft.com/en-us/products/health-data-services)
    - [eHDSI Gazelle](https://gazelle.ehdsi.eu/)
    - [EHDS Gazelle](https://ehds.gazelle-platform.net/)
    - [HL7 EU Implementation Guide](http://hl7.eu/fhir/)
    """)


# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("Built with Streamlit 🎈 | FHIR R4 IPS Validator | May 2026")
