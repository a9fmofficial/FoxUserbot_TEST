import asyncio
import logging
import threading
import time
import shutil
import subprocess
import os

from typing import Optional, Tuple

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from pyrogram import Client
from pyrogram.errors import RPCError, SessionPasswordNeeded
from pyrogram.types import User, TermsOfService


app = Flask(__name__)
code_input = None
auth_complete = False
auth_result = None
current_step = "phone"
current_phone = "+7"


user_data = {'phone': None, 'code': None, 'password': None}


HTML_TEMPLATE = open('web_auth/site.html', 'r', encoding='utf-8').read()


@app.route('/', methods=['GET', 'POST'])
def auth_web():
    global code_input, auth_complete, current_step, current_phone
    
    if request.method == 'POST':
        if 'phone' in request.form:
            current_phone = request.form['phone']
            current_step = 'code'
            return redirect(url_for('auth_web', step='code', phone=current_phone))
            
        elif 'code' in request.form:
            code_input = request.form['code']
            auth_complete = True
            current_step = 'code'  
            return redirect(url_for('auth_web', step='code', phone=current_phone))
            
        elif 'password' in request.form:
            code_input = request.form['password']
            auth_complete = True
            current_step = 'success'
            return redirect(url_for('auth_web', step='success'))
    
    step = request.args.get('step', current_step)
    phone = request.args.get('phone', current_phone)
    error = request.args.get('error', '')
    
    if step == 'password':
        current_step = 'password'
        current_phone = phone
    
    return render_template_string(HTML_TEMPLATE, step=step, phone=phone, error=error)

@app.route('/check_step', methods=['GET'])
def check_step():
    global current_step
    return {'step': current_step}

@app.route('/submit_code', methods=['POST'])
def submit_code():
    global current_step, user_data
    code = request.form.get('code')
    phone = request.args.get('phone')
    if not code or not phone:
        return jsonify({'error': 'Missing code or phone number'}), 400
    
    user_data['code'] = code if code else ''
    user_data['phone'] = phone if phone else ''
    
    try:
        success, user = sign_in_with_code(phone, code)
        if success and user:
            current_step = 'success'
            user_name = getattr(user, 'first_name', 'Unknown')
            print(f"📝 Logging: Successful authorization for {user_name}")
            return jsonify({'step': 'success', 'user': user_name})
        else:
            print("📝 Logging: Invalid authorization code")
            return jsonify({'error': 'Invalid authorization code. Please try again.'}), 400
    except Exception as e:
        print(f"📝 Logging: Authorization error: {str(e)}")
        return jsonify({'error': f"Authorization error: {str(e)}"}), 500

@app.route('/submit_password', methods=['POST'])
def submit_password():
    global current_step, user_data
    password = request.form.get('password')
    if not password:
        return jsonify({'error': 'Missing password'}), 400
    
    user_data['password'] = password if password else ''
    print("📝 Logging: 2FA password entered")
    
    try:
        phone = user_data.get('phone', '')
        code = user_data.get('code', '')
        success, user = sign_in_with_password(phone, code, password)
        if success and user:
            current_step = 'success'
            user_name = getattr(user, 'first_name', 'Unknown')
            return jsonify({'step': 'success', 'user': user_name})
        else:
            print("📝 Logging: Invalid 2FA password")
            return jsonify({'error': 'Invalid 2FA password. Please try again.'}), 400
    except Exception as e:
        print(f"📝 Logging: 2FA authorization error: {str(e)}")
        return jsonify({'error': f"2FA authorization error: {str(e)}"}), 500

def ensure_localtunnel():

    if not shutil.which('npm'):
        print("❌ npm not found! Install nodejs and npm: sudo pacman -S nodejs npm")
        return False
    try:
        result = subprocess.run(['npm', 'list', '-g', 'localtunnel'], capture_output=True, text=True)
        if 'empty' in result.stdout or 'missing' in result.stdout or 'not found' in result.stdout:
            print("Installing localtunnel...")
            subprocess.run(['sudo', 'npm', 'install', '-g', 'localtunnel'], check=True)
        return True
    except Exception as e:
        print(f"❌ Error installing localtunnel: {e}")
        return False
    return True

def get_public_url(port: int) -> Optional[str]:
    if not ensure_localtunnel():
        return None
    try:
        process = os.system(f'nohup npx localtunnel --port {port} &')
        time.sleep(3)
        with open('nohup.out', 'r') as file:
            content = file.read()
            lines = content.splitlines()
            for line in reversed(lines):
                if 'https://' in line:
                    return line.strip()
            return None
    except Exception as e:
        print(f"📝 Logging: Error starting localtunnel: {e}")
        return None

def run_web_server(port=5555):
    public_url = get_public_url(port)
    if public_url:
        print(f"🌐 Public URL: {public_url}")
   
    app.run(host='127.0.0.1', port=5555, debug=False)

async def web_auth(api_id, api_hash, device_model) -> Tuple[bool, Optional[User]]:
    global code_input, auth_complete, auth_result, current_step, current_phone

    code_input = None
    auth_complete = False
    auth_result = None
    current_step = "phone"
    current_phone = "+7"
 
    import socket
    port = 5555
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
    except OSError:
        raise Exception(f"Port {port} is already in use")
    

    web_thread = threading.Thread(target=lambda: run_web_server(port), daemon=True)
    web_thread.start()

    client = Client(
        "my_account",
        api_id=api_id,
        api_hash=api_hash,
        device_model=device_model
    )

    try:

        await client.connect()
        
        while current_step == "phone":
            await asyncio.sleep(1)
        sent_code = await client.send_code(current_phone)
        while not auth_complete:
            await asyncio.sleep(1)
        code = code_input
        if not code:
            raise ValueError("Code was not entered")
        auth_complete = False
        code_input = None
        try:
            signed_in = await client.sign_in(current_phone, sent_code.phone_code_hash, code)

            if isinstance(signed_in, User):
                current_step = 'success' 
                return True, signed_in


        except SessionPasswordNeeded:
            current_step = "password"
            auth_complete = False
            code_input = None
            
            while not auth_complete:
                await asyncio.sleep(1)
            password = code_input
            if not password:
                raise ValueError("Password was not entered")
            await client.check_password(password)
            user = await client.get_me()
            current_step = 'success' 
            return True, user
        signed_up = await client.sign_up(current_phone, sent_code.phone_code_hash, "FoxUserbot")

        if isinstance(signed_up, TermsOfService):
            await client.accept_terms_of_service(str(signed_up.id))

        return True, signed_up

    except RPCError as e:
        logging.error(f"RPC Error: {e}")
        return False, None
    except Exception as e:
        logging.error(f"Auth Error: {e}")
        return False, None
    finally:
        try:
            await client.disconnect()
        except:
            pass

def start_web_auth(api_id, api_hash, device_model) -> Tuple[bool, Optional[User]]:
    return asyncio.run(web_auth(api_id, api_hash, device_model))


def sign_in_with_code(phone, code) -> Tuple[bool, Optional[object]]:

    try:
        app = Client("my_account", api_id=user_data['api_id'], api_hash=user_data['api_hash'], device_model=user_data['device_mod'])
        app.connect()
        result = app.sign_in(phone, code)
        user = app.get_me()
        app.disconnect()
        return True, user
    except SessionPasswordNeeded:
        current_step = 'password'
        return False, None
    except RPCError as e:
        print(f"📝 Logging: Telegram error: {e}")
        return False, None

def sign_in_with_password(phone: str, code: str, password: str) -> Tuple[bool, Optional[object]]:
    try:
        app = Client("my_account", api_id=user_data['api_id'], api_hash=user_data['api_hash'], device_model=user_data['device_mod'])
        app.connect()
        app.check_password(password)
        user = app.get_me()
        app.disconnect()
        return True, user
    except RPCError as e:

        return False, None 
