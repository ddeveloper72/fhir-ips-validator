"""
Validate FHIR resources using EHDS Gazelle Matchbox

This module provides validation against IPS (International Patient Summary) profiles
using the EHDS Gazelle Matchbox FHIR validation service.
"""

import requests
import json
from typing import Dict, List, Any, Optional


# EHDS Gazelle Matchbox endpoint
MATCHBOX_BASE_URL = 'https://ehds.gazelle-platform.net/matchboxv3/fhir'

# IPS Profiles available for validation
IPS_PROFILES = {
    # Bundle profiles
    'Bundle (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips|2.0.0',
    'Bundle (IPS) 1.1.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips|1.1.0',
    'Bundle (IPS) - Latest': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips',
    
    # Individual resource profiles (2.0.0 versions)
    'AllergyIntolerance (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips|2.0.0',
    'Composition (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Composition-uv-ips|2.0.0',
    'Condition (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Condition-uv-ips|2.0.0',
    'Device (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Device-uv-ips|2.0.0',
    'DiagnosticReport (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/DiagnosticReport-uv-ips|2.0.0',
    'Immunization (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Immunization-uv-ips|2.0.0',
    'Medication (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Medication-uv-ips|2.0.0',
    'MedicationRequest (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/MedicationRequest-uv-ips|2.0.0',
    'MedicationStatement (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/MedicationStatement-uv-ips|2.0.0',
    'Observation - Pregnancy Status (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-pregnancy-status-uv-ips|2.0.0',
    'Observation - Alcohol Use (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-alcoholuse-uv-ips|2.0.0',
    'Observation - Tobacco Use (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-tobaccouse-uv-ips|2.0.0',
    'Observation - Lab/Pathology (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-results-laboratory-pathology-uv-ips|2.0.0',
    'Observation - Radiology (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Observation-results-radiology-uv-ips|2.0.0',
    'Organization (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Organization-uv-ips|2.0.0',
    'Patient (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Patient-uv-ips|2.0.0',
    'Practitioner (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Practitioner-uv-ips|2.0.0',
    'Procedure (IPS) 2.0.0': 'http://hl7.org/fhir/uv/ips/StructureDefinition/Procedure-uv-ips|2.0.0',
}

# Default profile for bundles
DEFAULT_BUNDLE_PROFILE = 'Bundle (IPS) 2.0.0'


def validate_fhir_with_matchbox(
    resource: Dict[str, Any],
    profile_name: str = DEFAULT_BUNDLE_PROFILE,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Validate a FHIR resource against an IPS profile using EHDS Gazelle Matchbox.
    
    Args:
        resource: FHIR resource (dict from JSON)
        profile_name: Name of the IPS profile to validate against (from IPS_PROFILES keys)
        timeout: Request timeout in seconds
        
    Returns:
        Dict with validation results:
        {
            'success': bool,
            'errors': List[Dict],
            'warnings': List[Dict],
            'information': List[Dict],
            'raw_response': Dict (OperationOutcome),
            'profile_url': str,
            'error_message': str (only if success=False)
        }
    """
    
    # Get profile URL
    profile_url = IPS_PROFILES.get(profile_name)
    if not profile_url:
        return {
            'success': False,
            'error_message': f'Unknown profile: {profile_name}',
            'errors': [],
            'warnings': [],
            'information': []
        }
    
    # Prepare request
    url = f'{MATCHBOX_BASE_URL}/$validate'
    params = {'profile': profile_url}
    headers = {'Content-Type': 'application/fhir+json'}
    
    try:
        # Submit validation request
        response = requests.post(
            url,
            params=params,
            json=resource,
            headers=headers,
            timeout=timeout
        )
        
        # Parse response
        if response.status_code == 200:
            operation_outcome = response.json()
            
            if operation_outcome.get('resourceType') != 'OperationOutcome':
                return {
                    'success': False,
                    'error_message': f'Unexpected response type: {operation_outcome.get("resourceType")}',
                    'errors': [],
                    'warnings': [],
                    'information': []
                }
            
            # Parse issues by severity
            issues = operation_outcome.get('issue', [])
            errors = []
            warnings = []
            information = []
            
            for issue in issues:
                severity = issue.get('severity', 'unknown')
                
                issue_data = {
                    'severity': severity,
                    'code': issue.get('code', 'unknown'),
                    'diagnostics': issue.get('diagnostics', 'No message'),
                    'location': issue.get('location', []),
                    'expression': issue.get('expression', [])
                }
                
                if severity == 'error' or severity == 'fatal':
                    errors.append(issue_data)
                elif severity == 'warning':
                    warnings.append(issue_data)
                elif severity == 'information':
                    information.append(issue_data)
            
            return {
                'success': True,
                'errors': errors,
                'warnings': warnings,
                'information': information,
                'raw_response': operation_outcome,
                'profile_url': profile_url,
                'profile_name': profile_name
            }
        else:
            # Handle error response
            try:
                error_outcome = response.json()
                error_msg = error_outcome.get('issue', [{}])[0].get('diagnostics', 'Unknown error')
            except:
                error_msg = f'HTTP {response.status_code}: {response.text[:200]}'
            
            return {
                'success': False,
                'error_message': error_msg,
                'errors': [],
                'warnings': [],
                'information': []
            }
            
    except requests.Timeout:
        return {
            'success': False,
            'error_message': f'Validation timeout after {timeout} seconds',
            'errors': [],
            'warnings': [],
            'information': []
        }
    except Exception as e:
        return {
            'success': False,
            'error_message': f'Validation error: {str(e)}',
            'errors': [],
            'warnings': [],
            'information': []
        }


def get_available_profiles() -> List[str]:
    """Get list of available IPS profile names."""
    return list(IPS_PROFILES.keys())


def get_profile_url(profile_name: str) -> Optional[str]:
    """Get the full URL for a profile name."""
    return IPS_PROFILES.get(profile_name)


def detect_resource_type(resource: Dict[str, Any]) -> Optional[str]:
    """
    Detect the FHIR resource type and recommend an appropriate profile.
    
    Args:
        resource: FHIR resource (dict from JSON)
        
    Returns:
        Recommended profile name, or None if no recommendation
    """
    resource_type = resource.get('resourceType', '')
    
    # For bundles, always recommend Bundle profile
    if resource_type == 'Bundle':
        return DEFAULT_BUNDLE_PROFILE
    
    # For individual resources, try to find matching profile
    for profile_name, profile_url in IPS_PROFILES.items():
        if resource_type in profile_name:
            return profile_name
    
    return None
