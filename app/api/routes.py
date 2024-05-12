from flask import request, jsonify
from app.db.mongo import *
from app.db.authentication import *
from app.features.otp_generate import *
from werkzeug.utils import secure_filename
import os
from app.features.location import *
from app.features.sms import *
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.crypto.prediction import *

def setup_routes(app):
    # Set the folder where uploaded files will be stored
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    # os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    @app.route('/register', methods=['POST'])
    def register():
        # Extract data from the request
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        mobile = data.get('mobile')
        role = data.get('role')
        dob = data.get('dob')
        gender = data.get('gender')
        category = data.get('category')
        specialization = data.get('specialization','')
        fees = data.get('fees',0)
        experience = data.get('experience',0)
        

        print(data)
        print(email, password, name, mobile, role,dob,gender,category,specialization,fees,experience)
        # Check if all required fields are present
        # if not (email and password and name and mobile and role):
        #     return jsonify({'data': 'Missing required fields'}), 400


        success,user_id = reg_auth(email, password, name, mobile, role,dob,gender,category,specialization,fees,experience)

        # Check if registration/authentication was successful
        if success:
            return jsonify({'data': 'Registration successful', 'user_id': str(user_id)}), 200
        else:
            return jsonify({'data': 'Registration failed'}), 500
    @app.route('/update-data', methods=['POST'])
    def updatedata():
        data = request.get_json()
        payload = data.get('data')
        user_id = data.get('id')

       

        try:
            # Assume loginotpcheck fetches the user and checks the password
            result=update_data(user_id,payload)
            if result:
                # This is just a simple implementation, password checking logic should be added
                return jsonify({'data': 'Successfully updated'}), 200
            else:
                return jsonify({'data': 'Failed to Update'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    @app.route('/delete-data', methods=['POST'])
    def deletedata():
        data = request.get_json()
     
        user_id = data.get('id')

       

        try:
            # Assume loginotpcheck fetches the user and checks the password
            result=delete_data_by_id(user_id)
            if result:
                # This is just a simple implementation, password checking logic should be added
                return jsonify({'data': 'Successfully deleted'}), 200
            else:
                return jsonify({'data': 'Failed to delete'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    @app.route('/appointments-today-total', methods=['GET'])
    def appointmentsTodayTotal():
      

        try:
          return jsonify(count_todays_appointments()), 200
           
        except Exception as e:
            return jsonify({'data': str(e)}), 500

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'data': 'Missing email or password'}), 400

        try:
            # Assume loginotpcheck fetches the user and checks the password
            result, user_id, role = login_auth(email,password)
            print(result, user_id, role)
            if result:
                # This is just a simple implementation, password checking logic should be added
                return jsonify({'data': 'Login successful', 'user_id': user_id, 'role':role}), 200
            else:
                return jsonify({'data': 'Invalid login credentials'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/send-otp', methods=['POST'])
    def send_otp():
        email = request.json.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        otp = generate_otp()
        try:
            send_mail(email, f'Your OTP for HelpDroid is: {otp}')
            return jsonify({'success': True, 'message': 'OTP sent successfully','recived_otp': otp}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    @app.route('/forgot-password', methods=['POST'])
    def forgot_password():
        email = request.json.get('email')
        password = request.json.get('password')
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400       
        try:
            update(email,password)
            print(email,password)
            return jsonify({'success': True, 'message': 'Password successfully'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    @app.route('/upload-prescription', methods=['POST'])
    def upload_prescription():
        email = request.form['email']  # Access email sent from the form
        file = request.files['file']  # Access the file sent from the form
        print(email, file)
        
        if not email or not file:
            return jsonify({'data': 'Missing required fields'}), 400
        
        if file and email:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(save_path)
            file.save(save_path)  # Save file to the uploads folder

        try:
            # Get the size of the file in kilobytes (KB)
            file_size_kb = os.path.getsize(save_path) / 1024

            # Check if the file size is less than or equal to 300 KB
            if file_size_kb > 300:
                os.remove(save_path)  # Clean up the temporary file
                return jsonify({'data': 'Choose a file within 300 KB'}), 400

            # If file size is acceptable, proceed with encryption and updating the database
           
            append_encrypted_image_to_prescription(save_path, email)

            os.remove(save_path)  # Clean up the temporary file
            return jsonify({'data': 'Prescription uploaded successfully'}), 200

        except Exception as e:
            os.remove(save_path)  # Ensure to clean up the temporary file in case of an error
            return jsonify({'data': str(e)}), 500
    

    @app.route('/get-prescription', methods=['POST'])
    def get_prescription():
        email = request.json.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400

        try:
            data = fetch_and_decrypt_prescription_images(email)
            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/delete-prescription', methods=['POST'])
    def delete_prescription():
        email = request.json.get('email')
        index = request.json.get('index')

        if not email or index is None:
            return jsonify({'data': 'Missing required fields'}), 400

        try:
            result = delete_prescription_image(email, index)
            if result:
                return jsonify({'data': 'Prescription image deleted successfully'}), 200
            else:
                return jsonify({'data': 'Failed to delete prescription image'}), 400
        except Exception as e:
            return jsonify({'data': str(e)}), 500


    @app.route('/upload-medication', methods=['POST'])
    def upload_medication():
        data=request.get_json()
        email=data.get('email')
        days=data.get('days')
        time=data.get('time')
        medicine=data.get('medication')
        print(data)
        if not all([email,days,time,medicine]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=insert_medication(email,days,time,medicine)
            if success:
                return jsonify({'data': 'Medication uploaded successfully'}), 200
            else:
                return jsonify({'data': 'Medication upload failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/get-medication', methods=['POST'])
    def get_medication():
        email=request.json.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            data=get_medications_details(email)
            print(data)
            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/remove-medication', methods=['POST'])
    def remove_medication():
        print(request.json)
        email=request.json.get('email')
        medication=request.json.get('medication')
        if not all([email,medication]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=delete_medication(email,medication)
            if success:
                return jsonify({'data': 'Medication deleted successfully'}), 200
            else:
                return jsonify({'data': 'Medication delete failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/edit-medication', methods=['POST'])
    def edit_medication():
        print(request.json)
        email=request.json.get('email')
        medication=request.json.get('medication')
        days=request.json.get('days')
        time=request.json.get('time')
        if not all([email,medication,days,time]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=update_medication(email,medication,days,time)
            if success:
                return jsonify({'data': 'Medication updated successfully'}), 200
            else:
                return jsonify({'data': 'Medication update failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/user-statistics', methods=['POST'])
    def user_statistics():
        email = request.json.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400

        try:
            prescription_count, medicine_count, chat_count,health_details = get_user_statistics(email)
            return jsonify({'prescription_count': prescription_count, 'medicine_count': medicine_count, 'chat_count': chat_count,'health_details':health_details}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/doc-statistics', methods=['POST'])
    def doc_statistics():
        email = request.json.get('email')
        print(email)
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400

        try:
            print("inside try")
            appiontment_count, chat_count , seven= get_doc_statistics(email)
            print(appiontment_count, chat_count,seven)
            return jsonify({'appiontment_count': appiontment_count, 'chat_count': chat_count,'seven':seven}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/upload-contacts', methods=['POST'])
    def upload_contacts():
        data=request.get_json()
        email=data.get('email')
        email1=data.get('email1')
        pname=data.get('name')
        mobile=data.get('mobile')
        print(data)
        if not all([email,email1,pname,mobile]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=insert_contact(email,email1,pname,mobile)
            if success:
                return jsonify({'data': 'Contact uploaded successfully'}), 200
            else:
                return jsonify({'data': 'Contact upload failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/get-contacts', methods=['POST'])
    def get_contacts():
        email=request.json.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            data=fetch_contacts(email)
            print(data)
            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500

    @app.route('/edit-contacts', methods=['POST'])
    def edit_contacts():
        data=request.get_json()
        email=data.get('email')
        email1=data.get('email1')
        pname=data.get('name')
        mobile=data.get('mobile')
        print(data)
        if not all([email,email1,pname,mobile]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=update_contact(email,email1,pname,mobile)
            if success:
                return jsonify({'data': 'Contact updated successfully'}), 200
            else:
                return jsonify({'data': 'Contact update failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500

    @app.route('/get-doctors', methods=['POST'])
    def get_doctors():
        data = request.get_json()
        role_raw = data.get("role")

        # Convert role to boolean
        # Any non-empty string other than "false" (case insensitive) will be True
        role = str(role_raw).lower() == "true"
        print(role,"role")
        #  email = data.get('email')
        try:
            # Assume `fetch_all_doctors` is a function that retrieves all doctors from your database
            
            doctors = find_by_role_true(role) 
            print("doc",doctors)
            return jsonify({'doctors': doctors}), 200
           

                
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @app.route('/remove-contacts', methods=['POST'])
    def remove_contacts():
        data=request.get_json()
        email=data.get('email')
        pname=data.get('name')
        print(data)

        if not all([email,pname]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=delete_contact(email,pname)
            if success:
                return jsonify({'data': 'Contact deleted successfully'}), 200
            else:
                return jsonify({'data': 'Contact delete failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
            
    @app.route('/get-messages', methods=['POST'])
    def get_messages():
        data=request.get_json()
        sender_id=data.get('sender_id')
        receiver_id=data.get('receiver_id')
        print(data)

        if not all([sender_id,receiver_id]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=fetch_messages(receiver_id,sender_id)
            return jsonify({'data': success}), 200
          
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    @app.route('/save-messages', methods=['POST'])
    def save_messages():
        data=request.get_json()
        sender_id=data.get('sender_id')
        receiver_id=data.get('receiver_id')
        text =data.get('text')
        print(data)

        if not all([sender_id,receiver_id]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            append_message(receiver_id,text,sender_id)
            return jsonify({'data': "Successfully added"}), 200
          
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    @app.route('/graph-admin', methods=['GET'])
    def graph_admin():
        try:
            
            return jsonify(retrieve_stats()), 200
          
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    socketio = SocketIO(app, cors_allowed_origins="*")  

    @socketio.on('join')
    def on_join(data):
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        room = get_room(sender_id, receiver_id)
        join_room(room)
        print(f'{sender_id} has entered room: {room}')

    @socketio.on('connect')
    def handle_connect():
        # Assume user_id is stored in the session or passed as part of the connection handshake
        user_id = request.args.get('user_id')
        join_room(user_id)
        print(f'User {user_id} connected and joined their room')


    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('send_message')
    def handle_send_message(json):
        sender_id = json['sender_id']
        receiver_id = json['receiver_id']
        room = get_room(sender_id, receiver_id)
        emit('receive_message', json, room=room)
        append_message(receiver_id,json['text'],sender_id)
      
    @socketio.on('leave')
    def on_leave(data):
        room = get_room(data['sender_id'], data['receiver_id'])
        room = get_room(data['sender_id'], data['receiver_id'])
        leave_room(room)
        print(f'{data["sender_id"]} left room: {room}')

    def get_room(user1, user2):
        return '-'.join(sorted([user1, user2]))


        
    @app.route('/emergency', methods=['POST'])
    def emergency():
        data=request.get_json()
        email=data.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400
        
        try:     
            details= user_details(email)
            for contact in details.get("contacts", []):
                response=get_location('223.191.62.144')
                message="Your closed one have severe health issues please check .\nUser Details:\n Name:"+(details.get("name"))+"\n Mobile "+(details.get("mobile"))+"\n Email:"+(details.get("email"))+ "\nLocation: "+"\nCountry: "+response.get("country_name")+"\nState: "+response.get("region")+"\nCity: "+response.get("city")+"\nLatitude: "+str(response.get("latitude"))+"\nLongitude: "+str(response.get("longitude"))    
                if contact.get("email"):
                    print(contact.get("email"))
                    #print(message)
                    send_mail(contact.get("email"),message,"Emergency from HelpDroid")
                    
                if contact.get("mobile"):
                    print(contact.get("mobile"))
                    send_sms(contact.get("mobile"),message)
            return jsonify({'data': 'Emergency Mail sent successfully'}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/notify', methods=['POST'])
    def notify():
        data=request.get_json()
        email=data.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400
        
        try:     
            send_notification(email)
            return jsonify({'data': 'Notification sent successfully'}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/upload-appointment', methods=['POST'])
    def upload_appointment():
        data=request.get_json()
        email=data.get('email')
        pname=data.get('appointment')
        time=data.get('time')
        date=data.get('date')
        
        print(data)
        if not all([email,pname,time,date]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=insert_appointment(email,pname,time,date)
            if success:
                return jsonify({'data': 'Appointment uploaded successfully'}), 200
            else:
                return jsonify({'data': 'Appointment upload failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/get-appointments', methods=['POST'])
    def get_appointments():
        email=request.json.get('email')
        if not email:
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            data=get_appointment_details(email)
            print(data)
            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/remove-appointment', methods=['POST'])
    def remove_appointment():
        print(request.json)
        email=request.json.get('email')
        pname=request.json.get('appointment')
        if not all([email,pname]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=delete_appointment(email,pname)
            if success:
                return jsonify({'data': 'Appointment deleted successfully'}), 200
            else:
                return jsonify({'data': 'Appointment delete failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    @app.route('/edit-appointment', methods=['POST'])
    def edit_appointment():
        print(request.json)
        email=request.json.get('email')
        pname=request.json.get('appointment')
        time=request.json.get('time')
        date=request.json.get('date')
        if not all([email,pname,time,date]):
            return jsonify({'data': 'Missing required fields'}), 400
        try:
            success=update_appointment(email,pname,time,date)
            if success:
                return jsonify({'data': 'Appointment updated successfully'}), 200
            else:
                return jsonify({'data': 'Appointment update failed'}), 401
        except Exception as e:
            return jsonify({'data': str(e)}), 500
    
    @app.route('/send-sms', methods=['POST'])
    def send_message():
        email = request.json.get('email')
      
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400       
        try:
           
            return jsonify({'success': True, 'message': 'Sent successfully'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/doctor-details',methods=['POST'])
    def doctor_details():
        print(request.json)
        data=request.get_json()
        email=data.get('email')
        specializations= data.get('specializations') 
        yearsOfExperience = data.get('yearsOfExperience')
        fees=data.get('fees')
        addresses=data.get('addresses')
        
        if not all([email,specializations,yearsOfExperience,fees,addresses]):
            return jsonify({'data': 'Missing required fields'}), 400
        
        try:
            details=doc_details(email,specializations,yearsOfExperience,fees,addresses)
            return jsonify({'data': details}), 200
        except Exception as e:
            return jsonify({'data': str(e)}), 500
        
    def health(email,spo2,pulse,temp,date):
        data=request.get_json()
        email=data.get('email')
        date=data.get('date')
        
        if not email or not spo2 or not pulse or not temp:
            return jsonify({'data': 'Missing required fields'}), 400
        
        try:
            success=insert_health(email,spo2,pulse,temp,date)
            if success:
                return True
            else:
                return False
            
        except Exception as e:
            return False

    @app.route('/check-score',methods=['POST'])
    def check_score():
        print(request.json)
        email=request.json.get('email')
        date=request.json.get('date')
        try:
            score,data=hybrid_score()
            print(score)
            success=health(email,data[5],data[1],data[0],date)
            if success:
                print(score)
                if(score == 0):
                    txt="Normal" 
                    msg="Your health is normal. Stay healthy and happy."           
                elif(score==1):
                    txt="Mild"
                    msg="Your health is mild. Please take care of yourself."
                elif(score == 2):
                    txt="Moderate"
                    msg="Your health is moderate. Please consult a doctor."
                else:
                    txt="Severe"
                    msg="Your health is severe. Please consult a doctor immediately. Your Emergency contacts have been notified."
                    details= user_details(email)
                    for contact in details.get("contacts", []):
                        response=get_location('223.191.62.144')
                        message="Your closed one have severe health issues please check .\nUser Details:\n Name:"+(details.get("name"))+"\n Mobile "+(details.get("mobile"))+"\n Email:"+(details.get("email"))+ "\nLocation: "+"\nCountry: "+response.get("country_name")+"\nState: "+response.get("region")+"\nCity: "+response.get("city")+"\nLatitude: "+str(response.get("latitude"))+"\nLongitude: "+str(response.get("longitude"))    
                        if contact.get("email"):
                            print(contact.get("email"))
                            #print(message)
                            send_mail(contact.get("email"),message,"Emergency from HelpDroid")
                            
                        if contact.get("mobile"):
                            print(contact.get("mobile"))
                            send_sms(contact.get("mobile"),message)
                
                return jsonify({'condition': txt, 'msg': msg, 'spo2': data[5], 'pulse': data[1], 'temperature': data[0]}), 200
            
        except Exception as e:
            return jsonify({'data': str(e)}), 500

               