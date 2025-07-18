import shutil
from pathlib import Path
from dbms.storage import StorageEngine

if __name__ == "__main__":
    db_dir = Path("manual_db")
    if db_dir.exists():
        shutil.rmtree(db_dir)
    db_dir.mkdir(exist_ok=True)
    engine = StorageEngine(str(db_dir))

    dbs = ["test_db1", "test_db2"]
    tables = [
        (
            "users",
            [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "nullable": False,
                    "primary_key": True,
                },
                {"name": "name", "type": "VARCHAR(20)", "nullable": False},
                {"name": "age", "type": "INTEGER", "nullable": False},
                {"name": "email", "type": "VARCHAR(50)", "nullable": False},
            ],
        ),
        (
            "orders",
            [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "nullable": False,
                    "primary_key": True,
                },
                {"name": "user_id", "type": "INTEGER", "nullable": False},
                {"name": "amount", "type": "FLOAT", "nullable": False},
                {"name": "status", "type": "VARCHAR(20)", "nullable": False},
            ],
        ),
    ]

    for db_name in dbs:
        engine.create_database(db_name)
        for table_name, columns in tables:
            engine.create_table(db_name, table_name, columns)
            if table_name == "users":
                rows = [
                    {
                        "id": i,
                        "name": f"User{i}",
                        "age": 20 + i,
                        "email": f"user{i}@example.com",
                    }
                    for i in range(1, 11)
                ]
            else:  # orders
                rows = [
                    {
                        "id": i,
                        "user_id": (i % 10) + 1,
                        "amount": float(100 + i),
                        "status": "shipped" if i % 2 == 0 else "pending",
                    }
                    for i in range(1, 11)
                ]
            engine.append_rows(db_name, table_name, rows)
    print(f"Manual DB created at: {db_dir.resolve()}")
    print("You can now manually inspect the files in this directory.")
    input("Press Enter to finish the test and leave the files in place...")
