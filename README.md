# Smart Parking Management System

A Python-based graphical parking management system that helps users find and manage parking slots for cars and bikes using pathfinding algorithms.

## Features

- Interactive GUI built with Pygame
- Efficient pathfinding using NetworkX
- Support for both car and bike parking slots
- Real-time visualization of parking paths
- Color-coded slot status indicators
- Multiple entry/exit points
- Slot management system

## Requirements
pygame
networkx


## Installation

pip install pygame networkx

## Usage

Run the main script:
python park1.py

### Controls

- Click on entry points (A or B) to select starting position
- **C**: Find nearest available car slot
- **B**: Find nearest available bike slot
- **R**: Reset all parking slots
- **E**: Empty a specific slot
- **ESC**: Exit application

## Parking Layout

- 14 car slots (C1-C14)
- 14 bike slots (B1-B14)
- 2 entry points (A and B)
- 2 exit points
- Connected road network for pathfinding

## Technical Details

- Uses Manhattan distance for pathfinding
- Implements A* algorithm through NetworkX
- Supports blocked nodes/edges for road maintenance
- Real-time path visualization
- Event-driven architecture
- Slot highlighting system

## Implementation

The system uses:
- NetworkX graph for road network representation
- Pygame for rendering and user interface
- Priority queue for pathfinding
- Enum classes for vehicle types
- Custom classes for parking slots
