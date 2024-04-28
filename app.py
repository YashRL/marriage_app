import streamlit as st
from pymongo import MongoClient
import datetime
import uuid

# Connect to MongoDB and create a new database and collection
client = MongoClient("mongodb+srv://yashrawal987:Uo9WhVC25AQkoruW@cluster0.aoauzkm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['new_database']  # New database
collection = db['new_collection']  # New collection

def post_page():
    st.title("Post Page")
    
    # Add a centered image
    st.image("1.jpg", use_column_width=True)

    # Type of Brahmin
    type_of_brahmin = st.text_input("Type of Brahmin (ब्राह्मण का प्रकार)")

    # Gotra
    gotra = st.text_input("Gotra (गोत्र)")

    # Name
    name = st.text_input("Name (नाम)")

    # Father Name
    father_name = st.text_input("Father Name (पिता का नाम)")

    # Mother Name
    mother_name = st.text_input("Mother Name (माँ का नाम)")

    # Sex
    sex = st.radio("Gender (लिंग)", ["Male", "Female"])

    # Date of Birth
    current_year = datetime.datetime.now().year
    min_birth_year = 1980
    dob = st.date_input("Date of Birth (जन्म की तारीख)", min_value=datetime.date(min_birth_year, 1, 1), max_value=datetime.date(current_year, 12, 31))

    # Time of Birth
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        hour = st.number_input("Hour (0-12)", min_value=0, max_value=12, step=1)
    with col2:
        minute = st.number_input("Minute (0-59)", min_value=0, max_value=59, step=1)
    with col3:
        am_pm = st.radio("AM/PM", ["AM", "PM"])

    # Place of Birth
    place_of_birth = st.text_area("Place of Birth (जन्म स्थान)")

    # Height
    height_feet = st.number_input("Height (Feet)")
    height_meter = st.number_input("Height (Meter)")

    # Body Type
    body_type = st.text_input("Body Type (शरीर के प्रकार)")

    # Color
    color = st.text_input("Color (रंग)")

    # Manglik Dosh
    manglik_dosh = st.radio("Manglik Dosh (मांगलिक दोष)", ["Yes", "No"])

    # Education
    education = st.text_area("Education (शिक्षा)")

    # Job/Work/Occupation
    occupation = st.text_input("Job/Work/Occupation (नौकरी/कार्य/व्यवसाय)")

    # Income
    income = st.text_input("Income (आय)")

    # Agriculture
    agriculture = st.radio("Agriculture (कृषि)", ["Yes", "No"])

    # Other Income Sources
    other_income_sources = st.text_area("Other Income Sources (अन्य आय स्रोत)")

    # Diet
    diet = st.selectbox("Diet (आहार)", ["Vegetarian (शाकाहारी)", "Non-Vegetarian (मांसाहारी)", "Vegan (दूध ना पाइन वाले)", "Other (अन्य)"])

    # Siblings
    siblings = st.text_area("Siblings (भाई-बहन)")

    # Permanent Address
    permanent_address = st.text_area("Permanent Address (स्थायी पता)")

    # Current Address
    current_address = st.text_area("Current Address (वर्त्तमान पता)")

    # Contact No.
    contact_no = st.text_input("Contact No. (संपर्क नंबर।)")

    # Mail
    mail = st.text_input("Mail (मेल)")

    # Postrer's Name
    postrers_name = st.text_input("Postrer's Name (प्रेषक का नाम)")

    # Additional Comments
    additional_comments = st.text_area("Additional Comments (अतिरिक्त टिप्पणियां)")

    # Process the form data when the main "Submit" button is clicked
    if st.button("Submit"):
        if 1 <= hour <= 12 and 0 <= minute <= 59:
            time_of_birth = f"{hour:02d}:{minute:02d} {am_pm}"
            # Create a document
            user_data = {
                "Type of Brahmin": type_of_brahmin,
                "Gotra": gotra,
                "Name": name,
                "Father Name": father_name,
                "Mother Name": mother_name,
                "Sex": sex,
                "Date of Birth": dob.strftime("%Y-%m-%d"),  # Convert date to string
                "Time of Birth": time_of_birth,
                "Place of Birth": place_of_birth,
                "Height (Feet)": height_feet,
                "Height (Meter)": height_meter,
                "Body Type": body_type,
                "Color": color,
                "Manglik Dosh": manglik_dosh,
                "Education": education,
                "Job/Work/Occupation": occupation,
                "Income": income,
                "Agriculture": agriculture,
                "Other Income Sources": other_income_sources,
                "Diet": diet,
                "Siblings": siblings,
                "Permanent Address": permanent_address,
                "Current Address": current_address,
                "Contact No.": contact_no,
                "Mail": mail,
                "Postrer's Name": postrers_name,
                "Additional Comments": additional_comments
            }

            # Insert the document into the new collection
            collection.insert_one(user_data)

            st.write("Form submitted successfully!")

def search_page():
    st.title("Search Page")
    
    # Add a centered image
    st.image("1.jpg", use_column_width=True)

    # Retrieve all documents from the collection
    documents = collection.find()

    # Display each document in a card view
    for document in documents:
        st.write("---")
        st.write(f"Type of Brahmin: {document['Type of Brahmin']}")
        st.write(f"Gotra: {document['Gotra']}")
        st.write(f"Name: {document['Name']}")
        st.write(f"Father Name: {document['Father Name']}")
        st.write(f"Mother Name: {document['Mother Name']}")
        st.write(f"Sex: {document['Sex']}")
        st.write(f"Date of Birth: {document['Date of Birth']}")
        st.write(f"Time of Birth: {document['Time of Birth']}")
        st.write(f"Place of Birth: {document['Place of Birth']}")
        st.write(f"Height (Feet): {document['Height (Feet)']}")
        st.write(f"Height (Meter): {document['Height (Meter)']}")
        st.write(f"Body Type: {document['Body Type']}")
        st.write(f"Color: {document['Color']}")
        st.write(f"Manglik Dosh: {document['Manglik Dosh']}")
        st.write(f"Education: {document['Education']}")
        st.write(f"Job/Work/Occupation: {document['Job/Work/Occupation']}")
        st.write(f"Income: {document['Income']}")
        st.write(f"Agriculture: {document['Agriculture']}")
        st.write(f"Other Income Sources: {document['Other Income Sources']}")
        st.write(f"Diet: {document['Diet']}")
        st.write(f"Siblings: {document['Siblings']}")
        st.write(f"Permanent Address: {document['Permanent Address']}")
        st.write(f"Current Address: {document['Current Address']}")
        st.write(f"Contact No.: {document['Contact No.']}")
        st.write(f"Mail: {document['Mail']}")
        st.write(f"Postrer's Name: {document['Postrer Name']}")



        st.write(f"Additional Comments: {document['Additional Comments']}")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Post", "Search page"])

    if page == "Post":
        post_page()
    elif page == "Search page":
        search_page()

# Call the main function to run the Streamlit app
if __name__ == "__main__":
    main()

# Add your credit message at the bottom of the application
st.markdown("---")
st.write("Developed by Yash Mahesh Rawal 'जय हत्केश'")
