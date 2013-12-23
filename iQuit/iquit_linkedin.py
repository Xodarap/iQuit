from linkedin import linkedin
import il_auth
import rethinkdb as r

app = il_auth.getApp()
conn = r.connect(db = 'iquit')

def add_peeps():
    peeps = app.get_connections(selectors = ['id', 'first-name', 'last-name',
                                         'positions'])
    r.table('people').insert(peeps['values']).run(conn)

# figures out when the last update to their profile is
def find_updated_date():
    print(r.table('people').map(lambda x: x['id']).run(conn))

find_updated_date()
