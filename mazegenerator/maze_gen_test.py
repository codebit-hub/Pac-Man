from mazegenerator import MazeGenerator

maze_gen = MazeGenerator(
    size=(14, 14), 
    perfect=False, 
    entry_cell=(1, 1), 
    exit_cell=(13, 13), 
    seed=42
    )


maze_grid = maze_gen.maze
shortest_path = maze_gen.shortest_path
maze_entry = maze_gen.maze_entry
maze_exit = maze_gen.maze_exit

print(f"Maze Grid:\n{maze_grid}")
print(f"Shortest Path: {shortest_path}")
print(f"Maze Entry: {maze_entry}")
print(f"Maze Exit: {maze_exit}")
