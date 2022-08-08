import util
import data_central as dc
import time

url = "http://192.168.1.183/read/"

data = dc.get_data_from_url(url)
util.print_dict(data)
