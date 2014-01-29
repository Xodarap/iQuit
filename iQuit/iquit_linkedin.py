from linkedin import linkedin
import il_auth
import rethinkdb as r
from datetime import datetime
import calendar
from dict_compare import dict_compare

app = il_auth.getApp()
conn = r.connect(db = 'iquit')

# all of the fields we can get with r_basic permission
basic_fields = ['id','first-name','last-name','headline','location',
                'industry', 'current-share', 'summary',
                'specialties', 'positions', 'picture-url']

def add_peeps():
    '''Outer loop to add profiles'''
    #peeps = app.get_connections(selectors = ['id', 'first-name', 'last-name',
    #                                         'positions'] 
    #                                      )
    now_inst = str(datetime.now())
    page_size = 25
    pages = 40
    offset = 4
    for start_page in range(offset * page_size, page_size * pages, page_size):
        peeps = app.search_profile(selectors = [{'people': ['id']}],
                                   params = {'company-name': 'amazon',
                                             'current-company': 'true',
                                             'count': page_size,
                                             'start': start_page})
        put_peeps_in(peeps, now_inst)
    

def put_peeps_in(peeps, now_inst = str(datetime.now())):
    '''Does a diff and adds any new profiles'''
    peeps = peeps['people']['values']
    def get_profile(person):
        profile = {}
        profile['data'] = app.get_profile(person['id'], selectors = basic_fields)
        query = r.table('people_overtime').filter({'id': person['id']}).order_by('instant')
        old_profile = query[0].run(conn)['data'] if query.count().run(conn) > 0 else {} 
        if dict_compare(profile['data'], old_profile): 
            return None
        else:
            profile['instant'] = now_inst
            profile['id'] = person['id']
            profile['id_instant'] = profile['id'] + '^' + profile['instant']
            return profile

    peeps = map(get_profile, peeps)
    peeps = filter(lambda x: x != None, peeps)
    r.table('people_overtime').insert(peeps).run(conn)
    return (peeps)


#add_peeps()

# figures out when the last update to their profile is
def find_updated_date():
    raw_vals = r.table('people')['id'].run(conn)
    not_found_yet = set(raw_vals)
    last_update = dict()
    for month in range(12,0,-1):
        cutoff = datetime(2013,month,1).utctimetuple()
        cutoff = calendar.timegm(cutoff) * 1000  # linkedin uses milliseconds
        print(cutoff)
        peeps = app.get_connections(selectors = ['id'],
                               params = {"modified": "updated",
                                          "modified-since": cutoff
                                          })
        # no one updated since then
        if not ('values' in peeps):
            continue

        for person in peeps['values']:
            person_id = person[u'id']
            if person_id in not_found_yet:
                last_update[person_id] = cutoff
                r.table('people').get(person_id).update({'last_update': cutoff}).run(conn)
                not_found_yet.remove(person_id)

    #print(set(last_update.values()))

#find_updated_date()
