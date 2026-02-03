import pandas as pd
import numpy as np
import time
import os

class BusinessEngine:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_df = None
        self.clean_df = None
        self.metadata = {}

    def load_data(self):
        """Phase A: Smart Loading"""
        ext = os.path.splitext(self.file_path)[-1].lower()
        if ext == '.csv':
            self.raw_df = pd.read_csv(self.file_path, low_memory=False)
        elif ext in ['.xls', '.xlsx']:
            self.raw_df = pd.read_excel(self.file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported format: {ext}")
        return self.raw_df

    def standardize_and_clean(self):
        df = self.raw_df.copy()
        
        # 1. Standardize Headers
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_').str.replace('(', '', regex=False)
                      .str.replace(')', '', regex=False))
        
        # 2. Handle "Trash" Strings
        df = df.replace(['N/A', 'n/a', '-', 'None', 'none'], np.nan)

        # 3. Numeric Scrubber (Crucial for Price/Quantity multiplication)
        for col in df.columns:
            if any(k in col for k in ['price', 'sales', 'revenue', 'quantity', 'amount', 'cost']):
                if df[col].dtype == 'object':
                    df[col] = df[col].replace(r'[\$, ]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 4. SMART LOGIC: Auto-calculate Revenue
        # Look for columns that imply a 'Unit Price' and a 'Volume'
        price_col = next((c for c in df.columns if 'price' in c or 'unit_price' in c), None)
        qty_col = next((c for c in df.columns if 'quantity' in c or 'qty' in c), None)
        
        if price_col and qty_col:
            # Create a new primary metric
            df['calculated_revenue'] = df[price_col] * df[qty_col]
            print(f"--> Logical Insight: Calculated 'calculated_revenue' from {price_col} * {qty_col}")

        # 5. Fill remaining gaps
        text_cols = df.select_dtypes(include=['object']).columns
        df[text_cols] = df[text_cols].fillna('Unknown')
        
        self.clean_df = df
        return df

    def classify_columns(self):
        df = self.clean_df
        classes = {'temporal': [], 'financial': [], 'categorical': [], 'identity': []}

        # Priority List: Ensure 'calculated_revenue' is at the front of the line
        cols = list(df.columns)
        if 'calculated_revenue' in cols:
            cols.insert(0, cols.pop(cols.index('calculated_revenue')))

        for col in cols:
            col_lower = col.lower()
            
            if any(k in col_lower for k in ['id', 'sku', 'code']) and 'customer' not in col_lower:
                classes['identity'].append(col)
            elif any(k in col_lower for k in ['date', 'time', 'year', 'month']):
                classes['temporal'].append(col)
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=False, cache=True)
            elif any(k in col_lower for k in ['revenue', 'sales', 'price', 'profit', 'amount']):
                classes['financial'].append(col)
            elif df[col].dtype == 'object' and df[col].nunique() < (len(df) * 0.2):
                classes['categorical'].append(col)

        self.metadata = classes
        return classes

    def run_analysis(self):
        """Phase C: Robust Logic (Fixed Future Deprecation)"""
        classes = self.metadata
        df = self.clean_df
        report = {}

        if classes['financial'] and classes['categorical']:
            # Use the category with the most meaningful spread
            main_metric = classes['financial'][0]
            # Prioritize 'product_category' if it exists, else use first cat
            main_cat = next((c for c in classes['categorical'] if 'category' in c), classes['categorical'][0])
            
            report['top_performers'] = df.groupby(main_cat)[main_metric].sum().sort_values(ascending=False).head(5)

        if classes['temporal'] and classes['financial']:
            date_col = classes['temporal'][0]
            metric_col = classes['financial'][0]
            # Fixed 'ME' warning here
            temp_df = df.dropna(subset=[date_col]).set_index(date_col)
            report['monthly_trend'] = temp_df[metric_col].resample('ME').sum()

        return report
    
    def generate_json_report(self, analysis_results):
        """Converts complex Pandas objects into a clean JSON-ready dictionary."""
        import json
        
        report = {
            "metadata": {
                "filename": os.path.basename(self.file_path),
                "columns_classified": self.metadata,
                "row_count": len(self.clean_df)
            },
            "charts": {}
        }

        # Convert Top Performers to a format frontend charts love
        if 'top_performers' in analysis_results:
            data = analysis_results['top_performers']
            report["charts"]["bar_chart"] = {
                "labels": data.index.tolist(),
                "values": data.values.tolist(),
                "title": f"Top {data.index.name.replace('_', ' ').title()} by Sales"
            }

        # Convert Time Trends
        if 'monthly_trend' in analysis_results:
            data = analysis_results['monthly_trend']
            report["charts"]["line_chart"] = {
                "labels": data.index.strftime('%Y-%m').tolist(),
                "values": data.values.tolist(),
                "title": "Revenue Growth Over Time"
            }

        return json.dumps(report, indent=4)

if __name__ == "__main__":
    FILE_NAME = 'online_retail_II.xlsx' 
    engine = BusinessEngine(FILE_NAME)
    
    # 2. Run Pipeline
    print(f"--- Processing: {FILE_NAME} ---")
    start = time.perf_counter()

    engine.load_data()
    engine.standardize_and_clean()
    classes = engine.classify_columns()
    analysis = engine.run_analysis()
    
    duration = time.perf_counter() - start

    # Export the 'Signal' to your future platform frontend
    json_output = engine.generate_json_report(analysis)
    print(json_output)
    print(f"\n[EVALUATION]")
    print(f"- Time to Process: {duration:.4f}s")
    print(f"- Identified {len(classes['financial'])} Financial columns: {classes['financial']}")
    print(f"- Identified {len(classes['categorical'])} Categories: {classes['categorical']}")
    
    print(f"\n[INSIGHTS PREVIEW]")
    if 'top_performers' in analysis:
        print(f"Top Grouping ({classes['categorical'][0]}) by ({classes['financial'][0]}):")
        print(analysis['top_performers'])