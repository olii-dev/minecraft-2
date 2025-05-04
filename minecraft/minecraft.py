from ursina import Ursina, Button, Text, Entity, color, scene, camera, application, mouse
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Load the font
pixel_font = 'minecraft/Pixeboy.ttf'

# Player setup
player = FirstPersonController()
player.visible = False
player.jump_height = 2

# Block types
grass_texture = 'grass'
dirt_texture = 'dirt'
stone_texture = 'stone'
wood_texture = 'wood'
current_block = 0
block_types = [grass_texture, dirt_texture, stone_texture, wood_texture]

# Grid size and chunk size
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

# Pause Menu
pause_menu = Entity(parent=camera.ui, model='quad', scale=(1.5, 1), color=color.rgba(0, 0, 0, 200), enabled=False)
pause_title = Text(text='PAUSED', parent=pause_menu, position=(0, 0.3), origin=(0, 0), scale=3, font=pixel_font, color=color.white)
resume_button = Button(text='Resume', parent=pause_menu, position=(0, 0.1), scale=(0.3, 0.1),
                       color=color.green, on_click=lambda: toggle_pause(False), hover_color=color.light_gray)
resume_button.text_entity.color = color.black
quit_button = Button(text='Quit', parent=pause_menu, position=(0, -0.1), scale=(0.3, 0.1),
                     color=color.red, on_click=application.quit, hover_color=color.light_gray)
quit_button.text_entity.color = color.black

# Hotbar
hotbar_slots = []
hotbar_background = Entity(parent=camera.ui, model='quad', scale=(0.4, 0.08), position=(0, -0.45),
              color=color.black.tint(0.6), origin=(0, 0), corner_radius=0.02)
hotbar_highlight = None

def create_hotbar():
    global hotbar_highlight
    for i, texture in enumerate(block_types):
        slot = Entity(parent=camera.ui, model='quad', texture=texture,
                      scale=(0.05, 0.05), position=(-0.15 + i * 0.1, -0.45),
                      color=color.white, origin=(0, 0))
        hotbar_slots.append(slot)

    hotbar_highlight = Entity(parent=camera.ui, model='circle',
            scale=(0.03, 0.03), position=hotbar_slots[0].position,
            color=color.yellow.tint(-.2), origin=(0, 0))

create_hotbar()

# Update
def update():
    x, y, z = player.position
    hud.text = f'Current block: {block_types[current_block]}\nCoordinates: ({int(x)}, {int(y)}, {int(z)})'
    hotbar_highlight.position = hotbar_slots[current_block].position
    load_chunks()

# Toggle pause
def toggle_pause(is_paused):
    pause_menu.enabled = is_paused
    player.enabled = not is_paused
    application.paused = is_paused

# Input
def input(key):
    global current_block
    if key == 'escape':
        toggle_pause(not pause_menu.enabled)
    if key == 'tab':
        current_block = (current_block + 1) % len(block_types)
        hotbar_highlight.position = hotbar_slots[current_block].position
    if key in ['1', '2', '3', '4']:
        index = int(key) - 1
        if index < len(block_types):
            current_block = index
            hotbar_highlight.position = hotbar_slots[current_block].position
    if key == 'right mouse down':
        for box in scene.children:
            if isinstance(box, Button) and box.hovered:
                if not player.intersects(box).hit:
                    new_block_position = box.position + mouse.normal
                    if (0 <= new_block_position.x <= max_world_size) and (0 <= new_block_position.z <= max_world_size):
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