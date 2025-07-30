from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flashing messages

# Load initial painting data
PAINTINGS = [
    {"id": 1, "title": "Painting 1", "image": "painting1.jpg", "bid": 0, "name": ""},
    {"id": 2, "title": "Painting 2", "image": "painting2.jpg", "bid": 0, "name": ""},
    {"id": 3, "title": "Painting 3", "image": "painting3.jpg", "bid": 0, "name": ""},
    {"id": 4, "title": "Painting 4", "image": "painting4.jpg", "bid": 0, "name": ""},
    {"id": 5, "title": "Painting 5", "image": "painting5.jpg", "bid": 0, "name": ""},
    {"id": 6, "title": "Painting 6", "image": "painting6.jpg", "bid": 0, "name": ""},
    {"id": 7, "title": "Painting 7", "image": "painting7.jpg", "bid": 0, "name": ""},
    {"id": 8, "title": "Painting 8", "image": "painting8.jpg", "bid": 0, "name": ""}
]

@app.route('/')
def index():
    return render_template("index.html", paintings=PAINTINGS)

@app.route('/bid/<int:painting_id>', methods=["GET", "POST"])
def bid(painting_id):
    painting = next((p for p in PAINTINGS if p["id"] == painting_id), None)
    if not painting:
        return "Painting not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        try:
            amount = float(request.form.get("amount"))
        except:
            flash("Invalid amount")
            return redirect(url_for("bid", painting_id=painting_id))

        if amount > painting["bid"]:
            painting["bid"] = amount
            painting["name"] = name
            flash("Bid placed successfully!")
            return redirect(url_for("index"))
        else:
            flash(f"Your bid must be higher than ${painting['bid']}")
            return redirect(url_for("bid", painting_id=painting_id))

    return render_template("bid.html", painting=painting)

if __name__ == '__main__':
    app.run(debug=True)
