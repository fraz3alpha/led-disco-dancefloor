import pygtk
pygtk.require('2.0')
import gtk
import operator
import time
import string

class DrawingAreaExample:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Drawing Area Example")

        self.area = gtk.DrawingArea()
        self.area.set_size_request(24, 18)

        window.add(self.area)
        self.area.connect("expose-event", self.area_expose_cb)

        self.area.show()
        window.show()

    def area_expose_cb(self, area, event):

        style = self.area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        self.area.window.draw_rectangle(gc, False, 0, 0, 1, 1)

        print self.area.window
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, 20, 20)
        w,h = pixbuf.get_width(), pixbuf.get_height()
        drawable = gtk.gdk.Pixmap(None, w, h, 24)

        pixbuf.get_from_drawable(self.area.window,self.area.window.get_colormap(),0,0,0,0,w,h)
        print pixbuf.get_pixels_array()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DrawingAreaExample()
    main()
