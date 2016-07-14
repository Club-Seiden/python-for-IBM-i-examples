import argparse
import ibm_db   # To install on the IBM i execute
                # easy_install3 /QOpenSys/QIBM/ProdData/OPS/Python-pkgs/ibm_db/ibm_db-2.0.5.2-py3.4-os400-powerpc.egg
                # Make sure you install 5733OPS-SI58194 and that you have
                # ibm_db-2.0.5.2 not ibm_db-2.0.5.1

import platform
import sys
from tabulate import tabulate # pip install tabulate --user


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Display netstat information.')
    parser.add_argument('--limit', type=int,
        help='Only show X rows')
    parser.add_argument('--offset', type=int,
        help='Skip first X rows')
    parser.add_argument('--port', type=int,
        help='Look for only local port')
    args = parser.parse_args()

    cn = ibm_db.connect('dbname', 'myuser', 'mypass', {})
    sql = '''
SELECT
        REMOTE_ADDRESS, REMOTE_PORT, REMOTE_PORT_NAME,
        LOCAL_ADDRESS, LOCAL_PORT, LOCAL_PORT_NAME,
        CONNECTION_TYPE,
        TRIM(AUTHORIZATION_NAME) AS AUTHORIZATION_NAME, JOB_NAME, SLIC_TASK_NAME
    FROM QSYS2.NETSTAT_JOB_INFO
    {0} -- WHERE CLAUSE
    ORDER BY LOCAL_PORT, LOCAL_ADDRESS, REMOTE_PORT,  REMOTE_ADDRESS
'''
    sql = sql.format("WHERE LOCAL_PORT = ?") if  args.port is not None else sql.format('')
    params = (args.port,) if args.port is not None else None
    if args.limit is not None:
        sql += "\n    LIMIT {0}".format(args.limit)
    if args.offset is not None:
        sql += "\n    OFFSET {0}".format(args.offset)

    netstat_stmt = ibm_db.prepare(cn, sql)
    ibm_db.execute(netstat_stmt, params)
    row = ibm_db.fetch_assoc(netstat_stmt)
    if row:
        rows = [row]
        while row != False:
            rows.append(row)
            row = ibm_db.fetch_assoc(netstat_stmt)
        print(tabulate(rows, 'keys'))
    ibm_db.close(cn)
