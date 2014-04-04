import gtk
import gobject

pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, 5, 5)

w,h = pixbuf.get_width(), pixbuf.get_height()
drawable = gtk.gdk.Pixmap(None, w, h, 24)
drawable.set_colormap
gc = drawable.new_gc()
drawable.draw_pixbuf(gc, pixbuf, 0,0,0,0,-1,-1)

#---ACTUAL DRAWING CODE---
# Red!
#gc.set_rgb_fg_color(gtk.gdk.Color(0x0, 0x0, 0x0))
#gc.set_rgb_fg_color(gtk.gdk.Color(0xFF, 0xFF, 0x0))
gc.set_foreground(gtk.gdk.Color(0xFF, 0xFF, 0xFF))
gc.set_background(gtk.gdk.Color(0xFF, 0xFF, 0xFF))
for x in range(5):
  for y in range(5):
    drawable.draw_point(gc, x, y)

#Black
#gc.set_rgb_fg_color(gtk.gdk.Color(0x0, 0x0, 0x0))
#gc.set_rgb_fg_color(gtk.gdk.Color(0xFF, 0xFF, 0x0))
#drawable.draw_rectangle(gc, True, 0,0, w,h)

#-------------------------

cmap = gtk.gdk.Colormap(gtk.gdk.visual_get_best(), False)
pixbuf.get_from_drawable(drawable,cmap,0,0,0,0,w,h)

print pixbuf.get_pixels_array()

