import pandas as pd
import pymysql
import creds

# Load the sampled data
df = pd.read_csv('sampled_turing_data.csv')

# Connect to RDS
connection = pymysql.connect(
    host=creds.host,
    user=creds.user,
    password=creds.password,
    db=creds.db,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 1. Clear existing data (be careful with this in production!)
        # We delete in order of dependencies
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Snippets;")
        cursor.execute("TRUNCATE TABLE Authors;")
        cursor.execute("TRUNCATE TABLE Categories;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # 2. Seed Categories (Just one for now)
        cursor.execute("INSERT INTO Categories (CategoryName) VALUES ('General Content');")
        category_id = cursor.lastrowid
        
        # 3. Seed Authors (All unique models in our CSV)
        unique_models = df['model'].unique()
        model_to_id = {}
        for model in unique_models:
            is_ai = 0 if model == 'wikipedia' else 1
            cursor.execute("INSERT INTO Authors (AuthorName, IsAI) VALUES (%s, %s);", (model, is_ai))
            model_to_id[model] = cursor.lastrowid
            
        # 4. Seed Snippets (Bulk insert for speed)
        sql = "INSERT INTO Snippets (SnippetText, CategoryID, AuthorID) VALUES (%s, %s, %s);"
        
        # We'll insert in batches of 100
        batch = []
        for index, row in df.iterrows():
            # Truncate text if it's extremely long for the DB column (TEXT is ~64KB)
            text = str(row['data'])[:60000] 
            author_id = model_to_id[row['model']]
            batch.append((text, category_id, author_id))
            
            if len(batch) >= 100:
                cursor.executemany(sql, batch)
                batch = []
        
        if batch:
            cursor.executemany(sql, batch)
            
        connection.commit()
        print(f"Successfully seeded {len(df)} snippets and {len(unique_models)} authors into RDS!")

finally:
    connection.close()
