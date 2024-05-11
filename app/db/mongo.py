import pymongo
import app.crypto.sha256 as sha256
import os
import json
import tempfile
from app.crypto.triple_des import decrypted, encrypted
from app.features.notification import *
from datetime import datetime,timezone,timedelta
from bson.objectid import ObjectId
import base64
from pymongo import ReturnDocument



# Replace with your MongoDB connection string
mongo_uri = 'mongodb+srv://sonadas8april:riyadasdas@cluster0.x0jnn5h.mongodb.net/'

# Create a MongoClient
client = pymongo.MongoClient(mongo_uri)

# Replace with your database name
db = client['HelpDroid']

# Replace with your collection name
collection = db['User']
collection2 = db['user_registered']

# Insert a document into the collection

def insert_data(email,password,mobile,name,role,dob,gender,category,specialization,fees,experience):
    # data = {'email': email, 'password': password,'mobile':mobile, 'name': name}
    # collection.insert_one(data)
    try:        
        hash = sha256.sha256(password+""+email)        
        data = {'email': email, 'password': hash,'mobile':mobile, 'name': name, 'role':role,'dob':dob,'gender':gender,'category':category}
        if role:
            data.update({
                'specialization': specialization,
                'fees': fees,
                'experience': experience
            })
        print(data)
        id=collection.insert_one(data)
        print("Inserted")
        if(id.inserted_id):
            update_registration_stats(role)
        print(id)
        return id.inserted_id
    except Exception as e:
        print(f"Error:  (An error occurred)",e)
def update_data(user_id, updates):
    try:
        # Prepare the update document
        update_doc = {'$set': updates}
        print("user_id",user_id)
        # Perform the update operation
        result = collection.update_one({'_id': ObjectId(user_id)}, update_doc)
        
        # Check if the document was successfully updated
        if result.matched_count > 0:
            print(f"Successfully updated document: {user_id}")
            if result.modified_count > 0:
                print(f"Modified fields: {updates}")
            else:
                print("No fields were modified (submitted values may be the same as existing values).")
        else:
            print("No document matches the provided ID.")
        
        return result.matched_count > 0  # Returns True if the update was successful, False otherwise
    except Exception as e:
        print(f"Error updating document: {e}")
        return False
def delete_data_by_id(document_id):
    try:
        # Convert string ID to ObjectId for MongoDB
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)

        # Perform the delete operation
        result = collection.delete_one({'_id': document_id})

        # Check if the document was successfully deleted
        if result.deleted_count > 0:
            print("Document successfully deleted.")
            return True
        else:
            print("No document found with that ID.")
            return False
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False
def count_todays_appointments():

    today = datetime.now()
    start_of_today = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_of_today = datetime(today.year, today.month, today.day, 23, 59, 59)
    
    # MongoDB aggregation to unwind the appointments array and match appointments by today's date
    pipeline = [
        {'$unwind': '$appointment'},  # Unwind the appointments array to process each appointment
        {'$match': {
            'appointment.date': {
                '$gte': start_of_today,
                '$lte': end_of_today
            }
        }},
        {'$count': 'total_appointments_for_today'}  # Count the total appointments for today
    ]
    
    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))
    
    # Handle the case where no appointments are found for today
    if result:
        return result[0]['total_appointments_for_today']
    else:
        return 0

def update_registration_stats(role):
    today_date = datetime.now().date().isoformat() 
    if role:
        increment_field = 'doctor'
        ensure_field = 'patient'
    else:
        increment_field = 'patient'
        ensure_field = 'doctor'

    # Update the stats document for today's date
    update_result = collection2.update_one(
        {'date': today_date},
        {
            '$inc': {increment_field: 1},  # Increment the count for the active role
            '$setOnInsert': {ensure_field: 0}  # Ensure the other field exists but only on insert
        },
        upsert=True  # Create a new document if one doesn't exist for today's date
        )
    
    if update_result.matched_count == 0:
        print("A new stats document was created for today.")
    elif update_result.modified_count > 0:
        print("Stats document updated for today.")
    # query = {'email': "Jlhn@john"}
def retrieve_stats():
    # Calculate the start date (7 days ago) and the end date (today)
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        # Query to find all entries within the date range, inclusive
        query = {
            'date': {
                '$gte': start_date.isoformat(),  # Greater than or equal to start_date
                '$lte': end_date.isoformat()     # Less than or equal to end_date
            }
        }

        # Perform the query and return the result
        results = collection2.find(query)
        
        # Format the results as specified: [{"x": "date", "y": "doctor"}, {"x": "date", "y": "patient"}]
        formatted_results = []
        formatted_results.append([])
        formatted_results.append([])
        for result in results:
            formatted_results[0].append({"x": result['date'], "y": result.get('doctor', 0)})
            formatted_results[1].append({"x": result['date'], "y": result.get('patient', 0)})

        return formatted_results
    except Exception as e:
        print(e)
        return []
def update(email_input,new_pass):
    filter_criteria = {"email": email_input}

    # Define the update operation (e.g., set a new value for a field)
    new_pass = sha256.sha256(new_pass+""+email_input)
    update_operation = {"$set": {"password": new_pass}}

    # Update the document in the collection
    collection.update_one(filter_criteria, update_operation)

    
def find(query):
   matching_documents = collection.find(query)
   return matching_documents
   
       
# def loginotpcheck(email_input):
#     query = {'email': email_input}
#     matching_documents = collection.find(query)
#     for document in matching_documents:
#         print("Login Successful")
#         role=(document['role'])
#         id=str(document['_id'])
#         if(role):
#             return "Doctor",id
#         else:
#             return "Patient",id

#     return None,None


def append_encrypted_image_to_prescription(path,email):
    # Encrypt the image data
    
    email = email
    encrypted_image = encrypted(path)

    result = collection.update_one(
        {"email": email},
        {"$push": {"prescription_images": encrypted_image}}
    )

    # Check if the update was successful
    if result.modified_count > 0:
        print(f"Image appended to prescription for {email}")
    else:
        print(f"No document found with email {email} or no update was needed.")

                
def fetch_and_decrypt_prescription_images(email):
    # Fetch the document for the given email
    document = collection.find_one({"email": email})

    # Check if the document was found
    if document:
        encrypted_images = document.get("prescription_images", [])

        decrypted_images = []
        for encrypted_image in encrypted_images:
            image_bytes = decrypted(encrypted_image)  # This function should decrypt the image
            base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
            decrypted_images.append(base64_encoded)


        return decrypted_images
    
    
    else:
        print(f"No document found with email {email}")
        return []
    
def delete_prescription_image(email, index):
    document = collection.find_one({"email": email})

    if document:
        encrypted_images = document.get("prescription_images", [])

        if 0 <= index < len(encrypted_images):
            del encrypted_images[index]
            result = collection.update_one(
                {"email": email},
                {"$set": {"prescription_images": encrypted_images}}
            )
            if result.modified_count > 0:
                print(f"Prescription image deleted for {email}")
                return True
    return False
    
def insert_medication(email,days,med_time,med_name):
    if not email:
        print("No email found in session.")
        return

    med_data = {"name": med_name, "time": med_time, "days": days}
    print(med_data)
    try:
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$push": {"medication": med_data}},
            upsert=False
        )
        
        if update_result.modified_count > 0:
            print("medication inserted successfully.")
            datetime_obj = datetime.fromisoformat(med_time)
            time_formatted = datetime_obj.strftime('%H:%M')
            print(time_formatted)
            schedule_medication_notification(med_name, time_formatted, days)
            return True
        else:
            print("No update was made.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    

def get_medications_details(email):
    # Replace with your collection name
    user_data = collection.find_one({"email": email})
    if user_data and "medication" in user_data:
        return user_data["medication"]
    return []
def delete_medication(email,med_name):
    if not email:
        print("No email found in session.")
        return

    if med_name is None :
        return

    med_data = {"name": med_name}

    try:
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$pull": {"medication": med_data}},
            upsert=False
        )
        
        
        if update_result.modified_count > 0:
            print("medication deleted successfully.")
            return True
        else:
            print("delete was not made, possibly because the medication does not exist.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def update_medication(email, med_name, days, med_time):
    if not email:
        print("No email found in session.")
        return

    if not med_name:
        print("No medication name provided.")
        return

    try:
        # Update the existing user document to update the medication
        update_result = collection.update_one(
            {"email": email, "medication.name": med_name},
            {"$set": {"medication.$.days": days, "medication.$.time": med_time}},
            upsert=False
        )

        if update_result.modified_count > 0:
            print("Medication updated successfully.")
            datetime_obj = datetime.fromisoformat(med_time)
            time_formatted = datetime_obj.strftime('%H:%M')
            print(time_formatted)
            schedule_medication_notification(med_name, time_formatted, days)
            # You may want to call a function here to update the medication schedule notification
            return True
        else:
            print("No update was made. Possibly because the medication name was not found.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    

def get_user_statistics(email):
    # Initialize counters
    prescription_count = 0
    medicine_count = 0
    unique_receiver_ids = set()
    health_counts_last_seven_days=[]

    try:
        # Retrieve the user document by email
        user_document = collection.find_one({"email": email})

        # Check if the document was found
        if user_document:
            # Count the number of prescriptions
            if "prescription_images" in user_document:
                prescription_count = len(user_document["prescription_images"])

            # Count the number of medicines
            if "medication" in user_document:
                medicine_count = len(user_document["medication"])

            try:
                    # Calculate the date 7 days ago
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                # Convert date strings in appointments to datetime objects and delete appointments older than 7 days
                result = collection.update_one(
                    {"email": email},
                    {"$pull": {"health": {"date": {"$lt": seven_days_ago.isoformat()}}}}
                )
                
                if result.modified_count > 0:
                    print("Old health deleted successfully.")
                else:
                    print("No health were deleted.")
                
            except Exception as e:
                print(f"An error occurred while deleting health: {e}")
            # Count the number of unique receiver IDs for chats
            if "messages" in user_document:
                # Iterate over each message group
                for message_group in user_document["messages"]:
                    # Extract unique receiver IDs from the messages
                    unique_receiver_ids.update([message_group["receiver_id"]])

        # Calculate dates for the last 7 days
        last_seven_days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        # Construct the object containing appointment counts for the last 7 days
        # Construct the object containing appointment counts for the last 7 days
        for day in last_seven_days:
            # Find the corresponding record in the database for the current day
            record = next((item for item in user_document['health'] if item['date'] == day), None)
            
            # If a record is found for the current day, extract the required information
            if record:
                health_counts_last_seven_days.append({
                    "date": record["date"],
                    "spo2": record.get("spo2", None),
                    "pulse": record.get("pulse", None),
                    "temp": record.get("temp", None)
                })
            else:
                # If no record is found for the current day, add None values
                health_counts_last_seven_days.append({
                    "date": day,
                    "spo2": None,
                    "pulse": None,
                    "temp": None
                })



        # Return the counts
        return prescription_count, medicine_count, len(unique_receiver_ids),health_counts_last_seven_days

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0, 0, 0 ,[] # Return zeros in case of any error 

def get_doc_statistics(email):
    # Initialize counters
    appointment_count = 0
    unique_receiver_ids = set()
    appointment_dates_count = {}

    try:
        # Retrieve the user document by email
        user_document = collection.find_one({"email": email})

        # Check if the document was found
        if user_document:
            # Count the number of appointments
            current_date = datetime.now().strftime("%Y-%m-%d")

            for appointment in user_document.get("appointment", []):
                appointment_date = appointment.get("date", "").split("T")[0]
                if appointment_date == current_date:
                    appointment_count += 1

                # Count appointments for each date for the last 7 days
                if appointment_date in appointment_dates_count:
                    appointment_dates_count[appointment_date] += 1
                else:
                    appointment_dates_count[appointment_date] = 1

                try:
                     # Calculate the date 7 days ago
                    seven_days_ago = datetime.now() - timedelta(days=7)
                    
                    # Convert date strings in appointments to datetime objects and delete appointments older than 7 days
                    result = collection.update_one(
                        {"email": email},
                        {"$pull": {"appointment": {"date": {"$lt": seven_days_ago.isoformat()}}}}
                    )
                    
                    if result.modified_count > 0:
                        print("Old appointments deleted successfully.")
                    else:
                        print("No appointments were deleted.")
                
                except Exception as e:
                    print(f"An error occurred while deleting appointments: {e}")

            # Count the number of unique receiver IDs for chats
            if "messages" in user_document:
                # Iterate over each message group
                for message_group in user_document["messages"]:
                    # Extract unique receiver IDs from the messages
                    unique_receiver_ids.update([message_group["receiver_id"]])

        # Calculate dates for the last 7 days
        last_seven_days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        # Construct the object containing appointment counts for the last 7 days
        # Construct the object containing appointment counts for the last 7 days
        appointment_counts_last_seven_days = [{"date": date, "count": appointment_dates_count.get(date, 0)} for date in last_seven_days]


        return appointment_count, len(unique_receiver_ids), appointment_counts_last_seven_days

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0, 0, {}  
        
def insert_contact(email,email1=None, name='user', mobile=None):
    
    if not email:
        print("No email found in session.")
        return
    
    if email1 is None:
        return
    if mobile is None:
        return
    
    contact_data = {"name": name, "email": email1, "mobile": mobile}
    print(contact_data)
    try:
        print(contact_data)
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$push": {"contacts": contact_data}},
            upsert=False
        )
        if update_result.matched_count == 0:
            print("No user found with the provided email.")
            return False
        elif update_result.modified_count > 0:
            print("Contact inserted successfully.")
            return True
        else:
            print("No update was made, possibly because the contact already exists.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def fetch_contacts(email):
    if not email:
        print("No email found in session.")
        return

    try:
        # Fetch the user document
        user_document = collection.find_one({"email": email})

        # Check if the document was found
        if user_document:
            contacts = user_document.get("contacts", [])
            print(contacts)
            return contacts
        else:
            print(f"No document found with email {email}")
            return []

    except Exception as e:
        print(f"Error: {e}")
        return []

def delete_contact(email, name):
    if not email:
        print("No email found in session.")
        return

    if name is None:
        print("Name must be provided.")
        return

    contact_data = {"name": name}

    try:
        # Print debug information
        print("Deleting contact with email:", email)
        print("Contact data:", contact_data)

        # Perform deletion operation
        result = collection.find_one_and_update(
            {"email": email},
            {"$pull": {"contacts": contact_data}},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            print("Contact deleted successfully.")
            return True
        else:
            print("No update was made, possibly because the contact does not exist.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def update_contact(email, new_email, name, new_mobile):
    if not email:
        print("No email found in session.")
        return False

    if new_email is None or new_mobile is None:
        print("Both new_email and new_mobile must be provided.")
        return False

    contact_data = {"contacts.$.email": new_email, "contacts.$.mobile": new_mobile}

    try:
        # Print debug information
        print("Updating contact with email:", email)
        print("New email:", new_email)
        print("New name:", name)
        print("New mobile:", new_mobile)

        # Update the existing user document to update the contact
        result = collection.find_one_and_update(
            {"email": email, "contacts.name": name},
            {"$set": contact_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            print("Contact updated successfully.")
            return True
        else:
            print("No update was made, possibly because the contact does not exist.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

    
def user_details(email):
    
    if not email:
        print("No email found in session.")
        return

    try:
        # Fetch the user document
        user_document = collection.find_one({"email": email})

        # Check if the document was found
        if user_document:
            return user_document
        else:
            print(f"No document found with email {email}")
            return []

    except Exception as e:
        print(f"Error: {e}")
        return []


def insert_appointment(email,p_name,a_time,a_date):
    
    if not email:
        print("No email found in session.")
        return

    if p_name is None or a_time is None or a_date is None:
        return

    a_data = {"name": p_name, "time": a_time, "date": a_date}

    try:
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$push": {"appointment": a_data}},
            upsert=False
        )
        
        
        if update_result.modified_count > 0:
            print("appointment inserted successfully.")
            time_obj = datetime.fromisoformat(a_time)
            time_formatted = time_obj.strftime('%H:%M')
            print(time_formatted)
            date_obj = datetime.fromisoformat(a_date)
            date_formatted = date_obj.strftime('%Y-%m-%d')
            
            print(time_formatted, date_formatted)
            schedule_appointment_notification(p_name, time_formatted, date_formatted)
            return True
        else:
            print("No update was made, possibly because the contact already exists.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def update_appointment(email, p_name, a_time, a_date):
    if not email:
        print("No email found in session.")
        return

    if p_name is None or a_time is None or a_date is None:
        return

    a_data = {"name": p_name, "time": a_time, "date": a_date}

    try:
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email, "appointment.name": p_name},
            {"$set": {"appointment.$": a_data}},
            upsert=False
        )
        
        
        if update_result.modified_count > 0:
            print("appointment updated successfully.")
            time_obj = datetime.fromisoformat(a_time)
            time_formatted = time_obj.strftime('%H:%M')
            print(time_formatted)
            date_obj = datetime.fromisoformat(a_date)
            date_formatted = date_obj.strftime('%Y-%m-%d')
            
            print(time_formatted, date_formatted)
            schedule_appointment_notification(p_name, time_formatted, date_formatted)
            return True
        else:
            print("No update was made, possibly because the contact already exists.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    

def get_appointment_details(email):
    
    # Ensure your MongoDB connection/collection is correctly set up here
    user_data = collection.find_one({"email": email})
    try:
        if user_data and "appointment" in user_data:
            # Get current local system time
            current_time = datetime.now()
            print("Current Time :", current_time)
            updated_appointments = []
            print("All appointments:", user_data["appointment"])
            for appointment in user_data["appointment"]:
                print("Original appointment:", appointment)
                # Combine date and time into a datetime object for local time
                print("Appointment Time:", appointment["time"])
                print("Appointment Date:", appointment["date"])
                appointment_date_time = datetime.fromisoformat(appointment["date"][:-6])  # Parse appointment date
                print("Appointment Date Time:", appointment_date_time)
                appointment_time = datetime.fromisoformat(appointment["time"][:-6]).time()  # Parse appointment time
                print("Appointment Time:", appointment_time)
                appointment_sch = datetime.combine(appointment_date_time.date(), appointment_time)  # Combine date and time
                print("Appointment Schedule:", appointment_sch)
                
                                                    
                
                if appointment_sch >= current_time:
                    print("Appointment is in the future.")
                    updated_appointments.append(appointment)
            
            # # Update the database with the remaining (future) appointments
            # collection.update_one({"email": email}, {"$set": {"appointment": updated_appointments}})
            
            return updated_appointments
        return []
    except Exception as e:
        print(f"Error: {e}")

def delete_appointment(email,p_name):
    
    if not email:
        print("No email found in session.")
        return

    if p_name is None:
        return
    print("p_name",p_name)
    
    try:
       
        apt_data = {"name": p_name}
        print(apt_data)
            # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$pull": {"appointment": apt_data}},
            upsert=False
        )
        
        
        if update_result.modified_count > 0:
            print("appointment deleted successfully.")
            return True
        else:
            print("delete was not made, possibly because the appointment does not exist.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


    
def send_notification(email):
    try:
        print("Sending notifications for", email)
        med_timings = get_medications_details(email)
        apt_timings = get_appointment_details(email)
        for med_timing in med_timings:
            schedule_medication_notification(med_timing["name"], med_timing["time"], med_timing["days"])
        for apt_timing in apt_timings:
            schedule_appointment_notification(apt_timing["name"], apt_timing["time"], apt_timing["date"])
    except Exception as e:
        print("Error")


def find_by_role_true(user_role):
  
    
    print(user_role)
    # if not user_role :
    try:
        print("FALSE PATIENT")
        query = {"role": {"$exists": True, "$eq": not user_role}}
        matching_documents = collection.find(query)
        print(matching_documents)
            # Format the results as a list of dictionaries containing 'name' and '_id'
        results = [
                {
                    'id': str(doc['_id']),
                    'name': doc.get('name', ""),
                    'email': doc.get('email', ""),
                    'mobile': doc.get('mobile', ""),
                    'category': doc.get('category', ""),
                    'gender': doc.get('gender', ""),
                    'dob': doc.get('dob', ""),
                     **({  # Conditional addition of fields
                        'specialization': doc.get('specialization', ""),
                        'experience': doc.get('experience', ""),
                        'fees': doc.get('fees', "")
                    } if not user_role else {})
                    
                }
                for doc in matching_documents
            ]
        print("Results:", results)
        return results
    except Exception as e:
        print(e)
        return []
    # else:
    #     print("TRUE DOCTOR")
    #     email_doc = collection.find_one({"email": email})
    
        
        
        # Retrieve details for each receiver ID
#         receiver_ids = [item['receiver_id'] for item in email_doc['messages']]
#         print(receiver_ids)
#         receiver_details = []

#         for receiver_id in receiver_ids:
#             # Convert the string ID to ObjectId for querying
#             object_id = ObjectId(receiver_id)
#             receiver_doc = collection.find_one({"_id": object_id}, {"name": 1})
            
#             if receiver_doc:
#                 receiver_details.append({
#                     'name': receiver_doc['name'],
#                     'id': str(receiver_doc['_id'])
#                 })
#         print(receiver_details)
#         return receiver_details

        

def append_message(receiver_id, text,sender_id):
    receiver_id = ObjectId(receiver_id)
    timestamp = datetime.now()
    sender_id = ObjectId(sender_id)
    print(sender_id, receiver_id)
    # Message for the sender: marking as 'sent'
    sender_message = {'text': text, 'is_sent': True, 'timestamp': timestamp}
    # Message for the receiver: marking as 'received' (is_sent = False)
    receiver_message = {'text': text, 'is_sent': False, 'timestamp': timestamp}

    # Update sender's document
    sender_result = collection.update_one(
        {'_id': sender_id, 'messages.receiver_id': receiver_id},
        {'$push': {'messages.$.messages': sender_message}}
    )
    if sender_result.modified_count == 0:
        collection.update_one(
            {'_id': sender_id},
            {'$push': {'messages': {'receiver_id': receiver_id, 'messages': [sender_message]}}}
        )
        print("New receiver_id added for sender.")

    # Update receiver's document
    receiver_result = collection.update_one(
        {'_id': receiver_id, 'messages.receiver_id': sender_id},
        {'$push': {'messages.$.messages': receiver_message}}
    )
    if receiver_result.modified_count == 0:
        collection.update_one(
            {'_id': receiver_id},
            {'$push': {'messages': {'receiver_id': sender_id, 'messages': [receiver_message]}}}
        )
        print("New sender_id added for receiver.")

def fetch_messages( receiver_id, sender_id):
    
    try:
        # Convert receiver_id to ObjectId if it's stored as such in the database
        receiver_oid = ObjectId(receiver_id)
        sender_oid = ObjectId(sender_id)
        # Execute a query to fetch the messages directly
        user_doc = collection.find_one(
            {'_id': sender_oid, 'messages.receiver_id': receiver_oid},
            {'messages.$': 1}  # Project only the matching messages subdocument
        )

        if not user_doc or 'messages' not in user_doc:
            print("No messages found or no user found with that email.")
            return []

        # Return the first matching group of messages (since $elemMatch or $ projects the first match only)
        messages_list = user_doc['messages'][0]['messages']  # Extracting the nested 'messages' from the matched group
        return messages_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list or appropriate
    

def doc_details(email,specializations,yearsOfExperience,fees,addresses):
    
    if not email:
        print("No email found in session.")
        return

    if not specializations or not yearsOfExperience or not fees or not addresses:
        print("Missing required data.")
        return

    try:
        existing_user = collection.find_one({"email": email})
        if existing_user and "doctor_details" in existing_user:
            # Doctor details already exist, so we need to replace them
            update_result = collection.update_one(
                {"email": email},
                {
                    "$set": {
                       
                            "specialization": specializations,
                            "experience": yearsOfExperience,
                            "fees": fees,
                            "addresses": addresses
                        
                    }
                },
                upsert=False
            )
        else:
            # Doctor details don't exist, so insert them
            update_result = collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "doctor_details": {
                            "specializations": specializations,
                            "yearsOfExperience": yearsOfExperience,
                            "fees": fees,
                            "addresses": addresses
                        }
                    }
                },
                upsert=True
            )

        if update_result.modified_count > 0:
            print("Doctor details inserted/updated successfully.")
            return True
        else:
            print("No update was made.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def insert_health(email,spo2,pulse,temp,date):
    if not email:
        print("No email found in session.")
        return

    if not spo2 or not pulse or not temp or not date:
        print("Missing required data.")
        return
    
    health_data = {"spo2": spo2, "pulse": pulse, "temp": temp, "date": date}

    try:
        # Update the existing user document to add the contact
        update_result = collection.update_one(
            {"email": email},
            {"$push": {"health": health_data}},
            upsert=False
        )
        
        if update_result.modified_count > 0:
            print("Health data inserted successfully.")
            return True
        else:
            print("No update was made.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    

    