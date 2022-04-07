import sys
from mysql.connector import connect, Error
sys.path.append('/secrets')
from config import secrets

DBHOST = secrets['dbhostname']
DBUSER = secrets['dbuser']
DBPASS = secrets['dbpassword']
DBNAME = 'certcheck'

def buildserverlist():
    serverlist = []
    server = {}

    try:
        with connect(
            host=DBHOST,
            user=DBUSER,
            password=DBPASS,
            database=DBNAME
        ) as connection:
            serverlistq = "SELECT * FROM serverlist ORDER BY hostname ASC"
            with connection.cursor() as cursor:
                cursor.execute(serverlistq)
                result = cursor.fetchall()
                for row in result:
                    server = {'url': row[1], 'port': int(row[2])}
                    serverlist.append(server)
                    server = {}
            return(serverlist)
    except Error as e:
        print(f"Error: {e}")

def updatedb(query):
    #print(f'Would run "{query}"')
    try:
        with connect(host=DBHOST,
            user=DBUSER,
            password=DBPASS,
            database=DBNAME
        ) as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(query)
                cnx.commit()
    except Exception as e:
        result = f'FAIL: {e}'
        return result
    else:
        result = 'DB Updated.\n'
        return result

def add_endpoint(servername,port):
    print(f'Adding endpoint {servername}:{port} to the database...')
    query = f'INSERT INTO {DBNAME}.serverlist(hostname, port) VALUES ("{servername}", {port});'
    return updatedb(query)

def del_endpoint(servername,port):
    print(f'Deleting endpoint {servername}:{port} from the database...')
    query = f'DELETE FROM {DBNAME}.serverlist WHERE hostname="{servername}" AND port={port};'
    return updatedb(query)


if __name__ == "__main__":    
    websites = buildserverlist()
    print(websites)
