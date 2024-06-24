if __name__ == '__main__':
   # with app.app_context():
    #    db.create_all()
        # Create an admin user (run this once)
     #   if not User.query.filter_by(username='admin').first():
     #       admin_user = User(username='admin', email='admin@example.com')
     #       admin_user.set_password('adminpass')
     #       db.session.add(admin_user)
     #       db.session.commit()
    app.run(debug=True)
