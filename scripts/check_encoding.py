"""Check for Windows-1252 characters in CDA files."""

files = [
    'examples/Patrick_Murphy_PS.xml',
    'examples/Diana_Ferreira_PS.xml',
    'examples/patient_summary_cda.xml',
    'examples/hospital_discharge_cda.xml'
]

for file_path in files:
    print(f"\n{file_path}:")
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Find all non-UTF-8 compatible bytes
        problem_bytes = []
        for i, byte in enumerate(data):
            if byte >= 0x80 and byte < 0xC0:  # Potential Windows-1252 range
                problem_bytes.append((i, hex(byte)))
        
        if problem_bytes:
            print(f"  ⚠️  Found {len(problem_bytes)} potentially problematic bytes:")
            for pos, byte_val in problem_bytes[:10]:  # Show first 10
                context = data[max(0, pos-20):pos+20]
                print(f"    Position {pos}: {byte_val} - Context: {context}")
        else:
            print("  ✅ No encoding issues found")
            
        # Try to decode as UTF-8
        try:
            data.decode('utf-8')
            print("  ✅ Valid UTF-8")
        except UnicodeDecodeError as e:
            print(f"  ❌ UTF-8 decode error: {e}")
            
    except FileNotFoundError:
        print(f"  ❌ File not found")
