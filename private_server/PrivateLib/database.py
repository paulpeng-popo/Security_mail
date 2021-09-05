import pyrebase

config = {
    "apiKey": "AIzaSyDzw4qxT7QKBrK3ge7uLqcfp9ibLsKrSpM",
    "authDomain": "nsysu-mail-project.firebaseapp.com",
    "databaseURL": "https://nsysu-mail-project-default-rtdb.firebaseio.com",
    "projectId": "nsysu-mail-project",
    "storageBucket": "nsysu-mail-project.appspot.com",
    "messagingSenderId": "852787793793"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# db.child("users").child("Paul").set({"email":"admin@example.com", "public key":"abc"})
# db.child("users").child("Jack").set({"email":"user2@example.com", "public key":"ghijk"})
# db.child("users").child("Morty").set({"email":"user1@example.com", "public key":"cdef"})

db.child("users").push({"email":"admin@example.com", "public key":"abc"})
db.child("users").push({"email":"user2@example.com", "public key":"ghijk"})
db.child("users").push({"email":"user1@example.com", "public key":"cdef"})

dd = db.child("users").order_by_child("email").equal_to("admin@example.com").get()
print(list(dd.val().items())[0][1]["public key"])

abc = db.child("users").get().val()
for k, v in abc.items():
    print(k, "-->", v)
