import networkx as nx
import pygame
from pygame.locals import *
import heapq
import math
from enum import Enum

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
SLOT_SIZE = 30
ROAD_WIDTH = 25

# colour
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 53, 69)       
GREEN = (40, 167, 69)      
BLUE = (0, 123, 255)       
GRAY = (108, 117, 125)     
YELLOW = (255, 193, 7)     
ORANGE = (253, 126, 20)    
LIGHT_BLUE = (240, 248, 255)  
TEXT_COLOR = (52, 58, 64)  
HIGHLIGHT_COLOR = (23, 162, 184)  

#UI 
TEXT_SIZE = 28
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 200
BUTTON_MARGIN = 10
SLOT_WIDTH = 80
SLOT_HEIGHT = 60
BIKE_SLOT_WIDTH = 50
BIKE_SLOT_HEIGHT = 40

class VehicleType(Enum):
    CAR = "Car"
    BIKE = "Bike"

class ParkingSlot:
    def __init__(self, position, slot_type, number):
        self.position = position
        self.type = slot_type
        self.number = number
        self.occupied = False
        self.highlighted = False
        self.highlight_timer = 0

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Smart Parking Management System")

font = pygame.font.Font(None, TEXT_SIZE)

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def find_path(graph, start, end):
    if start not in graph or end not in graph:
        return [], float('inf')
    
    pq = [(0, start, [])]
    visited = set()
    
    while pq:
        cost, current, path = heapq.heappop(pq)        
        if current == end:
            return path + [current], cost            
        if current in visited:
            continue
            
        visited.add(current)
        
        for next_node in graph.neighbors(current):
            if next_node not in visited and next_node not in blocked_nodes:
                edge = (current, next_node)
                if edge not in blocked_edges and (next_node, current) not in blocked_edges:
                    new_cost = cost + graph.edges[current, next_node]['weight']
                    heapq.heappush(pq, (new_cost, next_node, path + [current]))
    
    return [], float('inf')

def draw_rounded_rect(surface, color, rect, radius=10):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def create_button(text, position, width=BUTTON_WIDTH, height=BUTTON_HEIGHT):
    """Create a button with hover effect"""
    rect = pygame.Rect(position[0], position[1], width, height)
    mouse_pos = pygame.mouse.get_pos()
    color = HIGHLIGHT_COLOR if rect.collidepoint(mouse_pos) else GRAY
    draw_rounded_rect(screen, color, rect)
    
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return rect

def draw_parking_system(graph, car_slots, bike_slots, current_path=None):
    screen.fill(LIGHT_BLUE)
    
    for e in graph.edges:
        color = RED if e in blocked_edges else GRAY
        start_pos = graph.nodes[e[0]]['pos']
        end_pos = graph.nodes[e[1]]['pos']
        pygame.draw.line(screen, color, start_pos, end_pos, ROAD_WIDTH)
    
    if current_path:
        for i in range(len(current_path)-1):
            start = graph.nodes[current_path[i]]['pos']
            end = graph.nodes[current_path[i+1]]['pos']
            pygame.draw.line(screen, (*YELLOW, 128), start, end, ROAD_WIDTH+4)
            pygame.draw.line(screen, YELLOW, start, end, ROAD_WIDTH-4)

    current_time = pygame.time.get_ticks()
    
    for node, data in graph.nodes(data=True):
        if data['type'] == "entry":
            pygame.draw.circle(screen, (*GREEN, 128), data['pos'], SLOT_SIZE + 5)
            pygame.draw.circle(screen, GREEN, data['pos'], SLOT_SIZE)
    
            label_bg_rect = pygame.Rect(data['pos'][0] - 50, data['pos'][1] - 60, 100, 40)
            draw_rounded_rect(screen, (*WHITE, 230), label_bg_rect)
            draw_rounded_rect(screen, GREEN, label_bg_rect, 2)  
    
            text = font.render(f"ENTRY {data['entry_label']}", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(data['pos'][0], data['pos'][1] - 40))
            screen.blit(text, text_rect)
            
        elif data['type'] == "exit":
            pygame.draw.circle(screen, (*RED, 128), data['pos'], SLOT_SIZE + 5)
            pygame.draw.circle(screen, RED, data['pos'], SLOT_SIZE)
            
            exit_num = "1" if data['pos'][1] < WINDOW_HEIGHT/2 else "2"
            
            label_bg_rect = pygame.Rect(data['pos'][0] - 50, data['pos'][1] - 60, 100, 40)
            draw_rounded_rect(screen, (*WHITE, 230), label_bg_rect)
            draw_rounded_rect(screen, RED, label_bg_rect, 2)  
            
            text = font.render(f"EXIT {exit_num}", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(data['pos'][0], data['pos'][1] - 40))
            screen.blit(text, text_rect)
            
        elif data['type'] == "car_slot":
            slot = car_slots[node]
            if slot.highlighted:
                if current_time - slot.highlight_timer > 2000:
                    slot.highlighted = False
                color = HIGHLIGHT_COLOR
            else:
                color = RED if slot.occupied else GREEN
            
            shadow_rect = (node[0]-42, node[1]-28, SLOT_WIDTH+4, SLOT_HEIGHT+4)
            slot_rect = (node[0]-40, node[1]-30, SLOT_WIDTH, SLOT_HEIGHT)
            draw_rounded_rect(screen, (*BLACK, 64), shadow_rect)
            draw_rounded_rect(screen, color, slot_rect)
            
            text = font.render(slot.number, True, WHITE)
            screen.blit(text, (node[0]-15, node[1]-10))
            
        elif data['type'] == "bike_slot":
            slot = bike_slots[node]
            if slot.highlighted:
                if current_time - slot.highlight_timer > 2000:
                    slot.highlighted = False
                color = HIGHLIGHT_COLOR
            else:
                color = RED if slot.occupied else BLUE
            
            shadow_rect = (node[0]-27, node[1]-18, BIKE_SLOT_WIDTH+4, BIKE_SLOT_HEIGHT+4)
            slot_rect = (node[0]-25, node[1]-20, BIKE_SLOT_WIDTH, BIKE_SLOT_HEIGHT)
            draw_rounded_rect(screen, (*BLACK, 64), shadow_rect)
            draw_rounded_rect(screen, color, slot_rect)
            
            text = font.render(slot.number, True, WHITE)
            screen.blit(text, (node[0]-15, node[1]-10))
    
    # Draw control panel in bottom right corner
    panel_width = 280
    panel_height = 200
    margin = 20
    panel_rect = pygame.Rect(
        WINDOW_WIDTH - panel_width - margin,
        WINDOW_HEIGHT - panel_height - margin,
        panel_width,
        panel_height
    )
    
    draw_rounded_rect(screen, (*WHITE, 230), panel_rect)    
    header_rect = pygame.Rect(
        panel_rect.x,
        panel_rect.y,
        panel_width,
        40
    )
    draw_rounded_rect(screen, HIGHLIGHT_COLOR, header_rect)
    
    title = font.render("Controls", True, WHITE)
    title_rect = title.get_rect(center=(header_rect.centerx, header_rect.centery))
    screen.blit(title, title_rect)
    
    instructions = [
        ("C - Find car slot", GREEN),
        ("B - Find bike slot", BLUE),
        ("R - Reset all slots", GRAY),
        ("E - Empty slot", RED),
        ("ESC - Exit", TEXT_COLOR)
    ]
    
    for i, (text, color) in enumerate(instructions):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (panel_rect.x + 20, panel_rect.y + 50 + i*28))
    
    pygame.display.flip()

def create_parking_layout():
    g = nx.Graph()
    
    entries = [((100, 50), "A"), ((100, 750), "B")]  
    
    for pos, label in entries:
        g.add_node(pos, pos=pos, label=f"ENTRY {label}", type="entry", entry_label=label)       
    road_nodes = []
    
    for x in [100, 300, 600, 700, 1100]:
        for y in range(50, 751, 50):
            pos = (x, y)
            g.add_node(pos, pos=pos, label="", type="road")
            road_nodes.append(pos)
    
    for y in [50, 750]:
        for x in range(100, 1151, 50):
            pos = (x, y)
            if pos not in g:
                g.add_node(pos, pos=pos, label="", type="road")
                road_nodes.append(pos)
    
    for i, node1 in enumerate(road_nodes):
        for node2 in road_nodes[i+1:]:
            if manhattan_distance(node1, node2) == 50:
                g.add_edge(node1, node2, weight=1)
    
    car_slots = {}
    bike_slots = {}
    
    # Left car slots
    for row in range(7):
        x = 200
        y = 150 + row * 80
        pos = (x, y)
        slot_num = f"C{row + 1}"
        car_slots[pos] = ParkingSlot(pos, VehicleType.CAR, slot_num)
        g.add_node(pos, pos=pos, label=slot_num, type="car_slot")
        
        nearest_road = min(road_nodes, key=lambda n: manhattan_distance(n, pos))
        g.add_edge(pos, nearest_road, weight=1)
    
    # Bike slots
    for row in range(7):
        for col in range(2):
            x = 450 + col * 100
            y = 150 + row * 80
            pos = (x, y)
            slot_num = f"B{row * 2 + col + 1}"
            bike_slots[pos] = ParkingSlot(pos, VehicleType.BIKE, slot_num)
            g.add_node(pos, pos=pos, label=slot_num, type="bike_slot")
            
            nearest_road = min(road_nodes, key=lambda n: manhattan_distance(n, pos))
            g.add_edge(pos, nearest_road, weight=1)
    
    # Right car slots
    for row in range(7):
        x = 800
        y = 150 + row * 80
        pos = (x, y)
        slot_num = f"C{row + 8}"
        car_slots[pos] = ParkingSlot(pos, VehicleType.CAR, slot_num)
        g.add_node(pos, pos=pos, label=slot_num, type="car_slot")
        
        nearest_road = min(road_nodes, key=lambda n: manhattan_distance(n, pos))
        g.add_edge(pos, nearest_road, weight=1)
    
    return g, car_slots, bike_slots, entries

def find_nearest_available_slot(graph, start_pos, slots, vehicle_type):
    available_slots = [pos for pos, slot in slots.items() if not slot.occupied and slot.type == vehicle_type]
    if not available_slots:
        return None, None, None
    
    best_path = None
    best_distance = float('inf')
    best_slot = None
    
    for slot_pos in available_slots:
        path, distance = find_path(graph, start_pos, slot_pos)
        if path and distance < best_distance:
            best_path = path
            best_distance = distance
            best_slot = slot_pos
    
    return best_path, best_distance, best_slot

def get_slot_number():
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = True
    text = ''
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    done = True
                elif event.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        
        screen.fill((240, 240, 245))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        
        prompt = font.render("Enter slot number (e.g., C1, B1):", True, BLACK)
        screen.blit(prompt, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 60))
        
        pygame.display.flip()    
    return text.strip()


def empty_slot(slot_num, car_slots, bike_slots):
    current_time = pygame.time.get_ticks()
    found = False
    
    if slot_num.startswith('C'):
        for pos, slot in car_slots.items():
            if slot.number == slot_num and slot.occupied:
                slot.occupied = False
                
                slot.highlighted = True
                slot.highlight_timer = current_time
                found = True
                print(f"Emptied car slot {slot_num}")
                break
    elif slot_num.startswith('B'):
        for pos, slot in bike_slots.items():
            if slot.number == slot_num and slot.occupied:
                slot.occupied = False
                slot.highlighted = True
                slot.highlight_timer = current_time
                found = True
                print(f"Emptied bike slot {slot_num}")
                break
    
    return found

def main():
    graph, car_slots, bike_slots, entries= create_parking_layout()
    entry_positions = {pos for pos, label in entries}
    current_path = None
    selected_entry = None
    running = True
    
    while running:
        draw_parking_system(graph, car_slots, bike_slots, current_path)
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
                pygame.quit()
                return
                
            elif event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                for entry_pos in entry_positions:
                    if math.dist(entry_pos, pos) < SLOT_SIZE:
                        selected_entry = entry_pos
                        current_path = None
                        print(f"Selected entry point at {entry_pos}")
            
            elif event.type == KEYDOWN:
                if event.key == K_c and selected_entry:  # Find car slot
                    path, distance, slot_pos = find_nearest_available_slot(graph, selected_entry, car_slots, VehicleType.CAR)
                    if slot_pos:
                        current_path = path
                        car_slots[slot_pos].occupied = True
                        print(f"Found car slot {car_slots[slot_pos].number} at distance {distance}")
                    else:
                        print("No available car slots!")
                        
                elif event.key == K_b and selected_entry:  # Find bike slot
                    path, distance, slot_pos = find_nearest_available_slot(graph, selected_entry, bike_slots, VehicleType.BIKE)
                    if slot_pos:
                        current_path = path
                        bike_slots[slot_pos].occupied = True
                        print(f"Found bike slot {bike_slots[slot_pos].number} at distance {distance}")
                    else:
                        print("No available bike slots!")
                        
                elif event.key == K_r:  # Reset all slots
                    for slot in car_slots.values():
                        slot.occupied = False
                        slot.highlighted = False
                    for slot in bike_slots.values():
                        slot.occupied = False
                        slot.highlighted = False
                    current_path = None
                    print("All slots reset!")
                
                elif event.key == K_e:  # Empty specific slot
                    slot_num = get_slot_number()
                    if slot_num:
                        if not empty_slot(slot_num, car_slots, bike_slots):
                            print(f"Slot {slot_num} not found or already empty!")


if __name__ == "__main__":
    blocked_nodes = set()
    blocked_edges = set()
    main()