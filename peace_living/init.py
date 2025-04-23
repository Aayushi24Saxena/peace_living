import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'aayushis',
    'password': 'Toh5UBah'
}

conn = mysql.connector.connect(**db_config)
cur = conn.cursor()



# Tables
cur.execute("""
CREATE TABLE IF NOT EXISTS Building (
    BuildingId VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(50),
    Address VARCHAR(100),
    HasAC BOOLEAN,
    HasDining BOOLEAN
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Room (
    RoomNumber INT,
    BuildingId VARCHAR(10),
    NumBedrooms INT,
    PrivateBathrooms BOOLEAN,
    HasKitchen BOOLEAN,
    HasAC BOOLEAN,
    HasDining BOOLEAN,
    PRIMARY KEY (BuildingId, RoomNumber),
    FOREIGN KEY (BuildingId) REFERENCES Building(BuildingId)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Student (
    StudentId INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50),
    WantsAC BOOLEAN,
    WantsDining BOOLEAN,
    WantsKitchen BOOLEAN,
    WantsPrivateBathroom BOOLEAN
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Assignment (
    StudentId INT,
    BuildingId VARCHAR(10),
    RoomNumber INT,
    PRIMARY KEY (StudentId),
    FOREIGN KEY (StudentId) REFERENCES Student(StudentId),
    FOREIGN KEY (BuildingId, RoomNumber) REFERENCES Room(BuildingId, RoomNumber)
)
""")

# Insert sample data
cur.executemany("""
INSERT INTO Building (BuildingId, Name, Address, HasAC, HasDining)
VALUES (%s, %s, %s, %s, %s)
""", [
    ("B1", "Maple Hall", "123 College Rd", True, True),
    ("B2", "Creekside", "Wells Rd", False, True),
    ("B3", "Oak Hall", "456 Campus Dr", False, True),
    ("B4", "Pine Hall", "789 Dorm Ln", True, False),
    ("B5", "WaterColors", "1 Mile Rd", True, True)
])

cur.executemany("""
INSERT INTO Room (RoomNumber, BuildingId, NumBedrooms, PrivateBathrooms, HasKitchen, HasAC, HasDining)
VALUES (%s, %s, %s, %s, %s, %s, %s)
""", [
    (101, "B1", 2, True, True, True, True),
    (102, "B1", 3, False, False, False, True),
    (201, "B2", 1, True, True, True, False),
    (202, "B2", 2, False, False, False, False),
    (301, "B3", 2, True, False, True, False),
    (302, "B3", 3, False, True, False, True),
    (303, "B3", 1, False, False, True, True),
    (401, "B1", 2, True, True, True, True),
    (501, "B2", 1, False, True, False, True),
    (104, "B4", 1, True, False, True, True),
    (502, "B5", 1, True, True, False, False)
])

cur.executemany("""
INSERT INTO Student (Name, WantsAC, WantsDining, WantsKitchen, WantsPrivateBathroom)
VALUES (%s, %s, %s, %s, %s)
""", [
    ("Alicia", True, True, False, True),
    ("Ved", True, True, False, False),
    ("Bryan", False, True, True, False),
    ("Raj", True, False, False, True),
    ("Charlie", True, False, True, True),
    ("Kiara", True, True, False, True),
    ("Nola", True, True, True, True),
    ("Zane", False, False, False, False),
    ("Maya", True, True, True, True),
    ("Duy", False, False, True, False),
    ("Tara", True, False, False, False)
])

cur.executemany("""
INSERT INTO Assignment (StudentId, BuildingId, RoomNumber) 
VALUES(%s, %s, %s)
""", [
   (1, "B1", 101),
   (3, "B2", 201),
   (4, "B2", 202),
   (5, "B3", 301)
])

conn.commit()
cur.close()
conn.close()
print("Database initialized successfully.")
