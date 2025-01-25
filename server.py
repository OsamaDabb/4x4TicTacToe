from flask import Flask, request, jsonify

app = Flask(__name__)
games = {}  # Dictionary to store game sessions

@app.route("/create_game", methods=["POST"])
def create_game():
    game_id = request.json.get("game_id")
    if game_id in games:
        return jsonify({"status": "success", "message": "Game ID already exists"}), 202
    games[game_id] = {"moves": []}
    return jsonify({"status": "success", "message": f"Game {game_id} created"}), 201

@app.route("/send_move", methods=["POST"])
def send_move():
    game_id = request.json.get("game_id")
    move = request.json.get("move")
    if game_id not in games:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    games[game_id]["moves"].append(move)
    return jsonify({"status": "success"}), 200

@app.route("/get_moves/<game_id>", methods=["GET"])
def get_moves(game_id):
    if game_id not in games:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    return jsonify({"moves": games[game_id]["moves"]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
