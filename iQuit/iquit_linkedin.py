from linkedin import linkedin
import il_auth
import rethinkdb as r
import datetime
import calendar

app = il_auth.getApp()
conn = r.connect(db = 'iquit')

def add_peeps():
    peeps = app.get_connections(selectors = ['id', 'first-name', 'last-name',
                                             'positions'] 
                                          )
    r.table('people').insert(peeps['values']).run(conn)

#add_peeps()

# figures out when the last update to their profile is
def find_updated_date():
    raw_vals = r.table('people')['id'].run(conn)
    not_found_yet = set(raw_vals)
    last_update = dict()
    for month in range(12,0,-1):
        cutoff = datetime.datetime(2014,12,24).utctimetuple()
        cutoff = calendar.timegm(cutoff)
        peeps = app.get_connections(selectors = ['id'],
                               params = {"modified": "updated",
                                          "modified-since": cutoff
                                          })
        print(len(peeps['values']))
        for person in peeps['values']:
            person_id = person[u'id']
            if person_id in not_found_yet:
                last_update[person_id] = cutoff
                not_found_yet.remove(person_id)

                #print(last_update)

find_updated_date()
