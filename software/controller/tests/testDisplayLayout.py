__authors__ = ['Joel Wright']

import os
import sys
import yaml
import unittest

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)

from layout import DisplayLayout

#### Test Data ####
config1 = """
  1:
    width: 8
    height: 6
    x_position: 0
    y_position: 0
    orientation: N

  2:
    width: 8
    height: 6
    x_position: 0
    y_position: 6
    orientation: N

  3:
    width: 8
    height: 6
    x_position: 8
    y_position: 0
    orientation: E

  4:
    width: 8
    height: 6
    x_position: 8
    y_position: 8
    orientation: S
    """

layout1 = """   0    1    2    3    4    5    6    7  103  111  119  127  135  143 None None 
   8    9   10   11   12   13   14   15  102  110  118  126  134  142 None None 
  16   17   18   19   20   21   22   23  101  109  117  125  133  141 None None 
  24   25   26   27   28   29   30   31  100  108  116  124  132  140 None None 
  32   33   34   35   36   37   38   39   99  107  115  123  131  139 None None 
  40   41   42   43   44   45   46   47   98  106  114  122  130  138 None None 
  48   49   50   51   52   53   54   55   97  105  113  121  129  137 None None 
  56   57   58   59   60   61   62   63   96  104  112  120  128  136 None None 
  64   65   66   67   68   69   70   71  191  190  189  188  187  186  185  184 
  72   73   74   75   76   77   78   79  183  182  181  180  179  178  177  176 
  80   81   82   83   84   85   86   87  175  174  173  172  171  170  169  168 
  88   89   90   91   92   93   94   95  167  166  165  164  163  162  161  160 
None None None None None None None None  159  158  157  156  155  154  153  152 
None None None None None None None None  151  150  149  148  147  146  145  144 
"""
#### End Test Data ####

class TestDisplayLayout(unittest.TestCase):
	def setUp(self):
		self.config = yaml.load(config1)
		self.layout = layout1
	
	def test_layout_mapping(self):
		display_layout = DisplayLayout(self.config)
		self.assertEqual(display_layout.draw_layout(), self.layout)
		
# Start the tests
if __name__ == "__main__":
	unittest.main()


