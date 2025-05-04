from ursina import Ursina, Button, Text, Entity, color, scene, camera, application, mouse
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Load a pixelated font
pixel_font = 'minecraft/Pixeboy.ttf'

# Player setup
player = FirstPersonController()
player.visible = False
player.jump_height = 2

# Block types
grass_texture = 'textures/grass'
dirt_texture = 'textures/dirt'
stone_texture = 'textures/stone'
wood_texture = 'textures/wood'
current_block = 0
block_types = [grass_texture, dirt_texture, stone_texture, wood_texture]

# World + chunks
max_world_size = 28
chunk_size = 10
loaded_chunks = {}

def generate_chunk(x, z):
    for i in range(chunk_size):
        for j in range(chunk_size):
            grass_position = (j + x * chunk_size, 0, i + z * chunk_size)
            Button(color=color.white, model='cube', position=grass_position,
                   texture=grass_texture, parent=scene, origin_y=0.5)

            for k in range(1, 4):
                dirt_position = (j + x * chunk_size, -k, i + z * chunk_size)
                Button(color=color.white, model='cube', position=dirt_position,
                       texture=dirt_texture, parent=scene, origin_y=0.5)

def load_chunks():
    player_chunk_x = int(player.x // chunk_size)
    player_chunk_z = int(player.z // chunk_size)

    for x in range(player_chunk_x - 1, player_chunk_x + 2):
        for z in range(player_chunk_z - 1, player_chunk_z + 2):
            if 0 <= x * chunk_size < max_world_size and 0 <= z * chunk_size < max_world_size:
                if (x, z) not in loaded_chunks:
                    generate_chunk(x, z)
                    loaded_chunks[(x, z)] = True

# HUD
hud = Text(text='', parent=camera.ui, position=(0, 0.45), origin=(0, 0), scale=2, font=pixel_font)

# Pause menu
pause_menu = Entity(parent=camera.ui, model='quad', scale=(1.5, 1), color=color.rgba(0, 0, 0, 200), enabled=False)
pause_title = Text(text='PAUSED', parent=pause_menu, position=(0, 0.3), origin=(0, 0), scale=3, font=pixel_font, color=color.white)

resume_button = Button(text='Resume', parent=pause_menu, position=(0, 0.1), scale=(0.3, 0.1),
                       color=color.green, on_click=lambda: toggle_pause(False), hover_color=color.light_gray)
resume_button.text_entity.color = color.black

quit_button = Button(text='Quit', parent=pause_menu, position=(0, -0.1), scale=(0.3, 0.1),
                     color=color.red, on_click=application.quit, hover_color=color.light_gray)
quit_button.text_entity.color = color.black

def update():
    x, y, z = player.position
    hud.text = f'Current block: {block_types[current_block]}\nCoordinates: ({int(x)}, {int(y)}, {int(z)})'
    load_chunks()

def toggle_pause(is_paused):
    pause_menu.enabled = is_paused
    player.enabled = not is_paused
    application.paused = is_paused

def input(key):
    global current_block
    if key == 'escape':
        toggle_pause(not pause_menu.enabled)
    if key == 'tab':
        current_block = (current_block + 1) % len(block_types)
        print(f"Current block: {block_types[current_block]}")
    if key == 'right mouse down':
        for box in scene.children:
            if isinstance(box, Button) and box.hovered:
                if not player.intersects(box).hit:
                    new_block_position = box.position + mouse.normal
                    if (0 <= new_block_position.x < max_world_size) and (0 <= new_block_position.z < max_world_size):
                        new_block = Button(color=color.white, model='cube', position=new_block_position,
                                           texture=block_types[current_block], parent=scene, origin_y=0.5)
                        loaded_chunks[(int(new_block.x // chunk_size), int(new_block.z // chunk_size))] = True
                break
    if key == 'left mouse down':
        for box in scene.children:
            if isinstance(box, Button) and box.hovered:
                box.disable()
                loaded_chunks[(int(box.x // chunk_size), int(box.z // chunk_size))] = False
                break

app.run()