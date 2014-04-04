__author__ = 'Joel Wright'

import gtk
import math
import cairo
import struct
import pygtk
pygtk.require('2.0')

class DrawingAreaExample(gtk.Window):
    def __init__(self):
        super(DrawingAreaExample, self).__init__()

        self.set_title("Drawing Area Example")
        self.resize(300,400)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 300, 300)
        self.draw_to_surface()

        area = gtk.DrawingArea()
        area.set_size_request(300, 300)
        area.connect("expose-event", self.expose)

        show_button = gtk.Button("dump")
        show_button.connect("clicked", self.dump_pixmap)

        fixed = gtk.Fixed()
        fixed.put(area, 0, 0)
        fixed.put(show_button, 20, 320)

        self.add(fixed)

        self.show_all()

    def expose(self, widget, event):

        cr = widget.window.cairo_create()
        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()

    def draw_to_surface(self):

        cr = cairo.Context(self.surface)

        cr.set_line_width(9)
        cr.set_source_rgb(0.7, 0.2, 0.0)

        w = self.surface.get_width()
        h = self.surface.get_height()

        cr.translate(w/2, h/2)
        cr.arc(0, 0, 50, 0, 2*math.pi)
        cr.stroke_preserve()

        cr.set_source_rgb(0.3, 0.4, 0.6)
        cr.fill()

    def dump_pixmap(self, widget):
        d = self.surface.get_data()
        self.print_buffer(d)

    def print_buffer(self, data):
        s = ""
        coord = 0
        row = 1
        stride = self.surface.get_stride()

        while coord < len(data):
            b = struct.unpack('B',data[coord])
            g = struct.unpack('B',data[coord+1])
            r = struct.unpack('B',data[coord+2])
            coord += 4
            if (coord / row) > stride:
                row += 1
                s += '(%d,%d,%d)\n' % (r[0], g[0], b[0])
            else:
                s += '(%d,%d,%d) ' % (r[0], g[0], b[0])

        print s

DrawingAreaExample()
gtk.main()