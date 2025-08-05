import requests
import pandas as pd
from io import StringIO

# Step 1: Get raw markdown table from GitHub
url = "https://raw.githubusercontent.com/plchagnon/GRANTS/refs/heads/main/Deadlines.md"
response = requests.get(url)
md_text = response.text

# Step 2: Extract only the markdown table lines
def extract_table(md_text):
    lines = md_text.splitlines()
    table_lines = []
    in_table = False
    for line in lines:
        if line.strip().startswith('|'):
            table_lines.append(line)
            in_table = True
        elif in_table:
            break
    return '\n'.join(table_lines)

table_md = extract_table(md_text)

# Step 3: Parse markdown table into pandas DataFrame
df = pd.read_csv(StringIO(table_md), sep='|', skipinitialspace=True, engine='python')

# Remove empty first and last columns caused by markdown pipes
df = df.drop(columns=[df.columns[0], df.columns[-1]])

# Drop completely empty rows (if any)
df = df.dropna(how='all')

# convert to date time
df['Deadline'] = pd.to_datetime(df['Deadline'], format='%Y-%m-%d', errors='coerce')

today = pd.Timestamp.today().normalize()
overdue = df[(df['Deadline'].notna()) & (df['Deadline'] <= today)]
near_deadline_window = today + pd.Timedelta(days=7)

near = df[(df['Deadline'].notna()) & 
          (df['Deadline'] > today) & 
          (df['Deadline'] <= near_deadline_window)]

overdue.to_csv('overdue_deadlines.txt', sep='\t', index=False)
near.to_csv('near_deadlines.txt', sep = '\t', index=False)

