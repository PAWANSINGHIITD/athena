from flask import Flask, render_template, request, jsonify, redirect, url_for
from converters import NumeralConverter
import json, os

app = Flask(__name__)
converter = NumeralConverter()

# load puzzles and systems metadata
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
with open(os.path.join(DATA_DIR, "systems.json"), "r", encoding="utf-8") as f:
    SYSTEMS = json.load(f)
with open(os.path.join(DATA_DIR, "puzzles.json"), "r", encoding="utf-8") as f:
    PUZZLES = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", systems=SYSTEMS)

@app.route("/library")
def library():
    return render_template("library.html", systems=SYSTEMS)

@app.route("/system/<key>")
def system_detail(key):
    sysdata = SYSTEMS.get(key)
    if not sysdata:
        return "System not found", 404
    return render_template("system.html", key=key, system=sysdata)

@app.route("/converter", methods=["GET","POST"])
def converter_page():
    result = None
    explanation = None
    if request.method == "POST":
        mode = request.form.get("mode")
        system = request.form.get("system")
        text = request.form.get("text","").strip()
        try:
            if mode == "to_culture":
                n = int(text)
                conversion, explanation = converter.convert_with_explanation(n, system)
                result = conversion
            else:
                value, explanation = converter.parse_with_explanation(text, system)
                result = value
        except Exception as e:
            result = f"Error: {e}"
    return render_template("converter.html", systems=SYSTEMS, result=result, explanation=explanation)

@app.route("/practice")
def practice():
    return render_template("practice.html", puzzles=PUZZLES)

@app.route("/practice/<pid>", methods=["GET","POST"])
def practice_puzzle(pid):
    puzzle = next((p for p in PUZZLES if p["id"]==pid), None)
    feedback = None
    if not puzzle:
        return "Puzzle not found", 404
    if request.method=="POST":
        ans = request.form.get("answer","").strip().lower()
        correct = puzzle["answer"].strip().lower()
        if ans == correct:
            feedback = "Correct! Well done."
        else:
            feedback = f"Not quite. Expected: {puzzle['answer']}"
    return render_template("puzzle.html", puzzle=puzzle, feedback=feedback)

@app.route("/api/convert", methods=["POST"])
def api_convert():
    body = request.get_json()
    mode = body.get("mode")
    system = body.get("system")
    text = body.get("text")
    if mode=="to_culture":
        n = int(text)
        conv, exp = converter.convert_with_explanation(n, system)
        return jsonify({"result":conv, "explanation":exp})
    else:
        val, exp = converter.parse_with_explanation(text, system)
        return jsonify({"result":val, "explanation":exp})

if __name__=="__main__":
    app.run(debug=True, port=4000) 
