LEGACY_CODE_SAMPLES = [
    {
        "id": "syntax_001",
        "description": "Basic Python 2 patterns",
        "code": '''
import urllib2
import cPickle as pickle

def fetch_inventory(url):
    try:
        response = urllib2.urlopen(url)
        data = response.read()
        return pickle.loads(data)
    except urllib2.URLError, e:
        print "Error fetching inventory:", e
        return {}

def calculate_total(items):
    total = 0
    for item, qty in items.iteritems():
        price = item.get("price", 0)
        total += price * qty
    print "Total: $%d" % total
    return total

class InventoryManager(object):
    def __init__(self):
        self.items = {}

    def add_item(self, name, qty):
        if not isinstance(name, unicode):
            name = unicode(name, "utf-8")
        self.items[name] = qty

    def remove_item(self, name):
        if self.items.has_key(name):
            del self.items[name]

    def divide_stock(self, name, parts):
        qty = self.items.get(name, 0)
        return qty / parts
'''
    },
    {
        "id": "syntax_002",
        "description": "File I/O and exception handling",
        "code": '''
def read_config(filepath):
    try:
        f = open(filepath, "r")
        content = f.read()
        f.close()
        return content
    except IOError, e:
        print "Cannot open file: %s" % str(e)
        return None

def process_records(records):
    output = []
    for i, record in enumerate(records):
        print "Processing record %d of %d..." % (i+1, len(records))
        if record.has_key("active") and record["active"]:
            name = record.get("name", u"Unknown")
            value = record.get("value", 0)
            output.append(u"%s=%d" % (name, value))
    return output
'''
    }
]