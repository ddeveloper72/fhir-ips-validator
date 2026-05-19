"""
CDA Document Type Detection

Detects CDA document type from templateId elements and recommends 
the appropriate Gazelle validator.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Optional, List

# eHDSI Template ID to Validator mapping
TEMPLATE_TO_VALIDATOR = {
    # Patient Summary
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.3': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'Patient Summary (PS)',
        'level': 'L3 - Full Content Validation'
    },
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.2': {
        'name': 'eHDSI - FRIENDLY CDA (L3) validation - Wave 8 (V8.0.0)',
        'type': 'Patient Summary (PS)',
        'level': 'L3 - Friendly Format'
    },
    
    # ePrescription
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.1': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'ePrescription (eP)',
        'level': 'L3 - Full Validation'
    },
    
    # eDispensation
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.2': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'eDispensation (eD)',
        'level': 'L3 - Full Validation'
    },
    
    # Hospital Discharge Report
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.4': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'Hospital Discharge Report (HDR)',
        'level': 'L3 - Full Validation'
    },
    
    # Laboratory Report
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.5': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'Laboratory Report (LR)',
        'level': 'L3 - Full Validation'
    },
    
    # Medical Imaging Report
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.6': {
        'name': 'eHDSI OrCD - Medical Imaging Report CDA (L3) validation - Wave 10 (V10.0.0)',
        'type': 'Medical Imaging Report (MIR)',
        'level': 'L3 - OrCD Validation'
    },
    
    # IHE PCC Templates (fallback)
    '1.3.6.1.4.1.19376.1.5.3.1.1.1': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'IHE PCC Medical Documents',
        'level': 'L3 - IHE Compliance'
    },
}


def find_best_validator_match(document_type: str, validation_level: str, available_validators: List[str], validation_mode: str = "strict") -> Optional[str]:
    """
    Find the best matching validator from available list
    
    Args:
        document_type: Detected document type (e.g., 'Patient Summary (PS)')
        validation_level: Validation level (e.g., 'L3 - Full Content Validation')
        available_validators: List of validator names from platform
        validation_mode: 'strict' (default) or 'permissive'
            - strict: Prioritize implementation-specific validators (epSOS, eHDSI Wave)
            - permissive: Prioritize generic validators (HL7 - CDA Release 2)
    
    Returns:
        Best matching validator name, or None if no match
    """
    print(f"\n🔍 find_best_validator_match called:")
    print(f"   document_type: {document_type}")
    print(f"   validation_level: {validation_level}")
    print(f"   validation_mode: {validation_mode}")
    print(f"   # validators: {len(available_validators)}")
    
    # Extract key terms for matching
    doc_keywords = []
    
    if 'Patient Summary' in document_type or '(PS)' in document_type:
        doc_keywords.extend(['Patient Summary', 'IPS'])
        # Note: Removed 'PS' as standalone keyword because it matches inside 'epSOS' causing false positives
    if 'ePrescription' in document_type or '(eP)' in document_type:
        doc_keywords.extend(['ePrescription', 'Prescription'])
    if 'eDispensation' in document_type or '(eD)' in document_type:
        doc_keywords.extend(['eDispensation', 'Dispensation'])
    if 'Hospital Discharge' in document_type or '(HDR)' in document_type:
        doc_keywords.extend(['Hospital Discharge', 'HDR', 'Discharge'])
    if 'Laboratory' in document_type or '(LR)' in document_type:
        doc_keywords.extend(['Laboratory', 'LR', 'Lab'])
    if 'Medical Imaging' in document_type or '(MIR)' in document_type:
        doc_keywords.extend(['Medical Imaging', 'MIR', 'Imaging'])
    
    # Extract validation level keywords
    level_keywords = []
    if 'L3' in validation_level:
        level_keywords.extend(['L3', 'Level 3'])
    elif 'L1' in validation_level:
        level_keywords.extend(['L1', 'Level 1'])
    
    # Add general eHDSI/CDA keywords (lower priority)
    doc_keywords.extend(['CDA'])
    
    print(f"   doc_keywords: {doc_keywords}")
    print(f"   level_keywords: {level_keywords}")
    
    # Scoring system (strict mode):
    # - Document type match (e.g., "Patient Summary"): +10
    # - Validation level match (e.g., "L3"): +5
    # - eHDSI platform: +8
    # - Wave version: +5
    # - Document-specific validator: +10 (e.g., "Patient Summary validation" vs generic "PIVOT")
    # - OrCD validators: +5
    # - PIVOT/FRIENDLY: +5
    # - epSOS platform: +8
    # - Generic CDA: +2
    #
    # Example scores:
    # - "eHDSI - Patient Summary validation - Wave 7": 10+8+5+10 = 33 points ✅
    # - "eHDSI - PIVOT CDA (L3) validation - Wave 7": 2+5+8+5+5 = 25 points
    # - "epSOS - Patient Summary Pivot": 10+8+5 = 23 points
    
    # Score each validator
    best_match = None
    best_score = 0
    debug_scores = []  # For troubleshooting
    
    for validator in available_validators:
        score = 0
        validator_upper = validator.upper()
        match_details = []
        
        # Check document type keywords (high value)
        for keyword in doc_keywords:
            if keyword.upper() in validator_upper:
                # Prioritize specific document type matches over generic "CDA"
                if keyword.upper() == 'CDA':
                    # In permissive mode, boost generic CDA validators significantly
                    if validation_mode == "permissive" and "RELEASE 2" in validator_upper:
                        score += 20  # Strong preference for generic CDA R2
                        match_details.append("CDA R2 (Permissive):+20")
                    else:
                        score += 2
                        match_details.append("CDA:+2")
                else:
                    score += 10
                    match_details.append(f"{keyword}:+10")
        
        # Check validation level
        for keyword in level_keywords:
            if keyword.upper() in validator_upper:
                score += 5
                match_details.append(f"{keyword}:+5")
        
        # Boost eHDSI Wave validators (newer) - ONLY in strict mode
        if validation_mode == "strict" and 'EHDSI' in validator_upper:
            score += 8
            match_details.append("eHDSI:+8")
            
            # Further boost for Wave versions
            if any(wave in validator_upper for wave in ['WAVE 7', 'WAVE 8', 'WAVE 9', 'WAVE 10', 'V7.', 'V8.', 'V9.', 'V10.']):
                score += 5
                match_details.append("Wave:+5")
            
            # Extra boost for document-specific validators (e.g., "eHDSI - Patient Summary validation")
            # These are more specific than generic PIVOT/FRIENDLY validators
            if any(doc_type in validator_upper for doc_type in [
                'PATIENT SUMMARY VALIDATION',
                'EPRESCRIPTION VALIDATION',
                'EDISPENSATION VALIDATION',
                'HOSPITAL DISCHARGE REPORT',
                'LABORATORY RESULT',
                'MEDICAL IMAGING REPORT',
                'MEDICAL IMAGES'
            ]):
                score += 10
                match_details.append("Doc-specific:+10")
            
            # Boost OrCD document validators (also document-specific)
            if 'ORCD' in validator_upper:
                score += 5
                match_details.append("OrCD:+5")
        
        # Boost epSOS validators (older but still valid for EHDS platform) - ONLY in strict mode
        if validation_mode == "strict" and 'EPSOS' in validator_upper:
            score += 8
            match_details.append("epSOS:+8")
        
        # Prefer PIVOT or FRIENDLY validators (both platforms) - ONLY in strict mode
        if validation_mode == "strict":
            if 'PIVOT' in validator_upper:
                score += 5
                match_details.append("PIVOT:+5")
            elif 'FRIENDLY' in validator_upper:
                score += 5
                match_details.append("FRIENDLY:+5")
        
        # Track for debugging
        debug_scores.append((validator, score, match_details))
        
        # Update best match
        if score > best_score:
            best_score = score
            best_match = validator
    
    # Debug output - always show top 10 matches
    print(f"\n   Top 10 scoring validators:")
    for val, sc, details in sorted(debug_scores, key=lambda x: x[1], reverse=True)[:10]:
        indicator = "→" if val == best_match else " "
        print(f"   {indicator} {sc:2d} points: {val}")
        if details:
            print(f"      ({', '.join(details)})")
    
    print(f"\n   Best match: {best_match} (score: {best_score})")
    print(f"   Threshold: score > 3")
    
    # Lower threshold to 3 to allow epSOS matches
    return best_match if best_score > 3 else None


def detect_cda_type(xml_content: str, available_validators: Optional[List[str]] = None, validation_mode: str = "strict") -> Dict[str, any]:
    """
    Detect CDA document type from templateId elements
    
    Args:
        xml_content: XML content as string or bytes
        available_validators: Optional list of validators from the platform
        validation_mode: 'strict' (default) or 'permissive'
            - strict: Recommend implementation-specific validators (epSOS, eHDSI Wave)
            - permissive: Recommend generic validators (HL7 - CDA Release 2)
    
    Returns:
        dict: {
            'template_ids': List of template IDs found,
            'recommended_validator': Recommended validator name,
            'document_type': Human-readable document type,
            'validation_level': Validation level description,
            'confidence': 'high'|'medium'|'low',
            'match_reason': Explanation of why this validator was chosen
        }
    """
    try:
        # Parse XML
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode('utf-8')
        
        # Handle namespaces
        root = ET.fromstring(xml_content)
        
        # Define namespace map
        namespaces = {
            'hl7': 'urn:hl7-org:v3',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Find all templateId elements
        template_ids = []
        
        # Check document-level templateIds
        for template_elem in root.findall('.//hl7:templateId', namespaces):
            root_attr = template_elem.get('root')
            if root_attr:
                template_ids.append(root_attr)
        
        # Also check without namespace (some CDAs don't use namespaces)
        if not template_ids:
            for template_elem in root.findall('.//templateId'):
                root_attr = template_elem.get('root')
                if root_attr:
                    template_ids.append(root_attr)
        
        # Remove duplicates while preserving order
        template_ids = list(dict.fromkeys(template_ids))
        
        # Find best match
        recommended_validator = None
        document_type = 'Unknown CDA Document'
        validation_level = 'Generic CDA R2 Validation'
        confidence = 'low'
        match_reason = 'Default fallback'
        
        # First, identify document type from templates
        for template_id in template_ids:
            if template_id in TEMPLATE_TO_VALIDATOR:
                validator_info = TEMPLATE_TO_VALIDATOR[template_id]
                document_type = validator_info['type']
                validation_level = validator_info['level']
                
                print(f"\n🔍 DEBUG: Template match found")
                print(f"   Template ID: {template_id}")
                print(f"   Document Type: {document_type}")
                print(f"   Validation Level: {validation_level}")
                print(f"   Mode: {validation_mode}")
                
                # If available validators list provided, try to find best match
                if available_validators:
                    print(f"   Available validators: {len(available_validators)}")
                    recommended_validator = find_best_validator_match(
                        document_type, 
                        validation_level,
                        available_validators,
                        validation_mode
                    )
                    print(f"   find_best_validator_match returned: {recommended_validator}")
                    if recommended_validator:
                        confidence = 'high'
                        # Determine platform and mode
                        if validation_mode == "permissive" and "Release 2" in recommended_validator:
                            platform = 'Generic CDA R2 (Permissive)'
                            match_reason = f'Permissive mode: Using generic CDA R2 validator for {document_type}'
                        elif 'epSOS' in recommended_validator:
                            platform = 'epSOS'
                            match_reason = f'Matched {document_type} to {platform} validator (Strict mode)'
                        elif 'eHDSI' in recommended_validator:
                            platform = 'eHDSI'
                            match_reason = f'Matched {document_type} to {platform} validator (Strict mode)'
                        else:
                            platform = 'Generic'
                            match_reason = f'Matched {document_type} to {platform} validator'
                        break
                else:
                    # Fall back to hardcoded name (for backward compatibility)
                    recommended_validator = validator_info['name']
                    confidence = 'high'
                    match_reason = 'Exact template match'
                    break
        
        # If no template match but we have validators, try pattern matching
        if not recommended_validator and available_validators:
            # In permissive mode, prefer generic CDA R2 validators
            if validation_mode == "permissive":
                for validator in available_validators:
                    if 'CDA Release 2' in validator or 'CDA R2' in validator:
                        recommended_validator = validator
                        confidence = 'high'
                        match_reason = 'Permissive mode: Generic CDA R2 validator'
                        break
            
            # In strict mode, check for eHDSI documents
            if not recommended_validator:
                for template_id in template_ids:
                    if template_id.startswith('1.3.6.1.4.1.12559.11.10'):
                        document_type = 'eHDSI Document'
                        validation_level = 'L3 - Full Validation'
                        
                        # Try to find L3 validator
                        for validator in available_validators:
                            if 'L3' in validator and ('PIVOT' in validator or 'FRIENDLY' in validator):
                                recommended_validator = validator
                                confidence = 'medium'
                                match_reason = 'Pattern match: eHDSI L3 validator'
                                break
                        break
        
        # Final fallback - find any CDA validator
        if not recommended_validator and available_validators:
            # Look for CDA Release 2 validator
            for validator in available_validators:
                if 'CDA Release 2' in validator or 'CDA R2' in validator:
                    recommended_validator = validator
                    confidence = 'low' if validation_mode == "strict" else 'medium'
                    match_reason = 'Fallback: Generic CDA R2 validator'
                    break
            
            # If still nothing, use first validator
            if not recommended_validator and available_validators:
                recommended_validator = available_validators[0]
                confidence = 'low'
                match_reason = 'Fallback: First available validator'
        
        # Absolute fallback (no validators list provided)
        if not recommended_validator:
            recommended_validator = 'HL7 - CDA Release 2'
            document_type = 'Generic CDA R2 Document'
            validation_level = 'Basic CDA R2 Structure'
            confidence = 'low'
            match_reason = 'Default: No validators available'
        
        return {
            'template_ids': template_ids,
            'recommended_validator': recommended_validator,
            'document_type': document_type,
            'validation_level': validation_level,
            'confidence': confidence,
            'match_reason': match_reason
        }
    
    except Exception as e:
        # Return fallback on error
        return {
            'template_ids': [],
            'recommended_validator': 'HL7 - CDA Release 2',
            'document_type': 'CDA Document (detection failed)',
            'validation_level': 'Basic CDA R2 Structure',
            'confidence': 'low',
            'error': str(e)
        }


def get_validator_categories() -> Dict[str, List[str]]:
    """
    Get validators organized by category for dropdown display
    
    Returns:
        dict: Categories mapped to validator lists
    """
    return {
        'eHDSI Wave 9 (Latest)': [
            'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
            'eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.1.0)',
            'eHDSI - FRIENDLY CDA (L3) validation - Wave 9 (V9.1.0)',
        ],
        'eHDSI Wave 8': [
            'eHDSI - FRIENDLY CDA (L3) validation - Wave 8 (V8.0.0)',
            'eHDSI - Patient Summary CDA validation (L3) - Wave 8 (V8.0.0)',
        ],
        'OrCD (Medical Imaging)': [
            'eHDSI OrCD - Medical Imaging Report CDA (L3) validation - Wave 10 (V10.0.0)',
        ],
        'Generic CDA': [
            'HL7 - CDA Release 2',
            'CDA - IHE PCC',
        ]
    }


if __name__ == '__main__':
    # Test with example files
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        with open(file_path, 'rb') as f:
            content = f.read()
        
        result = detect_cda_type(content)
        
        print(f"\n{'='*80}")
        print(f"CDA DOCUMENT TYPE DETECTION")
        print(f"{'='*80}")
        print(f"\nFile: {file_path}")
        print(f"\nDocument Type: {result['document_type']}")
        print(f"Validation Level: {result['validation_level']}")
        print(f"Confidence: {result['confidence'].upper()}")
        print(f"\nRecommended Validator:")
        print(f"  {result['recommended_validator']}")
        print(f"\nTemplate IDs Found:")
        for tid in result['template_ids']:
            print(f"  - {tid}")
        print(f"\n{'='*80}\n")
    else:
        print("Usage: python detect_cda_type.py <path_to_cda.xml>")
