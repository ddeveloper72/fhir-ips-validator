"""Quick script to analyze the Matchbox validator page structure."""
import requests
from bs4 import BeautifulSoup

response = requests.get('https://gazelle.ehdsi.eu/evs/default/validator.seam?standard=28')
soup = BeautifulSoup(response.text, 'html.parser')

print("=== PAGE ANALYSIS ===\n")

title = soup.find('title')
print(f"Title: {title.get_text() if title else 'Not found'}\n")

h1s = soup.find_all(['h1', 'h2', 'h3'])
print("Headers:")
for h in h1s[:10]:
    print(f"  {h.name}: {h.get_text(strip=True)}")

print("\nFile inputs:")
inputs = soup.find_all('input', {'type': 'file'})
for i in inputs:
    print(f"  Name: {i.get('name')}")
    print(f"  Accept: {i.get('accept')}")
    print(f"  ID: {i.get('id')}")
    print()

print("Labels/Text mentioning FHIR:")
for text in soup.find_all(string=lambda t: t and 'FHIR' in str(t).upper()):
    print(f"  {str(text).strip()[:80]}")

print("\n=== SAVING FULL HTML ===")
with open('validator_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved to: validator_page.html")
