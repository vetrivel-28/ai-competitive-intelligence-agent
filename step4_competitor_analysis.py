"""
Step 4: Competitor Price Analysis
Compares brands by average price and rating, identifies best value
"""

import pandas as pd
import numpy as np
from load_data import load_data

def clean_price(price):
    """Clean and convert price to numeric"""
    if pd.isna(price) or price == 'N/A' or price == '':
        return np.nan
    
    # Convert to string and remove currency symbols and commas
    price_str = str(price).replace('₹', '').replace('$', '').replace(',', '').strip()
    
    try:
        return float(price_str)
    except:
        return np.nan

def clean_rating(rating):
    """Clean and convert rating to numeric"""
    if pd.isna(rating) or rating == 'N/A' or rating == '':
        return np.nan
    
    # Extract numeric rating (e.g., "4.5 out of 5" -> 4.5)
    rating_str = str(rating).split()[0]
    
    try:
        return float(rating_str)
    except:
        return np.nan

def perform_competitor_analysis(data):
    """Perform competitor price and rating analysis"""
    
    print("=" * 70)
    print("STEP 4: COMPETITOR PRICE ANALYSIS")
    print("=" * 70)
    
    # Combine product data from Amazon and Flipkart
    product_data = []
    
    if not data['amazon'].empty:
        amazon_df = data['amazon'].copy()
        amazon_df['source'] = 'Amazon'
        product_data.append(amazon_df)
    
    if not data['flipkart'].empty:
        flipkart_df = data['flipkart'].copy()
        flipkart_df['source'] = 'Flipkart'
        product_data.append(flipkart_df)
    
    if not product_data:
        print("❌ No product data available for analysis")
        return pd.DataFrame(), pd.DataFrame()
    
    # Combine all products
    all_products = pd.concat(product_data, ignore_index=True)
    
    print(f"\n📊 Total products for analysis: {len(all_products)}")
    
    # Clean price and rating data
    all_products['price_clean'] = all_products['price'].apply(clean_price)
    all_products['rating_clean'] = all_products['rating'].apply(clean_rating)
    
    # Filter out products with missing price data
    # Keep Unknown brands if that's all we have
    valid_products = all_products[all_products['price_clean'].notna()].copy()
    
    # If no ratings, use a default rating of 4.0 for demonstration
    if valid_products['rating_clean'].isna().all():
        print("\n⚠️ No rating data found. Using default rating of 4.0 for analysis.")
        valid_products['rating_clean'] = 4.0
    
    # If all brands are Unknown, try to extract from laptop_name
    if (valid_products['brand'] == 'Unknown').all():
        print("\n⚠️ All brands marked as 'Unknown'. Attempting to extract from laptop names...")
        
        def extract_brand_from_name(name):
            if pd.isna(name):
                return 'Unknown'
            name_lower = str(name).lower()
            brands = ['dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'apple', 'samsung', 
                     'microsoft', 'razer', 'alienware', 'lg']
            for brand in brands:
                if brand in name_lower:
                    return brand.capitalize()
            return 'Generic'
        
        valid_products['brand'] = valid_products['laptop_name'].apply(extract_brand_from_name)
    
    # Filter out Unknown brands
    valid_products = valid_products[valid_products['brand'] != 'Unknown'].copy()
    
    print(f"✅ Valid products with price data: {len(valid_products)}")
    
    if valid_products.empty:
        print("❌ No valid products for analysis")
        print("\n💡 TIP: Make sure your CSV files have:")
        print("   - Valid price data (numeric, e.g., 55000)")
        print("   - Brand information or laptop names with brand mentions")
        return pd.DataFrame(), pd.DataFrame()

    
    # Group by brand and calculate statistics
    print("\n" + "-" * 70)
    print("Calculating brand statistics...")
    print("-" * 70)
    
    brand_stats = valid_products.groupby('brand').agg({
        'price_clean': ['mean', 'min', 'max', 'count'],
        'rating_clean': ['mean', 'min', 'max']
    }).round(2)
    
    # Flatten column names
    brand_stats.columns = ['_'.join(col).strip() for col in brand_stats.columns.values]
    brand_stats = brand_stats.reset_index()
    
    # Rename columns for clarity
    brand_stats.columns = [
        'Brand', 'Avg_Price', 'Min_Price', 'Max_Price', 'Product_Count',
        'Avg_Rating', 'Min_Rating', 'Max_Rating'
    ]
    
    # Calculate value score (rating / price * 10000 for readability)
    brand_stats['Value_Score'] = (brand_stats['Avg_Rating'] / brand_stats['Avg_Price'] * 10000).round(2)
    
    # Sort by average price
    brand_stats = brand_stats.sort_values('Avg_Price', ascending=False)
    
    return brand_stats, valid_products

def identify_leaders(brand_stats):
    """Identify market leaders in different categories"""
    
    print("\n" + "=" * 70)
    print("COMPETITOR ANALYSIS RESULTS")
    print("=" * 70)
    
    # Display main comparison table
    print("\n📊 BRAND COMPARISON TABLE:")
    print("-" * 70)
    comparison_table = brand_stats[['Brand', 'Avg_Price', 'Avg_Rating', 'Product_Count']].copy()
    comparison_table['Avg_Price'] = comparison_table['Avg_Price'].apply(lambda x: f"₹{x:,.0f}")
    print(comparison_table.to_string(index=False))
    
    # Identify leaders
    print("\n" + "=" * 70)
    print("MARKET LEADERS")
    print("=" * 70)
    
    leaders = {}
    
    # Most expensive brand
    most_expensive = brand_stats.loc[brand_stats['Avg_Price'].idxmax()]
    leaders['most_expensive'] = most_expensive
    print(f"\n💰 MOST EXPENSIVE BRAND:")
    print(f"   {most_expensive['Brand']}")
    print(f"   Average Price: ₹{most_expensive['Avg_Price']:,.0f}")
    print(f"   Price Range: ₹{most_expensive['Min_Price']:,.0f} - ₹{most_expensive['Max_Price']:,.0f}")
    
    # Least expensive brand
    least_expensive = brand_stats.loc[brand_stats['Avg_Price'].idxmin()]
    leaders['least_expensive'] = least_expensive
    print(f"\n💵 MOST AFFORDABLE BRAND:")
    print(f"   {least_expensive['Brand']}")
    print(f"   Average Price: ₹{least_expensive['Avg_Price']:,.0f}")
    print(f"   Price Range: ₹{least_expensive['Min_Price']:,.0f} - ₹{least_expensive['Max_Price']:,.0f}")
    
    # Best rated brand
    best_rated = brand_stats.loc[brand_stats['Avg_Rating'].idxmax()]
    leaders['best_rated'] = best_rated
    print(f"\n⭐ BEST RATED BRAND:")
    print(f"   {best_rated['Brand']}")
    print(f"   Average Rating: {best_rated['Avg_Rating']:.2f}/5.0")
    print(f"   Rating Range: {best_rated['Min_Rating']:.1f} - {best_rated['Max_Rating']:.1f}")
    
    # Best value brand (highest rating per rupee)
    best_value = brand_stats.loc[brand_stats['Value_Score'].idxmax()]
    leaders['best_value'] = best_value
    print(f"\n🏆 BEST VALUE BRAND:")
    print(f"   {best_value['Brand']}")
    print(f"   Average Price: ₹{best_value['Avg_Price']:,.0f}")
    print(f"   Average Rating: {best_value['Avg_Rating']:.2f}/5.0")
    print(f"   Value Score: {best_value['Value_Score']:.2f}")
    
    return leaders


def generate_insights(brand_stats, valid_products):
    """Generate market insights"""
    
    print("\n" + "=" * 70)
    print("MARKET INSIGHTS")
    print("=" * 70)
    
    # Overall market statistics
    avg_market_price = valid_products['price_clean'].mean()
    avg_market_rating = valid_products['rating_clean'].mean()
    
    print(f"\n📈 Overall Market Statistics:")
    print(f"   Average Price: ₹{avg_market_price:,.0f}")
    print(f"   Average Rating: {avg_market_rating:.2f}/5.0")
    print(f"   Total Brands: {len(brand_stats)}")
    print(f"   Total Products: {len(valid_products)}")
    
    # Price segments
    print(f"\n💰 Price Segments:")
    budget = len(valid_products[valid_products['price_clean'] < 50000])
    mid_range = len(valid_products[(valid_products['price_clean'] >= 50000) & 
                                    (valid_products['price_clean'] < 80000)])
    premium = len(valid_products[valid_products['price_clean'] >= 80000])
    
    print(f"   Budget (<₹50,000): {budget} products ({budget/len(valid_products)*100:.1f}%)")
    print(f"   Mid-range (₹50,000-₹80,000): {mid_range} products ({mid_range/len(valid_products)*100:.1f}%)")
    print(f"   Premium (>₹80,000): {premium} products ({premium/len(valid_products)*100:.1f}%)")
    
    # Rating distribution
    print(f"\n⭐ Rating Distribution:")
    excellent = len(valid_products[valid_products['rating_clean'] >= 4.5])
    good = len(valid_products[(valid_products['rating_clean'] >= 4.0) & 
                              (valid_products['rating_clean'] < 4.5)])
    average = len(valid_products[valid_products['rating_clean'] < 4.0])
    
    print(f"   Excellent (≥4.5): {excellent} products ({excellent/len(valid_products)*100:.1f}%)")
    print(f"   Good (4.0-4.4): {good} products ({good/len(valid_products)*100:.1f}%)")
    print(f"   Average (<4.0): {average} products ({average/len(valid_products)*100:.1f}%)")
    
    # Price vs Rating correlation
    correlation = valid_products['price_clean'].corr(valid_products['rating_clean'])
    print(f"\n📊 Price-Rating Correlation: {correlation:.3f}")
    if correlation > 0.3:
        print("   → Higher prices tend to have better ratings")
    elif correlation < -0.3:
        print("   → Lower prices tend to have better ratings")
    else:
        print("   → Price and rating are not strongly correlated")

def main():
    """Main execution function"""
    
    # Load data
    print("Loading data from Step 1...")
    data = load_data()
    
    # Perform competitor analysis
    brand_stats, valid_products = perform_competitor_analysis(data)
    
    if brand_stats.empty:
        print("\n❌ Cannot perform analysis - insufficient data")
        return None, None
    
    # Identify market leaders
    leaders = identify_leaders(brand_stats)
    
    # Generate insights
    generate_insights(brand_stats, valid_products)
    
    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    brand_stats.to_csv('competitor_analysis.csv', index=False)
    print("✅ Saved: competitor_analysis.csv")
    
    # Create detailed report
    with open('competitor_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write("COMPETITOR PRICE ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("BRAND COMPARISON TABLE\n")
        f.write("-" * 70 + "\n")
        f.write(brand_stats[['Brand', 'Avg_Price', 'Avg_Rating', 'Product_Count']].to_string(index=False))
        f.write("\n\n")
        
        f.write("MARKET LEADERS\n")
        f.write("-" * 70 + "\n")
        f.write(f"\nMost Expensive: {leaders['most_expensive']['Brand']} (₹{leaders['most_expensive']['Avg_Price']:,.0f})\n")
        f.write(f"Most Affordable: {leaders['least_expensive']['Brand']} (₹{leaders['least_expensive']['Avg_Price']:,.0f})\n")
        f.write(f"Best Rated: {leaders['best_rated']['Brand']} ({leaders['best_rated']['Avg_Rating']:.2f}/5.0)\n")
        f.write(f"Best Value: {leaders['best_value']['Brand']} (Score: {leaders['best_value']['Value_Score']:.2f})\n")
    
    print("✅ Saved: competitor_analysis_report.txt")
    
    print("\n" + "=" * 70)
    print("✅ STEP 4 COMPLETE: Competitor Analysis Done!")
    print("=" * 70)
    
    return brand_stats, leaders

if __name__ == "__main__":
    brand_stats, leaders = main()
