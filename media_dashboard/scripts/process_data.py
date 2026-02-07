import pandas as pd
import json
import logging
import os
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_excel(file_path, output_path):
    """
    Reads the Excel file and converts it to a JSON structure suitable for the dashboard.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return

    try:
        logging.info(f"Reading file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Log columns for debugging
        logging.info(f"Columns found: {df.columns.tolist()}")

        # Standardize column names (strip whitespace)
        df.columns = df.columns.str.strip()

        # Define mapping from Excel columns to Data Dictionary keys
        # Based on analysis:
        # '序号', '客户名称', '媒介', '媒体名称', '发布位置', '合作内容及资源包', '见刊日期', '发布平台', '见刊标题', '见刊链接', '阅读量/播放量', '互动量', '备注'
        
        processed_data = []
        
        for index, row in df.iterrows():
            # Skip rows where critical info might be missing or it's a summary row (if any)
            # For now, we process all rows.

            # Handle NaN values for '阅读量/播放量' and '互动量'
            reads = row.get('阅读量/播放量', 0)
            if pd.isna(reads) or isinstance(reads, str): 
                # Attempt to clean string if it contains text, or set to 0
                # If it's a string like "10万+", we might need parsing. 
                # For now, assume it's numeric or treat as 0 if failing.
                try:
                    reads = float(str(reads).replace(',', ''))
                except ValueError:
                    reads = 0
            
            interactions = row.get('互动量', 0)
            if pd.isna(interactions):
                interactions = 0
            else:
                try:
                    # Handle cases like '-' or strings
                    interactions = str(interactions).replace(',', '').strip()
                    if interactions == '-' or interactions == '':
                        interactions = 0
                    else:
                        interactions = float(interactions)
                except ValueError:
                    interactions = 0
            
            item = {
                "id": str(row.get('序号', index + 1)),
                "project": str(row.get('客户名称', 'Unknown Project')), # Or use filename
                "media": str(row.get('媒体名称', '')),
                "platform": str(row.get('发布平台', 'Other')),
                "account": str(row.get('媒体名称', '')), # Fallback as we don't have separate account name col always
                "position": str(row.get('发布位置', '-')),
                "title": str(row.get('见刊标题', 'No Title')),
                "link": str(row.get('见刊链接', '#')),
                "reads": int(reads) if not pd.isna(reads) else 0,
                "interactions": int(interactions) if not pd.isna(interactions) else 0,
                "date": str(row.get('见刊日期', ''))
            }
            processed_data.append(item)

        logging.info(f"Processed {len(processed_data)} items.")

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Data saved to {output_path}")

    except Exception as e:
        logging.error(f"Error processing Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    EXCEL_FILE = "/Users/will/Desktop/通往AGI之路/公司业务相关/数据归档/20250206-CRV-batch3.xlsx" # Updated path
    OUTPUT_FILE = "../../public/data.json" # Relative path from media_dashboard/scripts/
    
    # Check if we are running from project root or elsewhere
    # script is in media_dashboard/scripts (planned), but for now I'm running it from root or Desktop
    # Let's assume we run it from /Users/will/Desktop/通往AGI之路
    
    process_excel(EXCEL_FILE, OUTPUT_FILE)
