import streamlit as st
import pymongo
from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://yashrawal987:Uo9WhVC25AQkoruW@cluster0.aoauzkm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['streamlit_auth']
collection = db['users']

def check_email_exists(email):
    return collection.find_one({"email": email}) is not None

def main():
    st.title("User Authentication")

    # Create form for user input
    with st.form("authentication_form"):
        username = st.text_input("User Name")
        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")
        check_password = st.text_input("Check Password", type="password")
        submit_button = st.form_submit_button("Submit")

        # Validate password
        if submit_button:
            if password != check_password:
                st.error("Passwords do not match. Please try again.")
            elif check_email_exists(email):
                st.error("Email ID already exists in the database.")
            else:
                # Insert user data into MongoDB Atlas
                user_data = {
                    "username": username,
                    "email": email,
                    "password": password
                }
                collection.insert_one(user_data)
                st.success("Authentication successful!")

if __name__ == "__main__":
    main()
