import mysql.connector

def connectDB():
  conn = mysql.connector.connect(user="threesixthreedb", 
                               password="Jd19_m_20k02",
                               host="den1.mysql6.gear.host",
                               database="threesixthreedb")
  return conn
  
c = connectDB()
mc = c.cursor()
mc.execute("select table_name from information_schema.tables where table_schema = 'threesixthreedb'")
results = mc.fetchall()
for res in results:
 print(res)
mc.close()
c.close()
