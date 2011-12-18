import shapefile

class LonLat2NUTS:

	def __init__(self, level=3):
		self.shp_src = "nuts2-shapefile/data/NUTS_RG_10M_2006"
		self.stat_level = level
		self.init_polygons()
		self.atan2cnt = 0

	def resolve(self, lon, lat, iso=None):
		if iso == None:
			iso = self.ll2nuts(lon,lat,level=0)
		nuts = iso
		for i in range(1,self.stat_level+1):
			nuts = self.ll2nuts(lon, lat, nuts, i)
		return nuts

	def ll2nuts(self, lon, lat, parent=None, level=None):
		"""
		returns NUTS code for this point
		"""
		if level == None:
			level = self.stat_level
		polygons = self.polygons[level]
		nuts_ids = self.nuts_ids[level]
		
		for i in range(len(polygons)):
			poly = polygons[i]
			nuts = nuts_ids[i]
			
			if parent != None and parent != nuts[:len(parent)]:
				# not the same parent, so skip this
				continue
			
			for j in range(len(poly)):
				contour = poly[j]
				if self.is_inside(contour, (lon,lat)):
					return nuts
			
		# lets find the nearest polygon
		global_min_dist = 9999999999999
		globel_nearest_ll = None
		nearest_poly = -1
		
		for i in range(len(polygons)):
			min_dist = 9999999999999
			nearest_ll = None
			poly = polygons[i]
			nuts = nuts_ids[i]
			if iso != None and iso != nuts[:2]:
				# not the same country, so skip this
				continue
				
			for j in range(len(poly)):
				contour = poly[i]
				for x,y in contour:
					dx = x - lon
					dy = y - lat
					dist = dx*dx + dy*dy
					if dist < min_dist:
						min_dist = dist
						nearest_ll = (x,y)
		
			if min_dist < global_min_dist:
				global_min_dist = min_dist
				nearest_poly = i
				
		nuts = nuts_ids[nearest_poly]
		return nuts

	def init_polygons(self):
		sf = shapefile.Reader(self.shp_src)
		recs = sf.records()
		self.polygons = polygons = {}
		self.nuts_ids = nuts_ids = {}
		stat_levels = range(self.stat_level+1)
		for sl in stat_levels:
			polygons[sl] = []
			nuts_ids[sl] = []
			for i in range(len(recs)):
				rec = recs[i]
				o_id,nuts_id,stat_level, area, le, shp_leng, shp_area = rec
				if stat_level == sl:
					nuts_ids[sl].append(nuts_id)
					shp = sf.shapeRecord(i).shape
					polygons[sl].append(self.shape_to_poly(shp))

	
	def shape_to_poly(self, shp):
		parts = shp.parts
		parts.append(len(shp.points))
		poly = []
		for j in range(len(parts)-1):
			pts = shp.points[parts[j]:parts[j+1]]
			poly.append(pts)
		return poly


	def is_inside(self, polygon, p):
		from math import atan2,pi
		twopi = pi*2
		n = len(polygon)
		angle = 0
		for i in range(n):
			x1,y1 = (polygon[i][0] - p[0], polygon[i][1] - p[1])
			x2,y2 = (polygon[(i+1)%n][0] - p[0], polygon[(i+1)%n][1] - p[1])
			theta1 = atan2(y1,x1)
			theta2 = atan2(y2,x2)
			self.atan2cnt += 2
			dtheta = theta2 - theta1
			while dtheta > pi:
				dtheta -= twopi
			while dtheta < -pi:
				dtheta += twopi
			angle += dtheta
		return abs(angle) >= pi


if __name__ == '__main__':
	from datetime import datetime
	
	ll2nuts = LonLat2NUTS(3)
	t0 = datetime.now()
	print ll2nuts.ll2nuts(11.619987,52.1271,'DE')
	t1 = datetime.now()
	print (t1-t0).microseconds/1000.0,'ms'

	# faster (for nuts-level below 2):
	print ll2nuts.resolve(11.619987,52.1271,'DE')
	t2 = datetime.now()
	print (t2-t1).microseconds/1000.0,'ms'
	
	

