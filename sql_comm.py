import sqlite3
PATH_DB = "/Users/pcsishun/project_envalic/17d_control/17d_backend/hlr_db.db"
conn = sqlite3.connect(PATH_DB)

cursor = conn.cursor()

# data =cursor.execute("""
#     SELECT * FROM state_hlr
#     """).fetchall()


# data2 =cursor.execute("""
#     SELECT * FROM setting_control
#     """).fetchall()



cursor.execute(""" DROP TABLE sensor_data_exhaust  """)
conn.commit()
# conn.close()

cursor.execute(""" DROP TABLE sensor_data_interlock  """)
conn.commit()
conn.close()
# data3 =cursor.execute("""   SELECT * FROM hlr_sensor_data LIMIT 10 """).fetchall()

# list_table = cursor.execute(""" PRAGMA table_info(hlr_sensor_data) """).fetchall()
# #columns = cursor.fetchall()

# list_table_db = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
# print(data, "\n")



# print(data2 ,"\n")


# print(data3, "\n")


# print(list_table)