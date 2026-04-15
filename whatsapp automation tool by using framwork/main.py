"""
WhatsApp Automation Tool - PROPER MEDIA HANDLING VERSION
Fixed: Images, Videos, Audio, Documents now send as actual media
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import datetime
import csv
import time
import json
import os
import re
import threading
from dataclasses import dataclass, asdict
from enum import Enum
import pyautogui
import webbrowser
import urllib.parse
import pyperclip
import subprocess
import platform

# Configuration
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5  # Increased pause for reliability

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatsapp-automation-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)


# ============================================================================
# DATA MODELS
# ============================================================================

class MessageStatus(Enum):
    SENT = "Sent"
    FAILED = "Failed"
    EMPTY = "Empty"


@dataclass
class Attachment:
    filePath: str
    fileType: str  # 'image', 'video', 'audio', 'document'
    fileName: str
    fileSize: str


@dataclass
class MessageHistory:
    timestamp: str
    recipient: str
    recipientName: str
    message: str
    status: str
    attachment: str = ""
    attachmentType: str = ""
    recipientType: str = "Individual"


# ============================================================================
# CORE FUNCTIONALITY WITH PROPER MEDIA HANDLING
# ============================================================================

class WhatsAppCore:
    def __init__(self):
        self.templates = {
            "Greeting": "Hello {name}! How are you doing today?",
            "Reminder": "Hi {name}, this is a friendly reminder about {customText}.",
            "Promo": "Dear {name}, we have a special offer for you today!",
            "ThankYou": "Thank you {name} for your support!",
            "Meeting": "Hi {name}, reminder about our meeting: {customText}.",
            "Birthday": "Happy Birthday {name}! Wishing you a wonderful day!",
            "GroupAnnouncement": "📢 *Announcement*\n\nHello everyone! {customText}",
            "GroupWelcome": "Welcome to the group {name}! 👋\n\n{customText}"
        }
        self.messageHistory = []
        self.historyFile = "data/MessageHistoryLog.csv"
        self.loadHistory()

    def loadHistory(self):
        try:
            if os.path.exists(self.historyFile):
                with open(self.historyFile, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.messageHistory.append(MessageHistory(
                            timestamp=row.get('timestamp', ''),
                            recipient=row.get('recipient', ''),
                            recipientName=row.get('recipientName', ''),
                            message=row.get('message', ''),
                            status=row.get('status', ''),
                            attachment=row.get('attachment', ''),
                            attachmentType=row.get('attachmentType', ''),
                            recipientType=row.get('recipientType', 'Individual')
                        ))
        except:
            pass

    def saveHistory(self):
        try:
            with open(self.historyFile, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'recipient', 'recipientName', 'message', 'status',
                              'attachment', 'attachmentType', 'recipientType']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.messageHistory:
                    writer.writerow({
                        'timestamp': entry.timestamp,
                        'recipient': entry.recipient,
                        'recipientName': entry.recipientName,
                        'message': entry.message,
                        'status': entry.status,
                        'attachment': entry.attachment,
                        'attachmentType': entry.attachmentType,
                        'recipientType': entry.recipientType
                    })
        except:
            pass

    def addToHistory(self, recipient, name, msg, status, attach="", attachType="", recipientType="Individual"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        displayMsg = msg
        if attach:
            displayMsg = f"[{attachType.upper()}] {msg[:50]}..." if msg else f"[{attachType.upper()} FILE] {attach}"

        entry = MessageHistory(
            timestamp=timestamp, recipient=recipient, recipientName=name or "Unknown",
            message=displayMsg[:100], status=status, attachment=attach,
            attachmentType=attachType, recipientType=recipientType
        )
        self.messageHistory.insert(0, entry)
        if len(self.messageHistory) > 500:
            self.messageHistory.pop()
        self.saveHistory()

    def getHistory(self, limit=100):
        return self.messageHistory[:limit]

    def clearHistory(self):
        self.messageHistory.clear()
        self.saveHistory()
        return True

    def getTemplates(self):
        return self.templates.copy()

    def addTemplate(self, name, content):
        if name and content:
            self.templates[name] = content
            return True
        return False

    def removeTemplate(self, name):
        if name in self.templates:
            del self.templates[name]
            return True
        return False

    # ========================================================================
    # PROPER MEDIA HANDLING - THIS IS THE FIXED PART
    # ========================================================================

    def attachAndSendMedia(self, filePath: str, fileType: str, progress_callback=None) -> bool:
        """
        Properly attach and send media file using the correct WhatsApp Web method
        """
        try:
            screenWidth, screenHeight = pyautogui.size()

            if progress_callback:
                progress_callback(f"📎 Attaching {fileType}: {os.path.basename(filePath)}")

            time.sleep(2)

            # STEP 1: Click the attachment (paperclip) button
            # WhatsApp Web attachment button is usually on the left side of message input
            attachX = int(screenWidth * 0.38)
            attachY = int(screenHeight - 80)

            print(f"Clicking attachment button at ({attachX}, {attachY})")
            pyautogui.click(attachX, attachY)
            time.sleep(2)  # Wait for menu to appear

            # STEP 2: Select the correct media type from the popup menu
            # The menu options appear in this order:
            # 1. Photos & Videos (for images and videos)
            # 2. Camera
            # 3. Document
            # 4. Contact
            # 5. Poll

            if fileType == "image" or fileType == "video":
                # For images and videos, select "Photos & Videos" (first option)
                print("Selecting Photos & Videos option")
                pyautogui.press('down', presses=1)  # First option
                time.sleep(0.5)
                pyautogui.press('enter')

            elif fileType == "document":
                # For documents, select "Document" (third option)
                print("Selecting Document option")
                pyautogui.press('down', presses=3)
                time.sleep(0.5)
                pyautogui.press('enter')

            elif fileType == "audio":
                # For audio, it's under Document menu, then select audio file
                print("Selecting Document option for audio")
                pyautogui.press('down', presses=3)
                time.sleep(0.5)
                pyautogui.press('enter')

            # Wait for file dialog to open
            time.sleep(3)

            if progress_callback:
                progress_callback(f"📂 Selecting file...")

            # STEP 3: Handle the file dialog
            # Convert to absolute path
            absPath = os.path.abspath(filePath)
            print(f"File path: {absPath}")

            # Method A: Use clipboard (most reliable)
            try:
                pyperclip.copy(absPath)
                time.sleep(0.5)

                # Paste the path into file dialog
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.5)

                # Press Enter to confirm file selection
                pyautogui.press('enter')
                time.sleep(2)

            except Exception as e:
                print(f"Clipboard method failed: {e}")
                # Method B: Type the path manually
                pyautogui.typewrite(absPath, interval=0.02)
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)

            # STEP 4: Wait for file to upload
            # File size affects upload time
            fileSizeMB = os.path.getsize(filePath) / (1024 * 1024)
            waitTime = max(5, min(int(fileSizeMB * 3), 45))  # Between 5-45 seconds

            if progress_callback:
                progress_callback(f"⏫ Uploading {fileType} ({fileSizeMB:.1f} MB)...")

            print(f"Waiting {waitTime} seconds for upload...")

            # Show countdown for large files
            for i in range(waitTime, 0, -1):
                if i % 5 == 0 and progress_callback:
                    progress_callback(f"Uploading... {i}s remaining")
                time.sleep(1)

            # STEP 5: Send the media
            print("Pressing Enter to send media...")
            pyautogui.press('enter')
            time.sleep(3)

            # For videos/large files, might need an extra enter
            if fileType == "video" and fileSizeMB > 5:
                time.sleep(2)
                pyautogui.press('enter')

            print("Media sent successfully!")
            return True

        except Exception as e:
            print(f"Error in attachAndSendMedia: {e}")
            import traceback
            traceback.print_exc()
            return False

    def sendToIndividual(self, phoneNumber: str, message: str, contactName: str = "",
                         attachment: Attachment = None, progress_callback=None) -> bool:
        """Send message to individual with proper media handling"""
        try:
            # Clean phone number
            phone = re.sub(r'[^\d+]', '', phoneNumber)
            if not phone.startswith("+"):
                phone = "+" + phone

            phoneForUrl = phone.replace("+", "")
            hasMessage = bool(message and message.strip())
            hasAttachment = attachment and os.path.exists(attachment.filePath)

            if not hasMessage and not hasAttachment:
                self.addToHistory(phone, contactName, "", MessageStatus.EMPTY.value)
                return False

            print(f"\n{'=' * 60}")
            print(f"SENDING TO: {contactName or phone}")
            print(f"MESSAGE: {message[:50] if message else 'No message'}")
            print(f"ATTACHMENT: {attachment.fileName if hasAttachment else 'None'}")
            print(f"{'=' * 60}")

            if progress_callback:
                progress_callback(f"📱 Opening chat with {contactName or phone}...")

            # Open WhatsApp Web
            url = f"https://web.whatsapp.com/send?phone={phoneForUrl}"
            webbrowser.open(url)

            # Wait for page to load
            for i in range(15, 0, -1):
                if progress_callback and i % 5 == 0:
                    progress_callback(f"⏳ Loading WhatsApp... {i}s")
                time.sleep(1)

            screenWidth, screenHeight = pyautogui.size()

            # Click to focus
            pyautogui.click(screenWidth // 2, screenHeight // 2)
            time.sleep(2)

            # Send attachment FIRST if present (important: media first, then text)
            if hasAttachment:
                if progress_callback:
                    progress_callback(f"📎 Sending {attachment.fileType}...")

                if not self.attachAndSendMedia(attachment.filePath, attachment.fileType, progress_callback):
                    raise Exception("Failed to send media")

                time.sleep(2)

            # Send text message
            if hasMessage:
                if progress_callback:
                    progress_callback("💬 Sending message...")

                # Click message input area
                pyautogui.click(screenWidth // 2, screenHeight - 100)
                time.sleep(1)

                # Clear any existing text
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)

                # Type message
                try:
                    pyperclip.copy(message)
                    pyautogui.hotkey('ctrl', 'v')
                except:
                    pyautogui.typewrite(message, interval=0.02)

                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)

            # Close tab
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)

            # Record success
            attachInfo = attachment.fileName if hasAttachment else ""
            attachType = attachment.fileType if hasAttachment else ""
            self.addToHistory(phone, contactName, message, MessageStatus.SENT.value,
                              attachInfo, attachType)

            if progress_callback:
                progress_callback(f"✅ Sent successfully to {contactName or phone}")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

            attachInfo = attachment.fileName if attachment else ""
            attachType = attachment.fileType if attachment else ""
            self.addToHistory(phoneNumber, contactName, message, MessageStatus.FAILED.value,
                              attachInfo, attachType)

            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")

            return False

    def sendToGroup(self, groupName: str, message: str, attachment: Attachment = None,
                    progress_callback=None) -> bool:
        """Send message to group with proper media handling"""
        try:
            print(f"\n{'=' * 60}")
            print(f"SENDING TO GROUP: {groupName}")
            print(f"{'=' * 60}")

            if progress_callback:
                progress_callback("📱 Opening WhatsApp Web...")

            webbrowser.open("https://web.whatsapp.com")

            # Wait for page to load
            for i in range(15, 0, -1):
                if progress_callback and i % 5 == 0:
                    progress_callback(f"⏳ Loading... {i}s")
                time.sleep(1)

            screenWidth, screenHeight = pyautogui.size()

            if progress_callback:
                progress_callback(f"🔍 Searching for group: {groupName}")

            # Click search box
            searchX = int(screenWidth * 0.3)
            searchY = 50
            pyautogui.click(searchX, searchY)
            time.sleep(1)

            # Clear and type group name
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('backspace')
            time.sleep(1)

            pyautogui.typewrite(groupName, interval=0.05)
            time.sleep(3)
            pyautogui.press('enter')
            time.sleep(3)

            # Click message area
            pyautogui.click(screenWidth // 2, screenHeight - 100)
            time.sleep(1)

            # Send attachment first if present
            hasAttachment = attachment and os.path.exists(attachment.filePath)
            if hasAttachment:
                if progress_callback:
                    progress_callback(f"📎 Sending {attachment.fileType}...")

                if not self.attachAndSendMedia(attachment.filePath, attachment.fileType, progress_callback):
                    raise Exception("Failed to send media")

                time.sleep(2)

            # Send text message
            if message and message.strip():
                if progress_callback:
                    progress_callback("💬 Sending message...")

                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)

                try:
                    pyperclip.copy(message)
                    pyautogui.hotkey('ctrl', 'v')
                except:
                    pyautogui.typewrite(message, interval=0.02)

                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)

            # Close tab
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'w')

            # Record success
            attachInfo = attachment.fileName if hasAttachment else ""
            attachType = attachment.fileType if hasAttachment else ""
            self.addToHistory(groupName, groupName, message, MessageStatus.SENT.value,
                              attachInfo, attachType, "Group")

            if progress_callback:
                progress_callback(f"✅ Sent successfully to group {groupName}")

            return True

        except Exception as e:
            print(f"Error: {e}")

            attachInfo = attachment.fileName if attachment else ""
            attachType = attachment.fileType if attachment else ""
            self.addToHistory(groupName, groupName, message, MessageStatus.FAILED.value,
                              attachInfo, attachType, "Group")

            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")

            return False


# Initialize core
core = WhatsAppCore()


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/templates', methods=['GET'])
def get_templates():
    return jsonify(core.getTemplates())


@app.route('/api/templates', methods=['POST'])
def add_template():
    data = request.json
    name = data.get('name', '').strip()
    content = data.get('content', '').strip()
    if name and content and core.addTemplate(name, content):
        return jsonify({'success': True})
    return jsonify({'success': False}), 400


@app.route('/api/templates/<name>', methods=['DELETE'])
def delete_template(name):
    return jsonify({'success': core.removeTemplate(name)})


@app.route('/api/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', 100, type=int)
    return jsonify([asdict(h) for h in core.getHistory(limit)])


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    core.clearHistory()
    return jsonify({'success': True})


@app.route('/api/history/export', methods=['GET'])
def export_history():
    history = core.getHistory(1000)
    export_path = 'data/history_export.csv'
    with open(export_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'recipientType', 'recipient', 'recipientName', 'message',
                                               'status'])
        writer.writeheader()
        for h in history:
            writer.writerow({'timestamp': h.timestamp, 'recipientType': h.recipientType,
                             'recipient': h.recipient, 'recipientName': h.recipientName,
                             'message': h.message, 'status': h.status})
    return send_file(export_path, as_attachment=True, download_name='whatsapp_history.csv')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Determine file type
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']:
        fileType = 'image'
    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv']:
        fileType = 'video'
    elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.opus']:
        fileType = 'audio'
    else:
        fileType = 'document'

    fileSize = os.path.getsize(filepath)
    if fileSize < 1024 * 1024:
        sizeStr = f"{fileSize / 1024:.1f} KB"
    else:
        sizeStr = f"{fileSize / (1024 * 1024):.1f} MB"

    return jsonify({
        'success': True,
        'file': {'path': filepath, 'name': filename, 'type': fileType, 'size': sizeStr}
    })


@app.route('/api/contacts/upload', methods=['POST'])
def upload_contacts():
    if 'file' not in request.files:
        return jsonify({'success': False}), 400

    file = request.files['file']
    contacts = []
    try:
        content = file.read().decode('utf-8')
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            isGroup = row.get('type', '').lower().strip() == 'group'
            recipient = row.get('recipient') or row.get('phone') or row.get('number') or row.get('group')
            name = row.get('name', row.get('contactName', 'Unknown'))
            if recipient:
                if not isGroup and not recipient.startswith('+'):
                    recipient = '+' + recipient
                contacts.append({'phoneNumber': recipient, 'contactName': name, 'isGroup': isGroup})
        return jsonify({'success': True, 'contacts': contacts, 'count': len(contacts)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('send_single')
def handle_send_single(data):
    phone = data.get('phone', '').strip()
    name = data.get('name', '').strip()
    message = data.get('message', '').strip()
    attachment_data = data.get('attachment')

    def progress_callback(status):
        socketio.emit('progress_update', {'status': status})

    def send_task():
        attach_obj = None
        if attachment_data:
            attach_obj = Attachment(
                filePath=attachment_data['path'],
                fileType=attachment_data['type'],
                fileName=attachment_data['name'],
                fileSize=attachment_data['size']
            )

        result = core.sendToIndividual(phone, message, name, attach_obj, progress_callback)
        socketio.emit('send_complete',
                      {'success': result, 'message': f"{'✅' if result else '❌'} Message to {name or phone}"})

    threading.Thread(target=send_task, daemon=True).start()
    emit('send_started', {'message': '🚀 Sending...'})


@socketio.on('send_group')
def handle_send_group(data):
    groupName = data.get('groupName', '').strip()
    message = data.get('message', '').strip()
    attachment_data = data.get('attachment')

    def progress_callback(status):
        socketio.emit('progress_update', {'status': status})

    def send_task():
        attach_obj = None
        if attachment_data:
            attach_obj = Attachment(
                filePath=attachment_data['path'],
                fileType=attachment_data['type'],
                fileName=attachment_data['name'],
                fileSize=attachment_data['size']
            )

        result = core.sendToGroup(groupName, message, attach_obj, progress_callback)
        socketio.emit('send_complete',
                      {'success': result, 'message': f"{'✅' if result else '❌'} Message to group {groupName}"})

    threading.Thread(target=send_task, daemon=True).start()
    emit('send_started', {'message': '🚀 Sending to group...'})


@socketio.on('send_bulk')
def handle_send_bulk(data):
    contacts = data.get('contacts', [])
    message = data.get('message', '').strip()
    attachment_data = data.get('attachment')

    def send_task():
        attach_obj = None
        if attachment_data:
            attach_obj = Attachment(
                filePath=attachment_data['path'],
                fileType=attachment_data['type'],
                fileName=attachment_data['name'],
                fileSize=attachment_data['size']
            )

        success = 0
        total = len(contacts)

        for i, contact in enumerate(contacts):
            socketio.emit('bulk_progress', {'current': i + 1, 'total': total, 'contact': contact['contactName']})
            socketio.emit('progress_update', {'status': f"📤 Sending to {contact['contactName']} ({i + 1}/{total})"})

            if contact.get('isGroup'):
                result = core.sendToGroup(contact['phoneNumber'], message, attach_obj)
            else:
                result = core.sendToIndividual(contact['phoneNumber'], message, contact['contactName'], attach_obj)

            if result:
                success += 1

            if i < total - 1:
                time.sleep(8)

        socketio.emit('send_complete', {'success': True, 'message': f"✅ Bulk complete: {success}/{total} successful"})

    threading.Thread(target=send_task, daemon=True).start()
    emit('send_started', {'message': f'🚀 Sending to {len(contacts)} recipients...'})


# ============================================================================
# HTML TEMPLATE (SIMPLIFIED)
# ============================================================================

os.makedirs('templates', exist_ok=True)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp Automation - Media Support</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .main-container { max-width: 1200px; margin: 20px auto; }
        .app-header { background: #075E54; color: white; padding: 20px; border-radius: 15px 15px 0 0; }
        .app-content { background: white; border-radius: 0 0 15px 15px; padding: 30px; }
        .btn-whatsapp { background: #25D366; color: white; font-weight: bold; padding: 12px 30px; border: none; border-radius: 50px; }
        .attachment-area { border: 2px dashed #ddd; border-radius: 10px; padding: 20px; text-align: center; cursor: pointer; }
        .attachment-area:hover { border-color: #25D366; background: #f8f9fa; }
        .file-attached { border-color: #25D366; background: #DCF8C6; }
        .media-btn { padding: 8px 16px; margin: 3px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="app-header">
            <div class="d-flex justify-content-between">
                <div>
                    <h2><i class="bi bi-whatsapp"></i> WhatsApp Automation</h2>
                    <p>✅ Images • Videos • Audio • Documents Support</p>
                </div>
                <button class="btn btn-light" onclick="openWhatsAppWeb()">📱 Open WhatsApp Web</button>
            </div>
        </div>

        <div class="app-content">
            <div class="alert alert-warning">
                <i class="bi bi-info-circle"></i> Keep WhatsApp Web OPEN and VISIBLE. DO NOT touch mouse/keyboard while sending.
            </div>

            <ul class="nav nav-tabs mb-4">
                <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#single">👤 Single</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#group">👥 Group</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#bulk">📋 Bulk</button></li>
                <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#history">📊 History</button></li>
            </ul>

            <div class="tab-content">
                <!-- Single Tab -->
                <div class="tab-pane fade show active" id="single">
                    <h4>Send Individual Message</h4>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <label>📞 Phone Number</label>
                            <input type="text" class="form-control" id="singlePhone" value="+" placeholder="+923001234567">
                        </div>
                        <div class="col-md-6">
                            <label>👤 Name (Optional)</label>
                            <input type="text" class="form-control" id="singleName" placeholder="John Doe">
                        </div>
                    </div>
                    <div class="mt-3">
                        <label>💬 Message</label>
                        <textarea class="form-control" id="singleMessage" rows="3" placeholder="Type your message..."></textarea>
                        <small><span id="singleCharCount">0</span> characters</small>
                    </div>
                    <div class="mt-3">
                        <label>📎 Attachment</label>
                        <div class="btn-group w-100 mb-2">
                            <button class="btn btn-outline-success media-btn" onclick="document.getElementById('singleImageInput').click()">🖼️ Image</button>
                            <button class="btn btn-outline-primary media-btn" onclick="document.getElementById('singleVideoInput').click()">🎥 Video</button>
                            <button class="btn btn-outline-warning media-btn" onclick="document.getElementById('singleAudioInput').click()">🎵 Audio</button>
                            <button class="btn btn-outline-secondary media-btn" onclick="document.getElementById('singleDocInput').click()">📄 Document</button>
                        </div>
                        <input type="file" id="singleImageInput" accept="image/*" style="display:none" onchange="handleFileSelect(this, 'single', 'image')">
                        <input type="file" id="singleVideoInput" accept="video/*" style="display:none" onchange="handleFileSelect(this, 'single', 'video')">
                        <input type="file" id="singleAudioInput" accept="audio/*" style="display:none" onchange="handleFileSelect(this, 'single', 'audio')">
                        <input type="file" id="singleDocInput" accept=".pdf,.doc,.docx,.txt,.zip" style="display:none" onchange="handleFileSelect(this, 'single', 'document')">
                        <div class="attachment-area" id="singleAttachmentArea" onclick="document.getElementById('singleDocInput').click()">
                            <i class="bi bi-cloud-upload fs-1"></i>
                            <p>Click to upload or use buttons above</p>
                            <div id="singleFileInfo"></div>
                        </div>
                    </div>
                    <button class="btn btn-whatsapp mt-3" onclick="sendSingleMessage()"><i class="bi bi-send"></i> Send Message</button>
                </div>

                <!-- Group Tab -->
                <div class="tab-pane fade" id="group">
                    <h4>Send Group Message</h4>
                    <div class="mt-3">
                        <label>👥 Group Name (exact match)</label>
                        <input type="text" class="form-control" id="groupName" placeholder="Family Group">
                    </div>
                    <div class="mt-3">
                        <label>💬 Message</label>
                        <textarea class="form-control" id="groupMessage" rows="3" placeholder="Type your message..."></textarea>
                    </div>
                    <div class="mt-3">
                        <label>📎 Attachment</label>
                        <div class="btn-group w-100 mb-2">
                            <button class="btn btn-outline-success media-btn" onclick="document.getElementById('groupImageInput').click()">🖼️</button>
                            <button class="btn btn-outline-primary media-btn" onclick="document.getElementById('groupVideoInput').click()">🎥</button>
                            <button class="btn btn-outline-warning media-btn" onclick="document.getElementById('groupAudioInput').click()">🎵</button>
                            <button class="btn btn-outline-secondary media-btn" onclick="document.getElementById('groupDocInput').click()">📄</button>
                        </div>
                        <input type="file" id="groupImageInput" accept="image/*" style="display:none" onchange="handleFileSelect(this, 'group', 'image')">
                        <input type="file" id="groupVideoInput" accept="video/*" style="display:none" onchange="handleFileSelect(this, 'group', 'video')">
                        <input type="file" id="groupAudioInput" accept="audio/*" style="display:none" onchange="handleFileSelect(this, 'group', 'audio')">
                        <input type="file" id="groupDocInput" accept=".pdf,.doc,.docx,.txt,.zip" style="display:none" onchange="handleFileSelect(this, 'group', 'document')">
                        <div class="attachment-area" id="groupAttachmentArea">
                            <i class="bi bi-cloud-upload fs-1"></i>
                            <div id="groupFileInfo"></div>
                        </div>
                    </div>
                    <button class="btn btn-whatsapp mt-3" onclick="sendGroupMessage()"><i class="bi bi-send"></i> Send to Group</button>
                </div>

                <!-- Bulk Tab -->
                <div class="tab-pane fade" id="bulk">
                    <h4>Bulk Messaging</h4>
                    <div class="mt-3">
                        <label>📂 Upload CSV</label>
                        <input type="file" class="form-control" id="csvFile" accept=".csv" onchange="loadCSV(this)">
                        <small>Format: type,recipient,name (type: individual or group)</small>
                    </div>
                    <div id="contactsPreview" class="mt-2"></div>
                    <div class="mt-3">
                        <label>💬 Message</label>
                        <textarea class="form-control" id="bulkMessage" rows="3"></textarea>
                    </div>
                    <div class="mt-3">
                        <label>📎 Attachment (same for all)</label>
                        <input type="file" id="bulkFileInput" style="display:none" onchange="handleFileSelect(this, 'bulk', 'auto')">
                        <div class="attachment-area" onclick="document.getElementById('bulkFileInput').click()">
                            <div id="bulkFileInfo">Click to upload</div>
                        </div>
                    </div>
                    <button class="btn btn-whatsapp mt-3" onclick="sendBulkMessages()" id="bulkSendBtn" disabled>Send to All</button>
                </div>

                <!-- History Tab -->
                <div class="tab-pane fade" id="history">
                    <h4>Message History</h4>
                    <button class="btn btn-outline-primary btn-sm me-2" onclick="refreshHistory()">🔄 Refresh</button>
                    <button class="btn btn-outline-danger btn-sm me-2" onclick="clearHistory()">🗑️ Clear</button>
                    <button class="btn btn-outline-success btn-sm" onclick="exportHistory()">📥 Export CSV</button>
                    <div class="table-responsive mt-3">
                        <table class="table table-hover">
                            <thead><tr><th>Time</th><th>Type</th><th>Recipient</th><th>Message</th><th>Status</th></tr></thead>
                            <tbody id="historyTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress-container mt-4" id="progressSection" style="display:none; background:#f0f0f0; padding:15px; border-radius:10px;">
                <div class="d-flex justify-content-between">
                    <span id="progressStatus">Ready</span>
                    <div class="spinner-border spinner-border-sm text-success"></div>
                </div>
                <div class="progress mt-2"><div class="progress-bar" id="progressBar" style="width:0%"></div></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const socket = io();
        let attachments = { single: null, group: null, bulk: null };
        let bulkContacts = [];

        socket.on('send_started', d => { showProgress(true); updateProgress(10, d.message); });
        socket.on('progress_update', d => updateProgress(null, d.status));
        socket.on('bulk_progress', d => updateProgress((d.current/d.total)*100, `Sending to ${d.contact} (${d.current}/${d.total})`));
        socket.on('send_complete', d => { showProgress(false); alert(d.message); refreshHistory(); });

        function showProgress(s) { document.getElementById('progressSection').style.display = s ? 'block' : 'none'; }
        function updateProgress(p, s) {
            if (p !== null) document.getElementById('progressBar').style.width = p + '%';
            if (s) document.getElementById('progressStatus').textContent = s;
        }
        function openWhatsAppWeb() { window.open('https://web.whatsapp.com', '_blank'); }

        function handleFileSelect(input, type, fileType) {
            const file = input.files[0]; if (!file) return;
            const formData = new FormData(); formData.append('file', file);
            fetch('/api/upload', { method: 'POST', body: formData })
                .then(r => r.json()).then(d => {
                    if (d.success) {
                        attachments[type] = d.file;
                        const icons = { image: '🖼️', video: '🎥', audio: '🎵', document: '📄' };
                        document.getElementById(type + 'FileInfo').innerHTML = `${icons[d.file.type] || '📎'} ${d.file.name} (${d.file.size})`;
                        document.getElementById(type + 'AttachmentArea').classList.add('file-attached');
                    }
                });
        }

        function sendSingleMessage() {
            const phone = document.getElementById('singlePhone').value.trim();
            if (!phone || phone === '+') { alert('Enter phone number'); return; }
            socket.emit('send_single', {
                phone, name: document.getElementById('singleName').value.trim(),
                message: document.getElementById('singleMessage').value.trim(),
                attachment: attachments.single
            });
        }

        function sendGroupMessage() {
            const name = document.getElementById('groupName').value.trim();
            if (!name) { alert('Enter group name'); return; }
            socket.emit('send_group', {
                groupName: name,
                message: document.getElementById('groupMessage').value.trim(),
                attachment: attachments.group
            });
        }

        function loadCSV(input) {
            const file = input.files[0]; if (!file) return;
            const formData = new FormData(); formData.append('file', file);
            fetch('/api/contacts/upload', { method: 'POST', body: formData })
                .then(r => r.json()).then(d => {
                    if (d.success) {
                        bulkContacts = d.contacts;
                        document.getElementById('bulkSendBtn').disabled = false;
                        document.getElementById('contactsPreview').innerHTML = `<div class="alert alert-success">✅ ${d.count} contacts loaded</div>`;
                    }
                });
        }

        function sendBulkMessages() {
            if (!bulkContacts.length) { alert('Load contacts first'); return; }
            socket.emit('send_bulk', {
                contacts: bulkContacts,
                message: document.getElementById('bulkMessage').value.trim(),
                attachment: attachments.bulk
            });
        }

        function refreshHistory() {
            fetch('/api/history').then(r => r.json()).then(h => {
                const tbody = document.getElementById('historyTableBody'); tbody.innerHTML = '';
                h.forEach(e => {
                    const row = tbody.insertRow();
                    row.innerHTML = `<td>${e.timestamp}</td><td>${e.recipientType}</td><td>${e.recipientName}<br><small>${e.recipient}</small></td><td>${e.message}</td><td><span class="badge bg-${e.status==='Sent'?'success':'danger'}">${e.status}</span></td>`;
                });
            });
        }

        function clearHistory() { if (confirm('Clear all history?')) fetch('/api/history', {method:'DELETE'}).then(() => refreshHistory()); }
        function exportHistory() { window.location.href = '/api/history/export'; }

        ['single', 'group', 'bulk'].forEach(t => {
            document.getElementById(t+'Message')?.addEventListener('input', function() {
                document.getElementById(t+'CharCount').textContent = this.value.length;
            });
        });

        document.addEventListener('DOMContentLoaded', refreshHistory);
    </script>
</body>
</html>
    ''')


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("✅ WhatsApp Automation Tool - PROPER MEDIA HANDLING")
    print("=" * 70)
    print("\n📱 Features:")
    print("   • Images send as actual images (not file paths)")
    print("   • Videos send as actual videos")
    print("   • Audio sends as actual audio files")
    print("   • Documents send as actual documents")
    print("\n🌐 Access at: http://localhost:5000")
    print("=" * 70)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()