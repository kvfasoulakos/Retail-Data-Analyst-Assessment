import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

class ProductMatcher:
    def __init__(self):
        self.weights = {
            'similarity': 0.60,
            'attributes': 0.40
        }
        # Regex patterns for attribute extraction
        self.patterns = {
            'brand': r'\b(nike|adidas|puma|vans|converse|levi\'s|zara|h&m|gucci|prada)\b',
            'color': r'\b(black|white|blue|red|green|yellow|navy|grey|pink|beige|brown)\b',
            'size': r'\b(xs|s|m|l|xl|xxl|\d{1,2}(?:\.\d)?(?:\s?(?:cm|mm|in|"))?)\b',
            'season': r'\b(summer|winter|autumn|spring|fall|ss\d{2}|fw\d{2})\b',
            'gender': r'\b(men|women|kids|unisex|boy|girl)\b'
        }

    def load_data(self, catalog_path, unstructured_path):
        """Loads data with error handling."""
        try:
            print("Loading datasets...")
            self.catalog = pd.read_csv(catalog_path)
            self.unstructured = pd.read_csv(unstructured_path)
            print(f"Loaded {len(self.catalog)} catalog items and {len(self.unstructured)} unstructured items.")
        except FileNotFoundError:
            print(f"Error: Could not find files. Ensure '{catalog_path}' and '{unstructured_path}' are in the directory.")
            raise

    def preprocess_text(self, text):
        if pd.isna(text):
            return ""
        text = str(text).lower()
        # Clean specific typos mentioned in report (e.g. santals -> sandals)
        text = text.replace('santals', 'sandals').replace('naavy', 'navy')
        text = re.sub(r'[^\w\s]', ' ', text)
        return " ".join(text.split())

    def extract_attributes(self, text):
        extracted = {}
        text = str(text).lower()
        for key, pattern in self.patterns.items():
            match = re.search(pattern, text)
            if match:
                extracted[key] = match.group(1)
            else:
                extracted[key] = None
        return extracted

    def calculate_tfidf_similarity(self):
        """Calculates text similarity using TF-IDF."""
        print("Calculating TF-IDF similarity...")
        
        # Prepare corpus
        self.catalog['processed_desc'] = self.catalog['Description'].apply(self.preprocess_text)
        self.unstructured['processed_desc'] = self.unstructured['description'].apply(self.preprocess_text)
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix_catalog = vectorizer.fit_transform(self.catalog['processed_desc'])
        tfidf_matrix_unstructured = vectorizer.transform(self.unstructured['processed_desc'])
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(tfidf_matrix_unstructured, tfidf_matrix_catalog)

    def find_best_matches(self):
        """Core logic: Hybrid matching of Text Similarity + Attribute Matching."""
        print("Running hybrid matching logic...")
        results = []

        for idx, row in self.unstructured.iterrows():
            u_attrs = self.extract_attributes(row['description'])
            
            # Get top candidates based on text similarity first (optimization)
            sim_scores = self.similarity_matrix[idx]
            top_indices = sim_scores.argsort()[-5:][::-1] # Check top 5 candidates
            
            best_score = -1
            best_match_row = None
            match_reason_parts = []
            
            for cat_idx in top_indices:
                cat_row = self.catalog.iloc[cat_idx]
                cat_attrs = self.extract_attributes(cat_row['Description'])
                
                # Attribute Score
                attr_matches = 0
                total_checks = 0
                current_reasons = []
                
                for key in self.patterns.keys():
                    if u_attrs[key] and cat_attrs[key]:
                        total_checks += 1
                        if u_attrs[key] == cat_attrs[key]:
                            attr_matches += 1
                            current_reasons.append(f"{key.title()}: {u_attrs[key]}")
                
                attr_score = (attr_matches / total_checks) if total_checks > 0 else 0
                
                # Hybrid Score
                text_score = sim_scores[cat_idx]
                final_score = (text_score * self.weights['similarity']) + (attr_score * self.weights['attributes'])
                
                if final_score > best_score:
                    best_score = final_score
                    best_match_row = cat_row
                    
                    # Formatting logic for "Match Reason" (Highly praised in report)
                    reason_str = " | ".join(current_reasons)
                    if not reason_str and text_score > 0.7:
                        reason_str = "High Text Similarity"
                    match_reason_parts = reason_str

            # Append result
            results.append({
                'Unstructured_ID': row.get('id', idx), # Handle if ID column exists or use index
                'Original_Description': row['description'],
                'Matched_Product_ID': best_match_row['Product_ID'] if best_match_row is not None else None,
                'Matched_Description': best_match_row['Description'] if best_match_row is not None else None,
                'Confidence_Score': round(best_score * 100, 2),
                'Match_Reason': match_reason_parts if match_reason_parts else "Low Confidence Match"
            })
            
        self.results_df = pd.DataFrame(results)
        return self.results_df

    def generate_visualizations(self):
        """Generates and SAVES the confidence distribution plot."""
        print("Generating visualizations...")
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.results_df, x='Confidence_Score', bins=20, kde=True, color='teal')
        plt.title('Distribution of Match Confidence Scores')
        plt.xlabel('Confidence Score (%)')
        plt.ylabel('Count')
        
        # Save figure to fix the "missing file" issue in the report
        output_file = 'viz1_confidence_distribution.png'
        plt.savefig(output_file)
        print(f"Visualization saved to {output_file}")
        plt.close()

    def run(self):
        self.load_data('b_product_catalog.csv', 'b_unstructured_descriptions.csv')
        self.calculate_tfidf_similarity()
        df = self.find_best_matches()
        self.generate_visualizations()
        
        df.to_csv('matching_results.csv', index=False)
        print("Process complete. Results saved to 'matching_results.csv'.")

if __name__ == "__main__":
    matcher = ProductMatcher()
    matcher.run()