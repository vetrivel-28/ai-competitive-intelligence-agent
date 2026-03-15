"""Create sample data for demonstration"""
import pandas as pd

# Create sample Amazon data
amazon_sample = pd.DataFrame({
    'laptop_name': [
        'Dell Inspiron 15', 'HP Pavilion 14', 'Lenovo IdeaPad 3',
        'ASUS VivoBook 15', 'Acer Aspire 5', 'Dell XPS 13',
        'HP Envy 13', 'Lenovo ThinkPad E14', 'ASUS ROG Strix',
        'MSI Modern 14'
    ],
    'brand': ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'Dell', 'HP', 'Lenovo', 'ASUS', 'MSI'],
    'price': [55000, 52000, 45000, 48000, 42000, 95000, 78000, 62000, 85000, 58000],
    'rating': [4.3, 4.2, 4.1, 4.4, 4.0, 4.7, 4.5, 4.6, 4.4, 4.3],
    'specifications': ['Intel i5, 8GB RAM', 'Intel i5, 8GB RAM', 'AMD Ryzen 5', 'Intel i5', 'Intel i3', 
                      'Intel i7, 16GB', 'Intel i7', 'Intel i5', 'AMD Ryzen 7', 'Intel i5'],
    'review_text': ['Good laptop', 'Nice performance', 'Value for money', 'Great display', 'Budget friendly',
                   'Premium build', 'Excellent', 'Business laptop', 'Gaming beast', 'Portable'],
    'comment_text': ['Recommended', 'Happy with purchase', 'Good deal', 'Love it', 'Decent',
                    'Worth the price', 'Amazing', 'Reliable', 'Fast', 'Lightweight']
})

# Create sample Flipkart data
flipkart_sample = pd.DataFrame({
    'laptop_name': [
        'Dell Vostro 15', 'HP 15s', 'Lenovo Legion 5',
        'ASUS TUF Gaming', 'Acer Nitro 5', 'Dell G15',
        'HP Omen 15', 'Lenovo Yoga Slim', 'ASUS ZenBook', 'MSI GF63'
    ],
    'brand': ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'Dell', 'HP', 'Lenovo', 'ASUS', 'MSI'],
    'price': [58000, 49000, 75000, 72000, 68000, 82000, 95000, 65000, 88000, 62000],
    'rating': [4.2, 4.1, 4.5, 4.4, 4.3, 4.4, 4.6, 4.3, 4.5, 4.2],
    'specifications': ['Intel i5', 'Intel i3', 'AMD Ryzen 7', 'AMD Ryzen 5', 'Intel i5',
                      'Intel i7', 'AMD Ryzen 7', 'Intel i5', 'Intel i7', 'Intel i5'],
    'reviews_comments': ['Good value', 'Affordable', 'Excellent gaming', 'Great performance', 'Good laptop',
                        'Gaming ready', 'Premium gaming', 'Slim design', 'Beautiful', 'Value for money']
})

# Save to CSV
amazon_sample.to_csv('amazon_sample.csv', index=False)
flipkart_sample.to_csv('flipkart_sample.csv', index=False)

print("✅ Sample data created:")
print("   - amazon_sample.csv")
print("   - flipkart_sample.csv")
print("\nTo use sample data, rename your current files and use these instead.")
