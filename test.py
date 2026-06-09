from usajobs_api import fetch_usajobs

jobs = fetch_usajobs("data analyst")

print(f"Found {len(jobs)} jobs\n")

for i, job in enumerate(jobs, start=1):
    desc = job.get("MatchedObjectDescriptor", {})
    print(f"{i}. {desc.get('PositionTitle')}")
    print(f"   Location: {', '.join(loc.get('LocationName', '') for loc in desc.get('PositionLocation', []))}")
    print(f"   Apply: {desc.get('PositionURI')}")
    print()
