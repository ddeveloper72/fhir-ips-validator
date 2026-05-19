"""
Check SOAP service methods
"""

from zeep import Client

EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'

print("=" * 80)
print("Gazelle SOAP Service Methods")
print("=" * 80)

client = Client(EHDS_WSDL)

print("\nService: ", client.service)
print("\nAvailable methods:")

for service in client.wsdl.services.values():
    print(f"\nService: {service.name}")
    for port in service.ports.values():
        print(f"\n  Port: {port.name}")
        operations = port.binding._operations
        for op_name, operation in operations.items():
            print(f"\n    Operation: {op_name}")
            # Get input/output
            if hasattr(operation, 'input'):
                print(f"      Input: {operation.input.body.type.name if hasattr(operation.input, 'body') else 'N/A'}")
            if hasattr(operation, 'output'):
                print(f"      Output: {operation.output.body.type.name if hasattr(operation.output, 'body') else 'N/A'}")
