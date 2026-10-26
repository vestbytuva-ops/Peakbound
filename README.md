# Peakbound – Pygame

A 2D physics-based driving game developed using **Python and Pygame**, inspired by the original *Hill Climb Racing*.

This project is being developed as part of an **Information Technology 2 (IT2)** school assignment, with a focus on object-oriented programming (OOP), game development, physics simulation, and structured code.

## About the Project

The goal of this project is to create a 2D driving game where players navigate challenging terrain while maintaining control of their vehicle.

The game will feature realistic physics, procedurally generated terrain, and a progression system that allows players to improve their vehicles.

The project also aims to introduce original gameplay elements rather than simply recreating the original game.

## Features

The following features are planned for development:

- **Vehicle Physics:** Gravity, acceleration, friction, and vehicle rotation.
- **Terrain Generation:** Dynamic hills and challenging landscapes.
- **Vehicle Controls:** Acceleration, braking, and balancing.
- **Camera System:** Smooth camera movement that follows the vehicle.
- **Fuel System:** Manage fuel while driving.
- **Coins and Rewards:** Collect currency and earn rewards.
- **Vehicle Upgrades:** Improve engine power, suspension, and other vehicle attributes.
- **Save System:** Store player progress locally using JSON files.
- **User Interface:** Main menu, garage, settings, and in-game HUD.

## Technologies

- **Python** – Main programming language
- **Pygame** – Game development framework
- **JSON** – Local data storage
- **Git & GitHub** – Version control
- **OOP** – Code organization and architecture

## Project Structure

The planned project structure separates game logic, physics, assets, and data into different modules.

```text
HillClimbRacing/
│
├── main.py
├── settings.py
│
├── game/
│   ├── __init__.py
│   ├── game.py
│   ├── vehicle.py
│   ├── physics.py
│   ├── terrain.py
│   ├── camera.py
│   └── ui.py
│
├── assets/
│   ├── images/
│   ├── sounds/
|   ├── stages/
│   └── fonts/
|   
│
├── data/
├── saves/
│
├── requirements.txt
├── .gitignore
└── README.md
```

The structure may change as development progresses.

## Installation

**1. Clone the repository**

Clone this repository to your local computer.

**2. Install dependencies**

Make sure Python is installed, then install Pygame:

```bash
python -m pip install pygame
```

**3. Run the game**

Navigate to the project directory and run:

```bash
python main.py
```

## Controls

The intended basic controls are:

| Key | Action |
|---|---|
| D / Right Arrow | Accelerate |
| A / Left Arrow | Brake / Reverse |
| Escape | Exit game |

Controls may change during development.

## Development Goals

The main objectives of this project are to:

1. Apply object-oriented programming principles.
2. Build a modular and maintainable codebase.
3. Implement physics-based vehicle movement.
4. Develop terrain generation and collision detection.
5. Create an interactive graphical user interface.
6. Implement persistent player data using JSON.
7. Improve problem-solving and debugging skills.

## Project Status

**Currently in development.**

The project is in its early stages. Core gameplay mechanics, vehicle physics, and additional features will be developed progressively.

## Disclaimer

This is an independent educational project inspired by *Hill Climb Racing*. It is not affiliated with or endorsed by the creators of the original game.
