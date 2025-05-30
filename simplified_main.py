from random import randint

class TileMap:
	def __init__(self, rows:int, columns:int, modifiers:list['TileMap']=[], default_val:int=0):
		#Generate a table rows tall and columns wide where each cell is default_val
		self.table = [[default_val for x in range(columns)].copy() for y in range(rows)]
		self.rows = rows
		self.columns = columns
		self.modifiers = modifiers

	def get_neighbours(self, coordinates:tuple) -> list:
		'''Returns a list of all valid orthagonally adjacent tiles'''
		#Neighbours are up, down, left, and right of the provided tile
		#Checks if any of those positions would be out of bounds
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

	def get_weight(self, coordinates:tuple) -> int:
		'''Returns the weight/terrain at coordinate (coordinates)'''
		x, y = coordinates
		aggregate = 0
		#If there are any overlay TileMaps
		if self.modifiers:
			for modifier in self.modifiers:
				#Then add those into the total weight
				aggregate += modifier.table[y][x]
		#Add in the original TileMap's weight
		aggregate += self.table[y][x]
		return aggregate

	def apply_modifier_layer(self, modifier:'TileMap'):
		#Permanently applies an overlay to a TileMap
		for row in self.table:
			for column in row:
				self.table[row][column] += modifier[row][column]
	
	def add_modifier_layer(self, modifier:'TileMap'):
		self.modifiers.append(modifier)

	def remove_modifier_layer(self):
		'''Removes the last added modifier'''
		self.modifiers.pop()

	def gen_modifier_layer(self, modifier_amount:int, num_tiles:int):
		'''Generate num_tiles many tiles at random positions with weights of modifier_amount'''
		for i in range(num_tiles):
			x = randint(0, self.columns-1)
			y = randint(0, self.rows-1)
			self.table[y][x] = modifier_amount

	#These two functions are purely for visual display of the pathing
	def print_with_colour(self, value, bonus=[], x=None, y=None):
		#If the weight is > 1, will print as green
		if value == 2:
			colour = 32
		elif value > 2:
			colour = 35
		#Else print as default colour
		else: 
			colour = 39
		#If the current position is in the additional bonus list, set to blue
		#(Used for highlighting the path)
		if (x, y) in bonus:
			colour = 34

		#If the weight isn't single digit, replace with an X to maintain "monospacing"
		if value < 10:
			print(f'\x1b[1;{colour}m{value}\x1B[0m ', end='')
		else:
			print(f'\x1b[1;31mX\x1B[0m ', end='')
		
	def print_table(self, bonus_colouring:list=[]):
		#Print each value in the table
		#Each row is separated by a newline
		for y, row in enumerate(self.table):
			for x, item in enumerate(row):
				self.print_with_colour(self.get_weight((x, y)), bonus_colouring, x, y)
			print('')

def dijkstra(source:tuple, dest:tuple, tiles:'TileMap') -> list:
	'''Given a source coordinate, a destination coordinate, and a TileMap, 
	will spit out the minimum weight and the path that weight represents in the form of (weight, [list of coords])'''

	def get_weight(node:tuple) -> int:
		'''Returns the weight value of the node'''
		return node[0]
	
	def get_index_of_occurences(match_val:'any', arr:list) -> list:
		'''Return the position of match_val in arr if arr contains match_val, else return False'''
		if match_val in arr:
			return arr.index(match_val)
		return False
	
	visited = []
	#to_visit is an array where the contents are [(x, y)]
	#to_visit_weight_path is the node's other half: [weight, [path]]
	
	initial = source
	#To visit represents the "priority queue" for Dijkstra's
	to_visit = [initial]
	to_visit_weight_path = [[0, []]]
	while to_visit:
		#Sort to force into backwards stack orientation based on weights, lowest last
		to_visit_weight_path, to_visit = (list(item) for item in zip(*sorted(zip(to_visit_weight_path, to_visit), key=get_weight, reverse=True)))
		#to_visit.sort(key=get_weight, reverse=True)
		#Take the lowest weight node from the stack
		current = to_visit.pop()
		current_weight = to_visit_weight_path.pop()
		#Add current node to list of visited nodes
		visited.append(current)
		#Gets the coordinates of all neighbours
		neighbours = tiles.get_neighbours(current)
		for neighbour in neighbours:
			weight = tiles.get_weight(neighbour)
			#If the current neighbour is the destination, return how we got there and how long it took
			if neighbour == dest:
				return current_weight[0]+ weight, current_weight[1] + [current, dest]
			#Check if current neighbour is already in the stack
			matches = get_index_of_occurences(neighbour, to_visit)#find_sub_array([neighbour[0], neighbour[1], None, None], to_visit)
			#Check if current neighbour has already been visited
			has_visited = neighbour in visited #find_sub_array([neighbour[0], neighbour[1], None, None], visited)
			#If neighbour already in the stack
			if matches:
				#If the weight in the stack is higher than the weight from current to the neighbour
				if to_visit_weight_path[matches][0] > weight + current_weight[0]:
					#Then replace the weight with the new weight
					to_visit_weight_path[matches][0] = weight + current_weight[0]
					#And set its path to current's path including current itself
					to_visit_weight_path[matches][1] += current_weight[1] + [current]
			#If the neighbour is not in the stack
			else:
				#And the neighbour hasn't already been visited
				if not has_visited:
					#Add neighbour and weight to stack
					to_visit.append(neighbour)
					to_visit_weight_path.append([weight+current_weight[0], current_weight[1] + [current]])
	#If all tiles have been searched and no path is found
	return "no path found"

def find_path(source:tuple, dest:tuple, tiles:TileMap):
	path = dijkstra(source, dest, tiles)
	return path

#Width, Height
map_size = (25, 25)

#Create the main TileMap
tiles = TileMap(map_size[0],map_size[1], default_val=1)

#Create the random spattering of mountains
mountains = TileMap(map_size[0],map_size[1])
mountains.gen_modifier_layer(9998, 200)

#Create the random spattering of forests
forests = TileMap(map_size[0],map_size[1])
forests.gen_modifier_layer(1, 300)

#Overlay mountains and forests on top off the main TileMap
tiles.add_modifier_layer(mountains)
tiles.add_modifier_layer(forests)

#Randomly pick a start point
start = (randint(0,map_size[0]-1), randint(0,map_size[1]-1))
end = start

#Ensure that start != end
while end == start:
	end = (randint(0,map_size[0]-1), randint(0,map_size[1]-1))

#Enable / Disable rain here
rain_enabled = True

#Don't do extra work if there's no rain
if not rain_enabled:
	path = find_path(start, end, tiles)
	#Print the grid
	tiles.print_table(path[1])
	print(f'Starting at {start} and moving to {end} will take {path[0]} turns')

else:
	#Add a blank layer that is removed just to simplify the loop
	tiles.add_modifier_layer(TileMap(map_size[0],map_size[1]))
	final_path = []
	while not start == end:
		#Add current position to the final_path
		final_path.append(start)
		#Reset the rain grid to empty
		rain = TileMap(map_size[0],map_size[1])
		#Generate x many new random rain tiles
		rain.gen_modifier_layer(2, 80)
		#Remove the current rain layer or the placeholder blank layer
		tiles.remove_modifier_layer(-1)
		#Add rain layer
		tiles.add_modifier_layer(rain)
		#Run Dijkstra's over the updated grid
		path = find_path(start, end, tiles)
		#Move one tile along the path
		start = path[1][1]
	tiles.print_table(final_path)
	print(final_path)