###################################################################################
###################################################################################

# Assignment 4 
# Juan Alejandro Otalora Castro
# UCID: 30107074

# Purpose: Write a version of the Beat Saber-inspired game introduces a significant enhancement:
# synchronizing beats with music through file reading, transitioning from a random beat generator to a...
# rhythm-fueled experience with the rhythm of your chosen song.

# Use different names for player_name due to key properties 

###################################################################################
###################################################################################


from SimpleGame.simplegame import *
import random
from math import *
import sys
import os
import re


###################################################################################
###################################################################################


BEAT_DIRECTIONS_R = ['up', 'down', 'left', 'right']
VISIBLE = 'visible'
SPEED = 5   # DO NOT CHANGE
streams= {1:range(0,376), 2:range(376,751)}
current_beat_index = 0

generation_speed = 0.6
frame_counter = 0
score = 0
SongNames = ['believer', 'shut up and dance', 'cake by the ocean', 'thunder']
Difficulties = ['Easy', 'Normal', 'Hard', 'Expert']
selected_background = None
my_backgrounds = ['background_cat', 'background_dog', 'background_hp_rav', 'background_goku']


game_ended = False
game_started = False
startScreenElements = {}
playScreenElements = {}
endScreenElements = {}

beatList = []


###################################################################################
###################################################################################

cwd = os.getcwd() 

file_path_10 = os.path.join(cwd, 'top10.csv')

def read_scores(file_path):
    scores = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip(): 
                    player, score_str = line.strip().split(',')
                    scores[player] = int(score_str)
    except FileNotFoundError:
        pass

    return scores

def write_scores(file_path, scores):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        for player, score in scores.items():
            file.write(f'{player},{score}\n')

def update_scores(file_path, new_player, new_score):

    # I don't remember if we used sort in class but I got the fragment of functionality from stackoverflow:
    # https://stackoverflow.com/questions/19199984/sort-a-list-in-python

    # Read the existing scores
    scores = read_scores(file_path)

    # Update the score for the new player, add if not present
    scores[new_player] = max(scores.get(new_player, 0), new_score)

    # Sort scores in descending order by value
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


    # Keep only the top 10 scores
    top_scores = dict(list(sorted_scores.items())[:10])

    # Write the updated, sorted scores back to the file
    write_scores(file_path, top_scores)

###################################################################################
###################################################################################


player_name = "Default Name"
songName = "Default Song"
difficulty = "Default Difficulty"

if len(sys.argv) == 4:
    player_name = str(sys.argv[1])
    songName = str(sys.argv[2])
    difficulty = str(sys.argv[3])

    if not player_name or not player_name.strip():
        print("Error: Player name must be a non-empty string.")
        sys.exit(1)

    if songName not in SongNames:
        print(f"Error: Song name must be one of {SongNames}.")
        sys.exit(1)

    if difficulty not in Difficulties:
        print(f"Error: Difficulty must be one of {Difficulties}.")
        sys.exit(1)

else:
    print("Usage: python FileName.py <player_name> <song_name> <difficulty>")
    sys.exit(1)


###################################################################################
###################################################################################

# For my code I had to do some research regarding how to get my code to find the right path for the files...
# I am not sure if this is due to me using VScode and not having the right configurations, but my relative path wasn't working...
# I ended up finding information in stack overflow about using the regular expressions module...
# This is the reason why my code includes it to find the path for my files required to use the program and meet the requirements...
    
beats_path = os.path.join(cwd, songName, f'{difficulty}.beat')

cwd = os.getcwd()
beats_path = os.path.join(cwd, songName, f'{difficulty}.beat')

if os.path.exists(beats_path):
    with open(beats_path, 'r') as file:
        
        header = re.split(r'\s+', file.readline().strip())
        c_index_Frame = header.index('Frame')
        c_index_Hand = header.index('Hand')
        c_index_Direction = header.index('Direction')
 
        extracted_data = []
        for line in file:
            
            parts = re.split(r'\s+', line.strip())
            Frame = parts[c_index_Frame]
            Hand = parts[c_index_Hand]
            Direction = parts[c_index_Direction]
            extracted_data.append((Frame, Hand, Direction))


###################################################################################
###################################################################################


def start_screen_setup():
    startScreenElements['ready'] = create_element('text-ready', (WIDTH / 2, 350))
    startScreenElements['space'] = create_element('space-bar', (WIDTH / 2, 600))
    startScreenElements['tap'] = create_element('tap-active', (WIDTH / 2 + 70, 600))
    startScreenElements['tap'][VISIBLE] = True
    schedule_callback_every(toggle_tap, .5)

def end_screen_setup():
    global game_ended

    game_ended = True
    endScreenElements['GameOver'] = create_element('text-gameover', (WIDTH / 2, HEIGHT / 2))
    endScreenElements['GameOver'][VISIBLE] = True
    schedule_callback_after(hide_gameover, 1)
     
def game_screen_setup():
    global game_started
    game_started = True
    cancel_callback_schedule(toggle_tap)
    playScreenElements['score'] = create_element('star2', (30, 30))
    playScreenElements['keyboard'] = create_element('keyboard_arrows', (WIDTH / 2, HEIGHT - 60))
    playScreenElements['keyboard']['base'] = 'keyboard_arrows_'
    playScreenElements['go'] = create_element('text-go', (WIDTH / 2, HEIGHT / 2 + 0))
    playScreenElements['go'][VISIBLE] = True
    schedule_callback_after(hide_go, .5)
        
def hide_go():
    playScreenElements['go'][VISIBLE] = False

def hide_gameover():
    endScreenElements['GameOver'][VISIBLE] = False

def toggle_tap():
    startScreenElements['tap'][VISIBLE] = not startScreenElements['tap'][VISIBLE]

def draw():
    """
    - Called automatically everytime there's a change in the screen
    - Do not include any operations other than drawing inside this function.
    - The only allowed statements/functions are the ones that have draw_ in the name like
    draw_background_image(), draw_element(), etc
    """
    global flag, songName, difficulty, player_name, my_backgrounds, selected_background
    # You may set different background for each step!
    if selected_background is None:
        selected_background = 'background_goku'

    draw_background(selected_background)

    if not game_started:
        # What you want to show *before* the game starts goes here. eg 'Press Space to Start!'
        
        draw_text_on_screen(f'Player Name: {player_name}', (WIDTH / 2, 50), fontsize=40)
        draw_text_on_screen(f'{songName}', (WIDTH / 2, 100), fontsize=40)
        draw_text_on_screen(f'Difficulty: {difficulty}', (WIDTH / 2, 150), fontsize=40)

        for gameElement in startScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)
    elif game_ended:
        # What you want to show *after* the game ends goes here. eg 'You Scored x Beats!'
        for gameElement in endScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)
            else: 
                draw_text_on_screen(f'Score: {score}', (WIDTH / 2, 100), lineheight=1.2, ocolor='lightseagreen', owidth=1.5, color="white", fontsize=90)
                draw_text_on_screen('Top 10 Scores', (WIDTH / 2, 220), lineheight=1.2, ocolor='lightseagreen', owidth=1.5, color="white", fontsize=80)
                scores_dict = read_scores(file_path_10)
                top_10_scores = sorted(scores_dict.items(), key=lambda item: item[1], reverse=True)[:10]
                startYtop10 = 280
                for item in top_10_scores:
                 draw_text_on_screen(f'{item[0]}: {item[1]}', (WIDTH / 2, startYtop10), ocolor='lightseagreen', owidth=1.5, color="white", fontsize=30)
                 startYtop10 += 40
                
    else:
        # What you want to show *during* the game goes here. e.g. beats, timer, etc
        draw_text_on_screen(f'{score}', (70, 32), color='yellow', fontsize=40)
        
        for gameElement in playScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)

        for beat in beatList:
            draw_element(beat)

def update(): # Check for negative value or music ends. Manage_background_music now has a T or F for song end so use that.
    """
    - Called automatically 60 times per second (every 1/60th of a second) to
    maintain a smooth frame rate of 60 fps.
    - Ideal for game logic e.g. moving objects, updating score, and checking game conditions.
    """
    # The frame counter keeps track of which frame we're on, this can be helpful for
    # operations that are time sensitive. You may also use the callback functions instead of
    # using the frame_counter.

    global frame_counter, game_ended, score, current_beat_index
    frame_counter += 1

    if current_beat_index < len(extracted_data):
        frame, hand, direction = extracted_data[current_beat_index]
        
        if frame_counter >= int(frame):
            stream_number = 1 if hand.strip().lower() == 'left' else 2
            generate_beat(stream_number, direction.strip().lower())
            current_beat_index += 1

    if not game_started:
        # Game logic if any *before* the game starts.
        pass

    elif game_ended:
        # Game logic if any *after* the game ends.
        pass
    else:
        # Game logic if any *during* the game.
        # move it 5 pixels down
        for beat in beatList:
            if beat['moving']:
                move_by_offset(beat, (0, SPEED))
                if get_position(beat, 'bottom') >= HEIGHT:
                    beat['moving'] = False
                    beat['scoreStatus'] = 'miss'
                    score -= 1
            elif beat['scoreStatus']:
                if beat['scoreStatus'] == 'hit':
                    score = score
                score_beat(beat)
 
def on_key_down(key):
    """
    Called when a key is pressed on the keyboard.
    - Do not use this function for game logic.

    Parameters:
    - key: An integer representative of the key that was pressed.
    In order to get a str value of the key pressed, use get_key() instead.
    """

    key_pressed = get_key_pressed(key)
    if key_pressed == 'space' and not game_started:
        start_game()
        return

    # Handle left side controls (awsd)
    if key_pressed in 'awsd':
        handle_side(key_pressed, 1)

    # Handle right side controls (arrow keys)
    elif key_pressed in ['left', 'up', 'down', 'right']:
        handle_side(key_pressed, 2)

def find_lowest_moving_beat_in_stream(stream_number):
    for beat in beatList:
        beat_center_x = get_position(beat, 'center')[0]
        if beat['moving'] and beat_center_x in streams[stream_number]:
            return beat
    return None

def keyboardArrowChangeBack():
    change_image(playScreenElements['keyboard'], playScreenElements['keyboard']['base'][:-1])

def handle_side(key_pressed, stream_number):

    global score

    beat = find_lowest_moving_beat_in_stream(stream_number)
    if beat:
        direction_map = {'a': 'left', 'w': 'up', 's': 'down', 'd': 'right'}
        pressed_direction = direction_map.get(key_pressed, key_pressed.replace('Arrow', '').lower())

        beat_top = get_position(beat, 'top')
        beat_bottom = get_position(beat, 'bottom')

        hit_window_top = 550
        hit_window_bottom = 650

        beat['moving'] = False
        change_image(playScreenElements['keyboard'], playScreenElements['keyboard']['base'] + pressed_direction)
        schedule_callback_after(keyboardArrowChangeBack, .1)

        if hit_window_top <= beat_bottom and beat_top <= hit_window_bottom:
            if beat['direction'] == pressed_direction:
                beat['scoreStatus'] = 'hit'
                beat['moving'] = False
                score += 2  
            else:
                beat['scoreStatus'] = 'miss'
                score -= 1  
        else:
            beat['scoreStatus'] = 'miss'
            beat['moving'] = False
            score -= 1  
        if get_position(beat, 'bottom') >= HEIGHT:
                    beat['moving'] = False
                    beat['scoreStatus'] = 'miss'
                    score -= 1  
def score_beat(beat): 
    status = beat['scoreStatus']
    beat['scoreStatus'] = ''
    direction = beat['direction']
    change_image(beat, direction + '-' + status)
    schedule_callback_after(remove_lowest_beat, .1)

def remove_lowest_beat():  
    if beatList:
        beatList.pop(0)

def find_lowest_moving_beat():
    for beat in beatList:
        if beat['moving']:
            return beat
    return None

def every_second():

    global songName, score

    if (score <= -1):
     end_game()
     return
    
    if (manage_background_music(songName,'is-playing') == False):
     end_game()
     return

def start_game():
    # user-defined function
    # only put logic that'll happen once when the game starts

    global selected_background, my_backgrounds

    selected_background = random.choice(my_backgrounds)

    game_screen_setup()
    manage_background_music(songName, 'play-once')
    manage_background_music(songName, 'change-volume', volume=0.3)
    schedule_callback_every(every_second, 1)

def end_game():
    
    global score, player_name

    cancel_callback_schedule(every_second)
    cancel_callback_schedule(generate_beat)
    end_screen_setup()
    beatList.clear()
    manage_background_music(songName, 'stop')
    update_scores(file_path_10, player_name, score)

def generate_beat(stream_number, direction): # Used to generate beat based on the direction specified and the stream number
    # Your logic to create a beat in the specified stream and direction
    # Example:
    x_position = streams[stream_number].start + (streams[stream_number].stop - streams[stream_number].start) // 2
    beat = create_element(direction + '-beat', centerPos=(x_position, 0))
    beat['direction'] = direction
    beat['moving'] = True
    beat['scoreStatus'] = ''
    beatList.append(beat)


# # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # DO NOT REMOVE THIS LINE!! # # # # # # # #
start_screen_setup()
run_game()
# # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # #