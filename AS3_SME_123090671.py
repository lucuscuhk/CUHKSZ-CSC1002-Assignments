import random
import time
from functools import partial
import turtle

# Direction and movement related variables
direction_map = {
    "Right": {"index": 0, "move": (20, 0)},
    "Up": {"index": 1, "move": (0, 20)},
    "Left": {"index": 2, "move": (-20, 0)},
    "Down": {"index": 3, "move": (0, -20)},
    "Pause": {"index": 4, "move": (0, 0)}
}

key_up = "Up"
key_down = "Down"
key_left = "Left"
key_right = "Right"
key_space = "space"

heading_by_key = {
    key_up: 90,
    key_down: 270,
    key_left: 180,
    key_right: 0
}

previous_direction = None
current_key = None
current_movement = None
can_switch_move = True
can_change_direction = True
moving_bias = [0, 0]

# Game state related variables
start_time = time.time()
game_state = None
contact_with_monster = False
strike_with_monster = False
display_game_over = False
monster_contacts_count = 0
winner_count = 0
game_elapsed_time = 0
current_speed = 0
nomal_game_speed = 200
slow_game_speed = 350
snake_movement_speed = 200

# Screen and display related variables
game_screen = None
intro_message_part1 = None
intro_message_part2 = None
status_display = None
game_font = ("Arial", 16, "normal")
snake_body_color = ("blue", "black")
snake_head_color = "red"
monster_color = "purple"

# Snake related variables
snake_entity = None
snake_length = 1
snake_size = 5
key_index_list = [0.5, 0.5]
snake_head_position = []
non_repeating_positions = [0.5, 0.5]
snake_body_position = []

# Food related variables
food_position_list = []
food_visibility_states = [False] * 5
food_consumed_list = [False] * 5

# Monster related variables
monster_entities = []


def configure_play_area():
    """
    Creates and configures the play area for the game, including drawing boundaries and displaying introductory text.

    Returns:
        tuple: A tuple containing turtle objects for intro text and status display.
    """
    m = create_turtle(0, 0, "", "black")
    m.shapesize(25, 25, 5)
    m.goto(0, -40)
    s = create_turtle(0, 0, "", "black")
    s.shapesize(4, 25, 5)
    s.goto(0, 250)
    intro_1 = create_turtle(-200, 150)
    intro_1.hideturtle()
    intro_1.write("Snake By 123090671", font=game_font)
    intro_2 = create_turtle(-200, 125)
    intro_2.hideturtle()
    intro_2.write("Click anywhere to start, have fun!!!", font=game_font)
    status = create_turtle(0, 0, "", "black")
    status.hideturtle()
    status.goto(-200, s.ycor())
    return intro_1, intro_2, status


def create_and_setup_turtle(position, count):
    """
    Creates a turtle at a specified position and sets it up with a label.

    Parameters:
        position (tuple): The (x, y) position for the turtle.
        count (int): The label for the turtle, indicating its order.

    Returns:
        Turtle: A configured turtle object at the specified position.
    """
    xcor = 20 * position[0]
    ycor = -50 + 20 * position[1]
    turtle = create_turtle(xcor, ycor)
    turtle.hideturtle()
    turtle.write(count, font=game_font)
    return turtle


def config_screen():
    """
    Configures and initializes the game screen.

    Returns:
        Screen: The configured turtle screen for the game.
    """
    s = turtle.Screen()
    s.tracer(0)
    s.title("Snake by 123090671")
    s.setup(500 + 120, 500 + 120 + 80)
    s.mode("standard")
    return s


def create_turtle(x, y, color="red", border="black"):
    """
    Creates a turtle entity with specified position and color.

    Parameters:
        x (int): The x-coordinate of the turtle.
        y (int): The y-coordinate of the turtle.
        color (str): The fill color of the turtle.
        border (str): The border color of the turtle.

    Returns:
        Turtle: A turtle object with specified attributes.
    """
    t = turtle.Turtle("square")
    t.color(border, color)
    t.up()
    t.goto(x, y)
    return t


def update_status():
    """
    Updates the game status, including the number of contacts, elapsed time, and current motion state, on the screen.
    """
    global monster_contacts_count, current_movement, game_elapsed_time, start_time, status_display
    current_time = time.time()
    game_elapsed_time = int(current_time - start_time)
    status_display.clear()
    status_display.goto(-200, status_display.ycor())
    status_display.write(f"Contact:{monster_contacts_count}", font=('arial', 15, 'bold'))
    status_display.goto(-50, status_display.ycor())
    status_display.write(f"Time:{game_elapsed_time}", font=('arial', 15, 'bold'))
    status_display.goto(100, status_display.ycor())
    status_display.write(f"Motion:{current_movement}", font=('arial', 15, 'bold'))
    game_screen.update()


def generate_monster_positions(center, radius, count):
    """
    Generates random positions for monsters within a specified radius from a center point.

    Parameters:
        center (tuple): The center point (x, y) around which monsters are positioned.
        radius (int): The radius within which monsters should be generated.
        count (int): The number of monster positions to generate.

    Returns:
        list: A list of tuples representing the (x, y) positions of monsters.
    """
    positions = set()
    while len(positions) < count:
        x = random.randint(center[0] - radius, center[0] + radius)
        y = random.randint(center[1] - radius, center[1] + radius)
        distance = ((x - snake_entity.xcor()) ** 2 + (y - snake_entity.ycor()) ** 2) ** 0.5
        if distance > 50:
            # Check if the new position overlaps with any existing monster
            if not any(abs(x - mx) < 20 and abs(y - my) < 20 for mx, my in positions):
                positions.add((x, y))
    return list(positions)


def create_food_list():
    """
    Generates a list of random positions for food items within the game area.

    Returns:
        list: A list of tuples representing the (x, y) positions for food items.
    """
    positions = {(random.randint(-12, 12), random.randint(-12, 12)) for _ in range(5)}
    return list(positions)


def display_food():
    """
    Creates and displays food items on the canvas at positions generated by `create_food_list`.
    """
    global food_list, turtle_list
    food_list = create_food_list()
    turtle_list = [create_and_setup_turtle(pos, count + 1) for count, pos in enumerate(food_list)]


def set_motion_and_direction(key):
    """
    Sets the motion and direction of the snake based on the pressed key.

    Parameters:
        key (str): The key pressed by the user.
    """
    global current_movement, current_key, snake_entity
    current_movement = key
    current_key = key
    snake_entity.setheading(heading_by_key[key])


def set_snake_heading(key):
    """
    Sets the direction of the snake or pauses its motion based on the pressed key.

    Parameters:
        key (str): The key pressed by the user.
    """
    global can_switch_move, current_movement, last_direction
    if key == key_space:
        if can_switch_move:
            current_movement = "Pause"
            can_switch_move = False
        else:
            can_switch_move = True
            if last_direction:
                set_motion_and_direction(last_direction)
            else:
                current_movement = "Pause"
    else:
        if key in heading_by_key:
            if can_switch_move:
                last_direction = key
            set_motion_and_direction(key)


def on_arrow_key_pressed(key):
    """
    Responds to arrow key presses, setting the direction of the snake and updating the game status.

    Parameters:
        key (str): The arrow key pressed by the user.
    """
    global current_key, last_direction
    current_key = key
    set_snake_heading(key)
    update_status()


def move_state():
    """
    Updates the motion state of the snake based on the switch_move variable and the pressed key.
    """
    global can_switch_move, current_movement, current_key
    if not can_switch_move:
        current_movement = "Pause"
    else:
        current_movement = current_key


def list_append():
    """
    Appends the index of the pressed key to the list_key global variable.
    """
    global key_index_list, current_key
    if current_key in direction_map:
        key_index_list.append(direction_map[current_key]["index"])


def list_non_append():
    """
    Appends the index of the pressed key to the list_non_repeat global variable if it's not a repeat of the last key.
    """
    global non_repeating_positions, current_key
    if current_key in direction_map and non_repeating_positions[-1] != direction_map[current_key]["index"]:
        non_repeating_positions.append(direction_map[current_key]["index"])


def get_moving_tendency():
    """
    Updates the global tendency variable with the next potential position of the snake.
    """
    global current_key, snake_entity, moving_bias
    if current_key in direction_map:
        dx, dy = direction_map[current_key]["move"]
        moving_bias = [snake_entity.xcor() + dx, snake_entity.ycor() + dy]


def back_substitute_moving_state():
    """
    Substitutes the moving state back to the last direction if the current motion is paused or invalid.
    """
    global can_switch_move, key_index_list, current_key, can_change_direction
    if can_switch_move and not can_change_direction:
        index = int(key_index_list[-1])
        reverse_map = {v["index"]: k for k, v in direction_map.items()}
        current_key = reverse_map.get(index, current_key)


def data():
    """
    Updates the current position of the snake to grid coordinates for collision detection and food consumption.
    """
    global x_cur, y_cur, x, y, snake_entity
    x_cur, y_cur = round(snake_entity.xcor()), round(snake_entity.ycor())
    x, y = round(x_cur / 20), round((y_cur + 40) / 20)


def preparation():
    """
    Prepares the game environment for the next frame by updating movement states and position data.
    """
    list_append()
    list_non_append()
    back_substitute_moving_state()
    get_moving_tendency()
    move_state()
    data()


def judge_strike():
    """
    Checks for collisions between the snake's head and any part of its body, indicating a self-collision.
    """
    global moving_bias, snake_body_position, strike_with_monster
    moving_bias[0], moving_bias[1] = round(moving_bias[0]), round(moving_bias[1])
    body_set = set(snake_body_position)
    strike_with_monster = (moving_bias[0], moving_bias[1]) in body_set


def create_body_list():
    """
    Maintains a list of coordinates representing the snake's body segments.

    Returns:
        list: A list of tuples each representing the (x, y) coordinates of a body segment.
    """
    global snake_head_position, snake_length
    while len(snake_head_position) > snake_length:
        snake_head_position.remove(snake_head_position[0])
    return snake_head_position


def get_body():
    """
    Updates the list of coordinates representing the snake's body for collision detection.
    """
    global snake_head_position, x_cur, y_cur, snake_body_position
    if (x_cur, y_cur) not in snake_head_position:
        snake_head_position.append((x_cur, y_cur))
    snake_body_position = create_body_list()


def handle_pause_key():
    """
    Manages the snake's motion when the space key is pressed to pause the game.
    """
    global can_switch_move, non_repeating_positions, current_key
    if current_key == "space" and can_switch_move:
        direction_info = direction_map.get(non_repeating_positions[-1])
        if direction_info:
            current_key = direction_info["move"]


def handle_non_pause_key():
    """
    Manages the game's state when a non-space key is pressed to resume the game from pause.
    """
    global can_switch_move, current_key
    if current_key != "space" and not can_switch_move:
        can_switch_move = not can_switch_move


def pause_case():
    """
    Toggles the pause state of the game, allowing the game to be paused and resumed.
    """
    handle_pause_key()
    handle_non_pause_key()


def on_timer_snake():
    """
    Acts as the main game loop timer function that updates game state including snake movement, eating, and checking win or game over conditions.
    """
    if game_state:
        return
    preparation()
    if catch():
        game_over()
        return
    get_body()
    judge_strike()
    pause_case()
    operate_snake()
    if len(snake_body_position) == 21:
        winner()
    food()
    game_screen.update()
    game_screen.ontimer(on_timer_snake, snake_movement_speed)


def operate_snake():
    """
    Manages snake operations including movement, body growth, and adjusting speed based on the snake's size.
    """
    global snake_entity, snake_length, snake_size, snake_body_color, snake_head_color, can_switch_move, current_movement, snake_movement_speed
    if not can_switch_move or current_key not in direction_map:
        return
    next_x = snake_entity.xcor() + direction_map[current_key]['move'][0]
    next_y = snake_entity.ycor() + direction_map[current_key]['move'][1]
    if not (-240 <= next_x <= 240 and -280 <= next_y <= 200):
        current_movement = "Pause"
        return
    # Update snake color and position
    snake_entity.color(*snake_body_color)
    snake_entity.stamp()
    snake_entity.color(snake_head_color)
    snake_entity.goto(next_x, next_y)
    data()  # Update position information

    # Adjust speed based on snake size
    adjust_snake_speed()

    if snake_length <= snake_size:
        snake_length += 1
    if len(snake_entity.stampItems) > snake_size:
        snake_entity.clearstamps(1)


def adjust_snake_speed():
    """
    Adjusts the snake's speed based on its current size.
    """
    global snake_movement_speed, snake_length, snake_size
    if snake_length < snake_size:
        snake_movement_speed = slow_game_speed
    else:
        snake_movement_speed = nomal_game_speed


def get_snake_head_position():
    """
    Retrieves the current position of the snake's head in grid coordinates.

    Returns:
        tuple: A tuple representing the (x, y) grid coordinates of the snake's head.
    """
    x_cur = int(snake_entity.xcor() // 20)
    y_cur = int((snake_entity.ycor() + 40) // 20)  # Adjust for grid's y-offset
    return x_cur, y_cur


def check_food_consumption(i, food_position, x_cur, y_cur):
    """
    Checks if the snake has consumed a food item based on its current position.

    Parameters:
        i (int): The index of the food item in the global food list.
        food_position (tuple): The (x, y) grid coordinates of the food item.
        x_cur (int): The x-coordinate of the snake's head in grid coordinates.
        y_cur (int): The y-coordinate of the snake's head in grid coordinates.
    """
    global food_consumed_list, turtle_list, snake_size, food_position_list, winner_count
    fx, fy = food_position
    if x_cur == fx and y_cur == fy and not food_consumed_list[i] and not food_visibility_states[i]:
        food_consumed_list[i] = True
        turtle_list[i].clear()
        snake_size += (i + 1)  # Increment snake size based on food index
        if food_position not in food_position_list:
            winner_count += 1
        food_position_list.append(food_position)


def food():
    """
    Manages the process of checking and handling food consumption by the snake.
    """
    global x, y, food_list, num, food_visibility_states
    x_cur, y_cur = get_snake_head_position()
    for i, food_position in enumerate(food_list):
        check_food_consumption(i, food_position, x_cur, y_cur)
        if all(food_consumed_list):
            winner()


def clear_food(index):
    """
    Clears the visual representation of a food item from the game screen.

    Parameters:
        index (int): The index of the food item in the global food list.
    """
    global turtle_list
    turtle_list[index].clear()


def move_food(index):
    """
    Moves a food item to a new random position within the game boundaries.

    Parameters:
        index (int): The index of the food item in the global food list.
    """
    global turtle_list, food_list
    # Define possible movements
    movements = [(0, 40), (0, -40), (40, 0), (-40, 0)]
    food_turtle = turtle_list[index]
    move = random.choice(movements)
    new_x = food_turtle.xcor() + move[0]
    new_y = food_turtle.ycor() + move[1]
    # Check if new position is within bounds
    if -240 <= new_x <= 240 and -280 <= new_y <= 200:
        food_turtle.goto(new_x, new_y)
        food_list[index] = (round(new_x / 20), round((new_y + 40) / 20))
    food_turtle.clear()
    food_turtle.write(index + 1, font=game_font)


def on_timer_conceal():
    """
    Handles the timing for the concealment and revealing of food items on the game screen.
    """
    global food_visibility_states, game_screen
    num = generate_random_food_index()
    food_visibility_states[num] = True
    rewrite_food_display(num)
    food_visibility_states[num] = False
    rewrite_food_display(num)
    time_conceal = random.randint(5000, 10000)  # Random concealment time
    game_screen.ontimer(on_timer_conceal, time_conceal)


def rewrite_food_display(index):
    """
    Updates the display of a food item based on its current state (concealed or revealed).

    Parameters:
        index (int): The index of the food item in the global food list.
    """
    global food_consumed_list, food_visibility_states
    if not food_consumed_list[index]:
        if food_visibility_states[index]:
            clear_food(index)
        else:
            move_food(index)


def on_timer_monster():
    """
    Handles the movement of monsters towards the snake and schedules the next movement event.

    This function calculates the direction for each monster to move towards the snake,
    ensuring monsters try to follow the snake while avoiding overlapping with each other.
    It also sets a timer for the next movement, creating a continuous chase effect.
    """
    global game_state, monster_entities, game_screen, snake_entity
    if game_state:
        return  # Stop moving monsters if the game state indicates a pause or end

    for monster in monster_entities:
        primary, secondary = calculate_monster_direction(monster)
        monster_moving(monster, primary, secondary)

    game_screen.update()
    # Randomize monster movement speed for added unpredictability
    monster_speed = random.randint(350, 700)
    game_screen.ontimer(on_timer_monster, monster_speed)


def calculate_monster_direction(monster):
    """
    Determines the optimal direction for a monster to move towards the snake.

    Parameters:
        monster (Turtle): The monster whose direction is being calculated.

    Returns:
        tuple: The primary and secondary directions (as (dx, dy) tuples) for the monster to move.
    """
    x_diff = snake_entity.xcor() - monster.xcor()
    y_diff = snake_entity.ycor() - monster.ycor()
    if abs(x_diff) > abs(y_diff):
        primary = (20 if x_diff > 0 else -20, 0)
        secondary = (0, 20 if y_diff > 0 else -20)
    else:
        primary = (0, 20 if y_diff > 0 else -20)
        secondary = (20 if x_diff > 0 else -20, 0)
    return primary, secondary


def monster_moving(monster, primary, secondary):
    """
    Moves the monster in one of the calculated directions, preferring the primary direction.

    The function tries to move the monster directly towards the snake but will choose an alternative
    route if the direct path is blocked by another monster or the game boundary.

    Parameters:
        monster (Turtle): The monster to be moved.
        primary (tuple): The preferred (dx, dy) direction to move.
        secondary (tuple): The secondary (dx, dy) direction to move if the primary is blocked.
    """
    directions = [primary, secondary, (-primary[0], -primary[1]), (-secondary[0], -secondary[1])]
    new_positions = [(monster.xcor() + dx, monster.ycor() + dy) for dx, dy in directions]

    for (new_x, new_y) in new_positions:
        # Check if the new position is within game boundaries and not overlapping with other monsters
        if not detect_overlap_for_monster(monster, new_x, new_y) and -240 <= new_x <= 240 and -280 <= new_y <= 200:
            monster.goto(new_x, new_y)
            break


def detect_overlap_for_monster(monster, new_x, new_y):
    """
    Checks if moving a monster to a new position would cause it to overlap with another monster.

    Parameters:
        monster (Turtle): The monster being moved.
        new_x (float): The new x-coordinate for the monster.
        new_y (float): The new y-coordinate for the monster.

    Returns:
        bool: True if the new position overlaps with another monster, False otherwise.
    """
    for other_monster in monster_entities:
        if other_monster is monster:
            continue  # Skip the monster itself
        if abs(other_monster.xcor() - new_x) < 20 and abs(other_monster.ycor() - new_y) < 20:
            return True
    return False


def generate_random_food_index():
    """
    Generates a random index for a food item that has not yet been eaten.

    Returns:
        int: A randomly selected index for an uneaten food item.
    """
    while True:
        num = random.randint(0, 4)
        if not food_consumed_list[num]:
            return num


def catch():
    """
    Checks if the snake has been caught by any monster, indicating a collision.

    Returns:
        bool: True if the snake is caught by a monster, False otherwise.
    """
    global monster_contacts_count, monster_entities, snake_entity, display_game_over
    for monster in monster_entities:
        x_diff = abs(monster.xcor() - snake_entity.xcor())
        y_diff = abs(monster.ycor() - snake_entity.ycor())
        if x_diff <= 20 and y_diff <= 20:
            monster_contacts_count += 1
            display_game_over = True
            update_status()
            return True
    return False


def check_contact():
    """
    Checks for contact between any monster and the snake, updating the contact count.
    This function assumes 'body_list' contains the current positions of the snake's body parts.
    """
    global monster_contacts_count, monster_entities, contact_with_monster, game_screen, game_state, display_game_over
    if game_state or display_game_over:
        return

    contact_with_monster = False
    for monster in monster_entities:
        monster_position = (round(monster.xcor()), round(monster.ycor()))
        # The comprehension iterates over 'body_list' to find any contact
        if any(abs(monster_position[0] - part[0]) < 20 and abs(monster_position[1] - part[1]) < 20 for part in
               snake_body_position):
            contact_with_monster = True
            break

    if contact_with_monster:
        monster_contacts_count += 1
    update_status()
    game_screen.ontimer(check_contact, 500)


def game_over():
    """
    Triggers the game over state and displays a game over message.
    """
    global game_screen, game_state
    gameover_turtle = turtle.Turtle()
    gameover_turtle.hideturtle()
    gameover_turtle.penup()
    gameover_turtle.goto(0, 0)
    gameover_turtle.color('red')
    gameover_turtle.write("Game Over!", align="center", font=("Arial", 40, "bold"))
    game_state = True


def winner():
    """
    Handles the win condition of the game, displaying a victory message on the screen.
    """
    global game_screen, game_state
    win_turtle = turtle.Turtle()
    win_turtle.hideturtle()
    win_turtle.penup()
    win_turtle.goto(0, 0)
    win_turtle.color('red')
    win_turtle.write("Winner!", align="center", font=("Arial", 40, "bold"))
    game_state = True


def clear_screen_clicks():
    """
    Clears any existing on-screen click events.
    """
    global game_screen
    game_screen.onscreenclick(None)


def clear_intro_texts():
    """
    Clears the introductory texts from the screen.
    """
    global intro_message_part1, intro_message_part2
    intro_message_part1.clear()
    intro_message_part2.clear()


def set_key_bindings():
    """
    Sets up the keyboard bindings for controlling the game.
    """
    global game_screen
    game_screen.onkey(partial(on_arrow_key_pressed, key_up), key_up)
    game_screen.onkey(partial(on_arrow_key_pressed, key_down), key_down)
    game_screen.onkey(partial(on_arrow_key_pressed, key_left), key_left)
    game_screen.onkey(partial(on_arrow_key_pressed, key_right), key_right)
    game_screen.onkey(partial(on_arrow_key_pressed, key_space), key_space)


def start_timers():
    """
    Starts the game timers for handling snake and monster movements and managing food concealment.
    """
    global start_time, game_screen
    start_time = time.time()
    display_food()
    game_screen.ontimer(on_timer_snake, 100)
    game_screen.ontimer(on_timer_monster, 100)
    game_screen.ontimer(on_timer_conceal, 5000)


def start_game(x, y):
    """
    Initializes and starts the game upon a screen click, preparing the game environment.

    Parameters:
        x (int): The x-coordinate of the click position. Not used in this function.
        y (int): The y-coordinate of the click position. Not used in this function.
    """
    clear_screen_clicks()
    clear_intro_texts()
    set_key_bindings()
    start_timers()


if __name__ == "__main__":
    game_screen = config_screen()
    intro_message_part1, intro_message_part2, status_display = configure_play_area()
    update_status()
    snake_initial_position = (0, 0)
    snake_entity = create_turtle(snake_initial_position[0], snake_initial_position[1], "red", "black")
    radius = 180
    monster_positions = generate_monster_positions((0, 0), radius, 4)
    monster_entities = [create_turtle(x, y, "purple", "black") for x, y in monster_positions]
    game_screen.onscreenclick(start_game)
    check_contact()
    game_screen.update()
    game_screen.listen()
    turtle.mainloop()
