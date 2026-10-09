"""Cross-language smoke test for the separate E5 collection."""
from query_e5 import search

QUERIES = [
    "What is DBMS?",
    "DBMS क्या है?",
    "தரவுத்தளம் என்றால் என்ன?",
    "What is computer science with artificial intelligence?",
    "செயற்கை நுண்ணறிவுடன் கணினி அறிவியல்",
    "कृत्रिम बुद्धिमत्ता के साथ कंप्यूटर विज्ञान",
]

def main():
    for query in QUERIES:
        print("\n" + "#" * 80)
        print(f"QUERY: {query}")
        try:
            rows = search(query, 5)
            if not rows:
                print("No results. Is the E5 collection populated?")
                continue
            for rank, row in enumerate(rows, start=1):
                meta = row["metadata"] or {}
                print(f"\n{rank}. {meta.get('title', meta.get('video_id', 'Unknown'))} [{meta.get('video_id')}]")
                print(f"Distance: {row['distance']:.4f}")
                print(f"Text: {row['text'][:350]}")
        except Exception as exc:
            print(f"Search failed: {type(exc).__name__}: {exc}")

if __name__ == "__main__":
    main()
