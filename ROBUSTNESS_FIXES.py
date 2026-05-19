# ============================================================================
# ROBUSTNESS IMPROVEMENTS FOR streamlit_app.py
# Add these functions and modifications to make the app more robust
# ============================================================================

# ADD THESE IMPORTS AT THE TOP (after existing imports):
import hashlib
import time
import traceback
import threading
from datetime import timedelta

# ADD THESE CONSTANTS AFTER load_dotenv():
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
API_TIMEOUT_SECONDS = 60
CACHE_DURATION_SECONDS = 3600  # 1 hour

# ============================================================================
# ADD THESE HELPER FUNCTIONS (before the existing parse_matchbox_diagnostic):
# ============================================================================

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
    Returns list of warnings for keys expiring in < 7 days.
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

def safe_api_call_wrapper(func, *args, timeout=API_TIMEOUT_SECONDS, **kwargs):
    """
    Wrapper for API calls with timeout and error handling.
    Returns (success: bool, result: any, error_message: str)
    """
    try:
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
# ADD AFTER st.set_page_config():
# ============================================================================

# Validate configuration at startup
config_status, missing_secrets = validate_required_secrets()
expiry_warnings = check_api_key_expiry()

# Show critical configuration warnings
if not any(config_status.values()):
    st.error("""
    🔴 **Critical: No validators configured!**
    
    Please add API credentials to your `.streamlit/secrets.toml` file or environment variables.
    See DEPLOYMENT_GUIDE.md for instructions.
    """)
    st.stop()

# Show expiry warnings
if expiry_warnings:
    for warning in expiry_warnings:
        st.warning(f"⚠️ {warning}")

# ============================================================================
# REPLACE FILE UPLOAD SECTION (around line 550):
# ============================================================================
# Find where you have: uploaded_file = st.file_uploader(...)
# ADD THIS VALIDATION AFTER GETTING file_to_process:

if file_to_process:
    # Validate file size
    is_valid_size, file_size, size_error = validate_file_size(file_to_process)
    
    if not is_valid_size:
        st.error(f"❌ {size_error}")
        if file_size > MAX_FILE_SIZE_BYTES:
            st.info(f"""
            **💡 Tip:** For large documents:
            - Try compressing the file
            - Remove unnecessary sections
            - Split into smaller batches
            
            Maximum file size: {MAX_FILE_SIZE_MB}MB
            """)
        st.stop()
    
    # Show file size info
    file_size_mb = file_size / (1024 * 1024)
    st.caption(f"File size: {file_size_mb:.2f} MB")
    
    # Read file content
    try:
        file_content = file_to_process.read().decode('utf-8')
        file_to_process.seek(0)  # Reset for later use
    except UnicodeDecodeError:
        st.error("❌ File encoding error. Please ensure the file is UTF-8 encoded.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()
    
    # Validate format based on file type
    if file_name.endswith('.json'):
        is_valid, data, error_msg = validate_json_format(file_content)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            st.info("""
            **💡 Tip:** Check your JSON file:
            - Use a JSON validator (jsonlint.com)
            - Ensure all quotes are properly closed
            - Check for trailing commas
            - Verify bracket/brace matching
            """)
            st.stop()
    
    elif file_name.endswith('.xml'):
        is_valid, error_msg = validate_xml_format(file_content)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            st.info("""
            **💡 Tip:** Check your XML file:
            - Ensure all tags are properly closed
            - Check for special characters that need escaping
            - Validate against CDA schema
            - Use an XML validator
            """)
            st.stop()

# ============================================================================
# WRAP API CALLS WITH ERROR HANDLING:
# ============================================================================
# Find your Azure FHIR validation section (around line 700)
# WRAP the validate_with_azure_fhir call like this:

# BEFORE:
#   result = validate_with_azure_fhir(file_content)

# AFTER:
with st.spinner("🔄 Validating with Azure FHIR (this may take up to 60 seconds)..."):
    try:
        success, result, error_msg = safe_api_call_wrapper(
            validate_with_azure_fhir,
            file_content,
            timeout=60
        )
        
        if not success:
            st.error(f"❌ Validation failed: {error_msg}")
            if "timeout" in error_msg.lower():
                st.info("""
                **💡 Timeout occurred. Possible causes:**
                - Large file size - try a smaller document
                - Azure service experiencing high load
                - Network connectivity issues
                
                **Try:**
                - Click 'Validate' again
                - Use a different validator
                - Try again in a few minutes
                """)
            st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        with st.expander("🔧 Technical Details"):
            st.code(traceback.format_exc())
        st.stop()

# Similar wrapping for Gazelle EVS calls (around line 850):
with st.spinner(f"🔄 Validating with {gazelle_platform} (this may take 30-60 seconds)..."):
    try:
        # Your existing validate_document call
        result = validate_document(temp_file_path, selected_validator, CDA_WSDL)
        
        if not result:
            st.error("❌ Validation returned no results. This may indicate:")
            st.info("""
            - API connectivity issues
            - Invalid validator selection
            - Unsupported document format
            
            **Try:**
            - Select a different validator
            - Check your document format
            - Try again in a moment
            """)
            st.stop()
    except Exception as e:
        st.error(f"❌ Validation failed: {str(e)}")
        if "timeout" in str(e).lower():
            st.info("The validation service is taking longer than expected. Please try again.")
        elif "connection" in str(e).lower():
            st.warning("Network connection issue. Please check your internet connection.")
        st.stop()

# ============================================================================
# ADD SESSION STATE CLEANUP:
# ============================================================================
# Add this at the beginning of your main validation logic:

if 'validation_in_progress' not in st.session_state:
    st.session_state['validation_in_progress'] = False

# Before starting validation:
if st.session_state['validation_in_progress']:
    st.warning("⏳ A validation is already in progress. Please wait...")
    st.stop()

# When starting validation:
st.session_state['validation_in_progress'] = True

# After validation completes (in finally block):
try:
    # ... validation code ...
    pass
finally:
    st.session_state['validation_in_progress'] = False
