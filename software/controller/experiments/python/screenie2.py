import gtk

image = gtk.Image()
pixmap,mask = pixbuf.render_pixmap_and_mask() # Function call
cm = pixmap.get_colormap()
red = cm.alloc_color('red')
gc = pixmap.new_gc(foreground=red)
pixmap.draw_line(gc,0,0,w,h)
image.set_from_pixmap(pixmap,mask)

print pixbuf.get_pixels_array()
