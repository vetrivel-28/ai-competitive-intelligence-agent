"""
Quick check — counts how many reviews were collected per product in amazon.csv and flipkart.csv
"""
import pandas as pd

for filename, review_col in [('amazon.csv', 'review_text'), ('flipkart.csv', 'reviews_comments')]:
    print(f"\n{'='*60}")
    print(f"FILE: {filename}")
    print(f"{'='*60}")
    try:
        df = pd.read_csv(filename)
        if review_col not in df.columns:
            print(f"  Column '{review_col}' not found. Columns: {list(df.columns)}")
            continue

        print(f"Total products: {len(df)}\n")
        for idx, row in df.iterrows():
            name = str(row.get('laptop_name', 'N/A'))[:45]
            reviews = str(row.get(review_col, ''))
            if reviews and reviews != 'N/A':
                count = len([r for r in reviews.split(' || ') if r.strip()])
            else:
                count = 0
            print(f"  [{idx+1}] {name:<45} → {count} reviews")

    except FileNotFoundError:
        print(f"  File not found. Run the scraper first.")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone.")
