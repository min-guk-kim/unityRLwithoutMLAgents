# Unity Reinforcement Learning Environment

This project provides a custom interface for training reinforcement learning agents within a Unity environment without relying on MLAgents. The primary goal is to integrate Unity with Python-based reinforcement learning algorithms.

## Table of Contents
1. [Description](#description)
2. [Setup & Installation](#setup-&-installation)
3. [Usage](#usage)
4. [Files & Directories](#files-&-directories)

## Description

The project consists of a Unity environment wherein a cube agent can be trained to achieve an optimal wayfinding task in 5x5 grid world. The agent will be trained based on Q-learning algorithm.

## Setup & Installation

**Requirements (still in progress)**:
- Unity 2020 or newer
- Python 3.7 or newer
- Jupyter (for `.ipynb` notebook execution)

1. Clone this repository:
   ```bash
   git clone [REPOSITORY_LINK]
   ```
2. Navigate to the Unity project directory and open it with the Unity editor.

3. (Coming Soon) Install necessary Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Unity environment.
2. In the project's root directory, execute the Jupyter notebook:
   ```bash
   jupyter notebook training.ipynb
   ```

## Files & Directories

- **CSharpForGIT.cs**: A Unity script managing the communication between the Unity engine and Python, facilitating the data transmission and reception.
- **unity_env.py**: Contains the Unity environment logic and how the agent interacts within this environment.
- **cube_agent.py**: Defines the agent's logic, actions, and policy for interaction with the Unity environment.
- **communication.py**: Oversees the TCP/IP communication protocol between Unity and Python.
- **training.ipynb**: A Jupyter notebook outlining the steps and procedures for training the agent.