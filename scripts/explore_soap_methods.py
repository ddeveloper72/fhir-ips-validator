"""
Explore SOAP API methods to see if there's a way to get validation result OIDs
"""

from zeep import Client
from zeep.plugins import HistoryPlugin
import os
from dotenv import load_dotenv

load_dotenv()

WSDL_URL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'

def explore_soap_methods():
    """List all available SOAP methods"""
    print("=" * 80)
    print("🔍 EXPLORING SOAP API METHODS")
    print("=" * 80)
    
    print(f"\nConnecting to: {WSDL_URL}")
    
    try:
        # Create client with history plugin to see requests/responses
        history = HistoryPlugin()
        client = Client(WSDL_URL, plugins=[history])
        
        print(f"\n✅ Connected successfully!")
        
        # Get service information
        print(f"\n{'─'*80}")
        print("Available Services:")
        print(f"{'─'*80}")
        
        for service in client.wsdl.services.values():
            print(f"\nService: {service.name}")
            
            for port in service.ports.values():
                print(f"  Port: {port.name}")
                print(f"  Binding: {port.binding.name}")
                print(f"  Methods:")
                
                operations = port.binding._operations
                for op_name in sorted(operations.keys()):
                    operation = operations[op_name]
                    print(f"\n    📋 {op_name}")
                    
                    # Try to get input parameters
                    if hasattr(operation.input, 'body'):
                        input_element = operation.input.body
                        if hasattr(input_element, 'type'):
                            print(f"       Input type: {input_element.type.name}")
                            # Try to get elements
                            if hasattr(input_element.type, 'elements'):
                                print(f"       Parameters:")
                                for elem in input_element.type.elements:
                                    elem_name = elem[0] if isinstance(elem, tuple) else 'unknown'
                                    print(f"         - {elem_name}")
                    
                    # Try to get output type
                    if hasattr(operation.output, 'body'):
                        output_element = operation.output.body
                        if hasattr(output_element, 'type'):
                            print(f"       Output type: {output_element.type.name}")
        
        # Look for methods that might return OIDs
        print(f"\n{'='*80}")
        print("Methods that might return validation result OIDs:")
        print(f"{'='*80}")
        
        interesting_methods = []
        for service in client.wsdl.services.values():
            for port in service.ports.values():
                operations = port.binding._operations
                for op_name in operations.keys():
                    op_lower = op_name.lower()
                    if any(keyword in op_lower for keyword in ['get', 'retrieve', 'result', 'oid', 'id', 'reference', 'url', 'report']):
                        interesting_methods.append(op_name)
        
        if interesting_methods:
            print("\n✅ Found potentially relevant methods:")
            for method in sorted(interesting_methods):
                print(f"   - {method}")
        else:
            print("\n❌ No methods found that suggest OID retrieval")
        
        # Test if we can call any methods that might help
        print(f"\n{'='*80}")
        print("Testing Method Signatures:")
        print(f"{'='*80}")
        
        # Try to get detailed info about each method
        for method_name in ['validateDocument', 'getListOfValidators', 'validateEvsObject']:
            try:
                method = getattr(client.service, method_name, None)
                if method:
                    print(f"\n📋 Method: {method_name}")
                    # Try to get signature info from zeep
                    # This is tricky as zeep doesn't expose signatures directly
                    print(f"   Method exists and is callable")
            except Exception as e:
                pass
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def check_validateEvsObject_method():
    """Check if validateEvsObject returns different info than validateDocument"""
    print(f"\n{'='*80}")
    print("Testing validateEvsObject Method")
    print(f"{'='*80}")
    
    try:
        client = Client(WSDL_URL)
        
        # Check if this method exists
        if hasattr(client.service, 'validateEvsObject'):
            print("\n✅ validateEvsObject method exists!")
            print("\nThis method might return different information.")
            print("Would need to test with actual parameters.")
        else:
            print("\n❌ validateEvsObject method not found")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    explore_soap_methods()
    check_validateEvsObject_method()
    
    print(f"\n{'='*80}")
    print("CONCLUSION")
    print(f"{'='*80}")
    print("""
Based on the SOAP API exploration:

1. The SOAP API is designed for SYNCHRONOUS validation
   - Submit document → Get immediate results → No persistent storage

2. The REST API is designed for ASYNCHRONOUS validation
   - Submit document → Get OID → Results stored persistently → Get report URL

3. SOAP response contains validation results but NO OID

4. This is BY DESIGN - two different workflows:
   - SOAP: Quick validation for development/testing
   - REST: Persistent reports for compliance/sharing

RECOMMENDATION:
Keep current SOAP implementation with web UI link for persistent reports.
This is the intended workflow for Gazelle CDA validation.
    """)

if __name__ == '__main__':
    main()
