import yaml
import pprint

def load():
  f = open('config.yaml')
  data = yaml.load(f)
  f.close

  pp = pprint.PrettyPrinter()
  pp.pprint(data)
  return data
