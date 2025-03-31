import json
import csv
import json
import pandas as pd

def flatten_job_data(job):
    """Flatten the nested job data structure"""
    return {
        'title': job.get('title', ''),
        'url': job.get('url', ''),
        'posted': job.get('posted', ''),
        'budget_type': job.get('budget', {}).get('type', ''),
        'budget_amount': job.get('budget', {}).get('amount', ''),
        'experience_level': job.get('experience_level', ''),
        'duration': job.get('duration', ''),
        'description': job.get('description', ''),
        'skills': ', '.join(job.get('skills', [])),
        'page_number': job.get('page_number', '')
    }

def convert_json_to_csv(input_file, output_file):
    # Read JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)

    # Flatten the data
    flattened_data = [flatten_job_data(job) for job in jobs_data]
    
    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)
    
    # Write to CSV with double quotes
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')

if __name__ == "__main__":
    input_file = "upwork_jobs.json"
    output_file = "upwork_jobs.csv"
    convert_json_to_csv(input_file, output_file)
