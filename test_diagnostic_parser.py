"""Test the Matchbox diagnostic parser with real messages"""
import sys
sys.path.insert(0, '.')

# Import the parser function
import re

# Sample diagnostic messages from the screenshot
test_messages = [
    # Info 2 - the long slice matching message
    """This element does not match any known slice defined in the profile http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips|2.0.0 (this may not be a problem, but you should check that it's not intended to match a slice) Slice Info: 1.) Bundle.entry[33]: discriminator = true and (resource is Composition) and resource.conformsTo('http://hl7.org/fhir/uv/ips/StructureDefinition/Composition-uv-ips|2.0.0') = false, Bundle.entry[33]: discriminator = true and (resource is AllergyIntolerance) and resource.conformsTo('http://hl7.org/fhir/uv/ips/StructureDefinition/AllergyIntolerance-uv-ips') = false""",
    
    # Wrong display name warning
    """Wrong Display Name 'Subcutaneous route' for http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C38200. Valid display is 'HEMODIALYSIS' (for the language(s) 'en-US')""",
    
    # Validation context info
    """Validation for profile http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips|2.0.0 (2024-06-19T10:50:07-05:00). Loaded packages: hl7.fhir.r4.core#4.0.1, hl7.fhir.xver-extensions#0.1.0, hl7.terminology""",
    
    # Nested validation
    """Validate resource against profile http://hl7.org/fhir/uv/ips/StructureDefinition/Composition-uv-ips - provided as bundle param"""
]

def parse_matchbox_diagnostic(diagnostics: str) -> dict:
    """Parse Matchbox diagnostic messages (copied from streamlit_app.py)"""
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
    result['profile_urls'] = list(set(profile_urls))
    
    # Extract FHIR paths
    path_pattern = r'Bundle\.entry\[\d+\](?:\.[a-zA-Z]+)*|resource\.[a-zA-Z]+(?:\[[^\]]+\])?'
    fhir_paths = re.findall(path_pattern, diagnostics)
    result['fhir_paths'] = list(set(fhir_paths))
    
    # Handle common message types
    if 'does not match any known slice' in diagnostics:
        result['summary'] = 'Element not matching expected slice'
        result['details'] = 'This element doesn\'t match any known slice defined in the profile. This may not be a problem if your use case allows additional elements.'
    
    elif 'Validation for profile' in diagnostics and 'Loaded packages' in diagnostics:
        result['summary'] = 'Validation context loaded'
        version_match = re.search(r'profile\s+([^\s]+)\s+\(([^)]+)\)', diagnostics)
        if version_match:
            profile_name = version_match.group(1).split('/')[-1]
            version = version_match.group(2)
            result['details'] = f'Using profile: {profile_name} ({version})'
        else:
            result['details'] = 'Validation configuration loaded successfully'
    
    elif 'Wrong Display Name' in diagnostics:
        wrong_match = re.search(r"Wrong Display Name '([^']+)'", diagnostics)
        correct_match = re.search(r"Valid display is '([^']+)'", diagnostics)
        system_match = re.search(r'for ([^\s]+)\s', diagnostics)
        
        wrong_name = wrong_match.group(1) if wrong_match else 'unknown'
        correct_name = correct_match.group(1) if correct_match else 'unknown'
        system = system_match.group(1).split('/')[-1] if system_match else 'unknown system'
        
        result['summary'] = f'Display name should be "{correct_name}" not "{wrong_name}"'
        result['details'] = f'Terminology: {system}'
    
    elif 'provided as bundle param' in diagnostics or 'Validate resource against' in diagnostics:
        result['summary'] = 'Validating nested resource'
        profile_match = re.search(r'profile\s+([^\s]+)', diagnostics)
        if profile_match:
            profile_name = profile_match.group(1).split('/')[-1]
            result['details'] = f'Checking resource against: {profile_name}'
        else:
            result['details'] = 'Nested resource validation in progress'
    
    else:
        sentences = re.split(r'[.!?]\s+', diagnostics)
        first_sentence = sentences[0] if sentences else diagnostics
        result['summary'] = first_sentence[:120] + ('...' if len(first_sentence) > 120 else '')
        result['details'] = diagnostics[:500] + ('...' if len(diagnostics) > 500 else '')
    
    # Split into sub-issues
    issue_pattern = r'\d+\.\)\s+Bundle\.entry\[\d+\]'
    if re.search(issue_pattern, diagnostics):
        parts = re.split(r'(\d+\.\)\s+Bundle\.entry\[\d+\])', diagnostics)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                issue_text = parts[i] + parts[i + 1]
                summary = issue_text[:150] + ('...' if len(issue_text) > 150 else '')
                result['sub_issues'].append(summary)
    
    return result


print("="*80)
print("MATCHBOX DIAGNOSTIC PARSER TEST")
print("="*80)

for idx, msg in enumerate(test_messages, 1):
    print(f"\n{'='*80}")
    print(f"TEST MESSAGE {idx}")
    print(f"{'='*80}")
    print(f"\nOriginal ({len(msg)} chars):")
    print(msg[:150] + "..." if len(msg) > 150 else msg)
    
    parsed = parse_matchbox_diagnostic(msg)
    
    print(f"\n✨ PARSED OUTPUT:")
    print(f"  Summary: {parsed['summary']}")
    print(f"  Details: {parsed['details']}")
    
    if parsed['fhir_paths']:
        print(f"  FHIR Paths: {', '.join(parsed['fhir_paths'])}")
    
    if parsed['profile_urls']:
        print(f"  Profile URLs ({len(parsed['profile_urls'])}):")
        for url in parsed['profile_urls']:
            profile_name = url.split('/')[-1]
            print(f"    • {profile_name}")
    
    if parsed['sub_issues']:
        print(f"  Sub-issues ({len(parsed['sub_issues'])}):")
        for i, sub in enumerate(parsed['sub_issues'], 1):
            print(f"    {i}. {sub[:80]}...")

print("\n" + "="*80)
print("✅ Parser test complete!")
print("="*80)
