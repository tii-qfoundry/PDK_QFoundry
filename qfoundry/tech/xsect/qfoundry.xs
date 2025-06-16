#	QFoudnry PDK xsection

# input layers:

wg = layer("130/1")

# cross section calculations

# thickness of the stack
height(7.5)
depth(4)
substrate = bulk

al_pos = grow(0.3)
etch_al= wg 

etch_angle = 3
mask(etch_al).etch(0.3, :taper => etch_angle, :bias =>  0, :into => al_pos) 

al_oxide = mask(wg).grow(0.01, lateral=0.01, mode = 'round') 

# output

layers_file(File.join(File.expand_path(File.dirname(__FILE__),'..'), "qfoundry.lyp"))
output("300/0", bulk)
output("301/0", al_pos)
output("302/0", al_oxide)
