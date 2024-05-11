from app.db.mongo import *
from app.crypto.sha256 import *

def reg_auth(email_input, password_input, name_input, mobile_input, role,dob,gender,category,specialization,fees,experience):
    inserted_id = insert_data(email_input, password_input, mobile_input, name_input, role,dob,gender,category,specialization,fees,experience)
    print(inserted_id)
    if inserted_id:
        return True, inserted_id  # Return the ObjectId as the second part of the tuple
    else:
        return False, None
    
def login_auth(email_input, password_input=None):
    # If a password is provided, hash it together with the email to check for a match.
    if password_input is not None:
        hash = sha256(password_input + "" + email_input)
        matching_documents = find({"email": email_input, "password": hash})
    else:
        matching_documents = find({"email": email_input})

    for document in matching_documents:
        print(document)
        role=(document['role'])
        id=str(document['_id'])
        if(role):
            return "Doctor",id,role
        else:
            return "Patient",id,role

    return None,None

