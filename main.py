from random import randint

def coordinate_permutations(x_arr, y_arr) -> list:
	perms = []
	for x in x_arr:
		for y in y_arr:
			perms.append((x, y))
	return perms

class TileMap:
	def __init__(self, rows:int, columns:int, modifiers:list['TileMap']=[], default_val:int=0):
		self.table = [[default_val for x in range(columns)].copy() for y in range(rows)]
		self.rows = rows
		self.columns = columns
		self.modifiers = modifiers

	def get_neighbours(self, coordinates:tuple) -> list:
		#this is now ugly af
		x, y = coordinates[0:2]
		neighbour_coords = []
		if y-1 >= 0:
			neighbour_coords.append((x, y-1))
		if y+1 < self.rows:
			neighbour_coords.append((x, y+1))
		if x-1 >= 0:
			neighbour_coords.append((x-1, y))
		if x+1 < self.columns:
			neighbour_coords.append((x+1, y))
		return neighbour_coords
		#diagonal movement
		'''x, y = coordinates[0:2]
		bounds = (max(0, x-1), min(x+2, self.columns), max(0, y-1), min(y+2, self.rows))
		neighbour_coords = coordinate_permutations(
        	list(range(bounds[0], bounds[1])), 
        	list(range(bounds[2], bounds[3])))
		neighbour_coords.remove((x, y))
		return neighbour_coords'''
		#neighbouring_rows = self.table[bounds[2]:bounds[3]+1]
		#neighbouring_vals = map(lambda x: x[bounds[0]:bounds[1]+1], neighbouring_rows

	def get_weight(self, coordinates) -> int:
		x, y = coordinates
		aggregate = 0
		if self.modifiers:
			for modifier in self.modifiers:
				aggregate += modifier.table[y][x]

		aggregate += self.table[y][x]
		return aggregate

	def apply_modifier_layer(self, modifier):
		for row in self.table:
			for column in row:
				self.table[row][column] += modifier[row][column]
	
	def add_modifier_layer(self, modifier:'TileMap'):
		self.modifiers.append(modifier)

	def gen_modifier_layer(self, modifier_amount, num_tiles):
		for i in range(num_tiles):
			x = randint(0, self.columns-1)
			y = randint(0, self.rows-1)
			self.table[y][x] = modifier_amount

	def print_with_colour(self, value, bonus=[], x=None, y=None):
		if value > 1:
			colour = 32
		else: 
			colour = 39

		if (x, y) in bonus:
			colour = 34

		if value < 10:
			print(f'\x1b[1;{colour}m{value}\x1B[0m ', end='')
		else:
			print(f'\x1b[1;31mX\x1B[0m ', end='')
		
	def print_table(self, bonus_colouring:list=[]):
		for y, row in enumerate(self.table):
			for x, item in enumerate(row):
				self.print_with_colour(self.get_weight((x, y)), bonus_colouring, x, y)
				#print(' ', end='')
			print('')
			#print([self.get_weight((x, index)) if self.get_weight((x, index))<10 else 'x' for x in row])

def find_sub_array(conditions:list, arr:list) -> list[int]:
	'''
	Takes an array of conditions, where None will match anything, 
	and returns all indices of the original arr that match the conditions 
	'''
	#This could probably be done with regex in a single filter
	indices = [i for i, x in enumerate(conditions) if x == None]
	indices.sort(reverse=True)
	to_return = []
	comparison_arr = list(filter(lambda x: x!=None, conditions))
	cut_down_arr = arr
	for index in indices:
		cut_down_arr = list(map(lambda x: x[:index] + x[index+1:], cut_down_arr))
	for index, sub_arr in enumerate(cut_down_arr):
		if sub_arr == comparison_arr:
			to_return.append(index)
	
	return to_return

def dijkstra(source:tuple, dest:tuple, tiles:TileMap):
	#to_visit is an array where the contents are (x, y, total_weight, predecessor)
	visited = []
	initial = [source[0], source[1], 0, []]
	to_visit = [initial]
	while to_visit:
		to_visit.sort(key=lambda x: x[2], reverse=True)
		current = to_visit.pop()
		visited.append(current)
		neighbours = tiles.get_neighbours(current)
		for neighbour in neighbours:
			weight = tiles.get_weight(neighbour)
			if neighbour[0] == dest[0] and neighbour[1] == dest[1]:
				#bingo
				return current[2]+ weight, current[3] + [(current[0], current[1]), (dest[0], dest[1])]
			matches = find_sub_array([neighbour[0], neighbour[1], None, None], to_visit)
			has_visited = find_sub_array([neighbour[0], neighbour[1], None, None], visited)
			#print(bool(has_visited))
			#print(to_visit,visited)
			
			if matches:
				if to_visit[matches[0]][2] > weight + current[2]:
					to_visit[matches[0]][2] = weight + current[2]
					to_visit[matches[0]][3] += current[3] + [(current[0], current[1])]
			else:
				if not has_visited:
					to_visit.append(
						[neighbour[0], neighbour[1], weight+current[2], current[3] + [(current[0], current[1])]])
			
	#enable this for shortest dist to all tiles
	#for visit in visited:
		#print(visit[0], visit[1], visit[2])
	return "no path found"#visited[find_sub_array([dest[0], dest[1], None, None], visited)[0]][2], visited[find_sub_array([dest[0], dest[1], None, None], visited)[0]][3] + [(dest[0], dest[1])]
			#input('')

def find_path(source:tuple, dest:tuple, tiles:TileMap, rain=None):
	if rain:
		tiles.apply_modifier_layer(tiles, rain)
	path = dijkstra(source, dest, tiles)
	return path

map_size = (25, 25)

tiles = TileMap(map_size[0],map_size[1], default_val=1)

mountains = TileMap(map_size[0],map_size[1])
mountains.gen_modifier_layer(9999, 200)

forests = TileMap(map_size[0],map_size[1])
forests.gen_modifier_layer(1, 300)

tiles.add_modifier_layer(mountains)
tiles.add_modifier_layer(forests)

start = (randint(0,map_size[0]-1), randint(0,map_size[1]-1))
end = start
while end == start:
	end = (randint(0,map_size[0]-1), randint(0,map_size[1]-1))

path = find_path(start, end, tiles)

tiles.print_table(path[1])

print(f'Starting at {start} and moving to {end} will take {path[0]} turns')