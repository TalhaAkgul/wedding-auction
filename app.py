from flask import Flask, render_template, request, redirect, url_for, flash
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-key")

# Initialize Firebase
# Replace with your actual file name
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load painting IDs to display (IDs 1 to 8)
PAINTING_IDS = [str(i) for i in range(1, 9)]


@app.route('/')
def index():
    paintings = []
    for pid in PAINTING_IDS:
        doc = db.collection("paintings").document(pid).get()
        if doc.exists:
            data = doc.to_dict()

            # Get highest bid from subcollection
            bids_ref = db.collection("paintings").document(
                pid).collection("bids")
            top_bid = bids_ref.order_by(
                "amount", direction=firestore.Query.DESCENDING).limit(1).get()
            if top_bid:
                highest_bid = top_bid[0].to_dict()
                amount = highest_bid.get("amount", 0)
                name = highest_bid.get("name", "")
            else:
                amount = 0
                name = ""

            paintings.append({
                "id": pid,
                "title": data.get("title", f"Painting {pid}"),
                "image": data.get("image", f"painting{pid}.jpg"),
                "bid": amount,
                "name": name
            })
    return render_template("index.html", paintings=paintings)


@app.route('/bid/<painting_id>', methods=["GET", "POST"])
def bid(painting_id):
    painting_ref = db.collection("paintings").document(painting_id)
    doc = painting_ref.get()
    if not doc.exists:
        return "Painting not found", 404

    painting = doc.to_dict()
    painting.setdefault("title", f"Painting {painting_id}")
    painting.setdefault("image", f"painting{painting_id}.jpg")

    # Get highest current bid
    bids_ref = painting_ref.collection("bids")
    top_bid = bids_ref.order_by(
        "amount", direction=firestore.Query.DESCENDING).limit(1).get()
    current_bid = top_bid[0].to_dict()["amount"] if top_bid else 0

    if request.method == "POST":
        name = request.form.get("name")
        try:
            amount = float(request.form.get("amount"))
        except:
            flash("Invalid amount")
            return redirect(url_for("bid", painting_id=painting_id))

        if amount > current_bid:
            bids_ref.add({
                "name": name,
                "amount": amount,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            flash("Bid placed successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash(f"Your bid must be higher than DKK {current_bid}", "error")
            return redirect(url_for("bid", painting_id=painting_id))

    return render_template("bid.html", painting={
        "id": painting_id,
        "title": painting["title"],
        "image": painting["image"],
        "bid": current_bid
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
