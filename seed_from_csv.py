import csv
import pymysql
import creds
import sys

# Load the sampled data using the built-in csv module (Very lightweight)
def seed_database():
    try:
        connection = pymysql.connect(
            host=creds.host,
            user=creds.user,
            password=creds.password,
            db=creds.db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to RDS!")
    except Exception as e:
        print(f"Error connecting to RDS: {e}")
        return

    try:
        with connection.cursor() as cursor:
            # 1. Clear existing data
            print("Clearing old data...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE Snippets;")
            cursor.execute("TRUNCATE TABLE Authors;")
            cursor.execute("TRUNCATE TABLE Categories;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
            # 2. Seed 'General' Category
            cursor.execute("INSERT INTO Categories (CategoryName) VALUES ('General Content');")
            category_id = cursor.lastrowid
            
            # 3. Open CSV and process
            print("Reading 'sampled_turing_data.csv'...")
            with open('sampled_turing_data.csv', mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # First pass: Get unique models and seed Authors
                models = {} # name -> id
                rows = []
                for row in reader:
                    model_name = row['model']
                    if model_name not in models:
                        is_ai = 0 if model_name == 'wikipedia' else 1
                        cursor.execute("INSERT INTO Authors (AuthorName, IsAI) VALUES (%s, %s);", (model_name, is_ai))
                        models[model_name] = cursor.lastrowid
                    rows.append(row)

                print(f"Seeded {len(models)} authors: {list(models.keys())}")

                # 4. Seed Snippets (Batch insert)
                sql = "INSERT INTO Snippets (SnippetText, CategoryID, AuthorID) VALUES (%s, %s, %s);"
                batch = []
                count = 0
                
                for r in rows:
                    text = r['data'][:60000] # Truncate for safety
                    author_id = models[r['model']]
                    batch.append((text, category_id, author_id))
                    
                    if len(batch) >= 100:
                        cursor.executemany(sql, batch)
                        count += len(batch)
                        batch = []
                
                if batch:
                    cursor.executemany(sql, batch)
                    count += len(batch)
                
            connection.commit()
            print(f"SUCCESS! Seeded {count} snippets into RDS.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    seed_database()
