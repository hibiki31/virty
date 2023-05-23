from main import app, db, setup_ip



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        setup_ip()
    app.run(host="0.0.0.0", port=8766, debug=True)