import requests

SERVER_URL = "https://fourx4tictactoe.onrender.com"

def create_game(game_id):
    response = requests.post(f"{SERVER_URL}/create_game", json={"game_id": game_id})
    return response.json()

def send_move(game_id, move):
    response = requests.post(f"{SERVER_URL}/send_move", json={"game_id": game_id, "move": move})
    return response.json()

def get_moves(game_id):
    response = requests.get(f"{SERVER_URL}/get_moves/{game_id}")
    if response.status_code == 200:
        return response.json()["moves"]
    return []
