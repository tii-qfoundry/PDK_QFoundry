# use klayout.lay and klayout.db for standalone module
# https://www.klayout.de/forum/discussion/2269/image-to-gds-conversion


import pya as klay
import pya as kdb

ly = kdb.Layout()
ly.dbu = 0.001

top_cell = ly.create_cell("TOP")

image = klay.Image("")

# threshold
thr = 128

# pixel dimension in DBU (EDIT: comment was misleading)
pixel_size = int(0.5 + 0.1 / ly.dbu)

image_geo = kdb.Region()

for y in range(0, image.height()):
  on = False
  xstart = 0
  for x in range(0, image.width()):
    # take green (component 1) value for "intensity"
    value = image.get_pixel(x, y, 1) >= thr
    if value != on:
      on = value
      if on: 
        xstart = x
      else:
        image_geo.insert(kdb.Box(xstart, y, x, y + 1) * pixel_size)
  # EDIT: added these two lines
  if on: 
    image_geo.insert(kdb.Box(xstart, y, image.width(), y + 1) * pixel_size)

image_geo = image_geo.merged()

layer = ly.layer(1, 0)
top_cell.shapes(layer).insert(image_geo)

image_geo = image_geo.smoothed(pixel_size * 0.99)

layer = ly.layer(2, 0)
top_cell.shapes(layer).insert(image_geo)

#ly.write("converted.gds")