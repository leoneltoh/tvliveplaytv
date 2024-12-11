from flask import Flask, send_file, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import re
from datetime import datetime
import pytz

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire pour stocker le nombre de spectateurs par flux
viewers = {}

# Stockage temporaire des programmes (à remplacer par une base de données)
channel_programs = {}

def parse_m3u(url):
    try:
        response = requests.get(url)
        content = response.text
        channels = []

        lines = content.split('\n')
        current_channel = {}

        for line in lines:
            if line.startswith('#EXTINF:'):
                match = re.search(r'tvg-logo="([^"]*)".*?,(.*)$', line)
                if match:
                    current_channel = {
                        'logo': match.group(1),
                        'name': match.group(2).strip()
                    }
            elif line.startswith('http'):
                if current_channel:
                    current_channel['url'] = line.strip()
                    channels.append(current_channel)
                    current_channel = {}

        return channels
    except Exception as e:
        print(f"Erreur lors de la récupération du M3U: {e}")
        return []


def get_program(channel_name):
    try:
        if channel_name not in channel_programs:
            # Programme par défaut si aucun n'existe
            channel_programs[channel_name] = [
                {
                    "time": datetime.now(pytz.UTC).strftime("%H:%M"),
                    "title": "Programme en cours",
                    "description": "Description du programme en cours"
                }
            ]
        return channel_programs[channel_name]
    except Exception as e:
        print(f"Erreur lors de la récupération du programme: {e}")
        return []


@app.route('/')
def home():
    channels = parse_m3u(
        'https://liste-des-chaines-m-3-u-graceafrica2.replit.app/playtv.m3u')

    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PlayTV 4K</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            /* Version: 1.0.1 */
            :root {
                --primary-color: #ff69b4;
                --bg-color: #121212;
                --text-light: #ffffff;
                --card-bg: rgba(0, 0, 0, 0.6);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: var(--bg-color);
                color: var(--text-light);
                line-height: 1.6;
                min-height: 100vh;
                background-image: url('https://liste-des-chaines-m-3-u-graceafrica2.replit.app/f.jpg?ixlib=rb-4.0.3');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }
            
            header {
                background: rgba(0, 0, 0, 0.8);
                padding: 1rem;
                text-align: center;
                backdrop-filter: blur(10px);
                border-bottom: 2px solid var(--primary-color);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            h1 {
                font-size: 1.2rem;
                color: var(--primary-color);
                text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
            }

            .tv-icon {
                color: var(--primary-color);
                font-size: 1.4rem;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 1rem;
            }
            
            .search-container {
                margin: 20px auto;
                width: 100%;
                max-width: 800px;
                padding: 0 20px;
                position: relative;
            }

            .search-input {
                width: 100%;
                padding: 15px 20px 15px 45px;
                border: 2px solid var(--primary-color);
                border-radius: 30px;
                background: rgba(0, 0, 0, 0.6);
                color: var(--text-light);
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(255, 105, 180, 0.1);
            }

            .search-input:focus {
                outline: none;
                background: rgba(0, 0, 0, 0.8);
                box-shadow: 0 0 20px rgba(255, 105, 180, 0.2);
                transform: translateY(-2px);
            }

            .search-input::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }

            .search-icon {
                position: absolute;
                left: 35px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--primary-color);
                font-size: 1.2rem;
            }

            .channel-list {
                display: flex;
                flex-direction: column;
                gap: 0.3rem;
                margin-top: 1rem;
            }
            
            .channel-item {
                display: flex;
                align-items: center;
                padding: 0.4rem;
                background: var(--card-bg);
                border-radius: 6px;
                backdrop-filter: blur(5px);
                transition: transform 0.2s ease, background 0.3s ease;
                border: 1px solid rgba(255, 105, 180, 0.1);
                text-decoration: none;
                position: relative;
            }
            
            .channel-item:hover {
                transform: translateX(5px);
                background: rgba(0, 0, 0, 0.8);
                border-color: var(--primary-color);
            }
            
            .channel-logo {
                width: 35px;
                height: 35px;
                object-fit: contain;
                margin-right: 10px;
                border-radius: 4px;
            }
            
            .channel-name {
                font-size: 1rem;
                color: var(--text-light);
                flex-grow: 1;
            }

            .program-btn {
                background: transparent !important;
                border: none !important;
                padding: 8px !important;
                color: rgba(255, 255, 255, 0.8) !important;
                cursor: pointer;
                font-size: 1.2rem !important;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-left: auto;
            }

            .program-btn:hover {
                color: rgba(255, 255, 255, 1) !important;
                transform: scale(1.1);
            }

            .share-btn {
                background: transparent !important;
                border: none !important;
                padding: 8px !important;
                color: rgba(255, 255, 255, 0.8) !important;
                cursor: pointer;
                font-size: 1.2rem !important;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .share-btn:hover {
                color: rgba(255, 255, 255, 1) !important;
                transform: scale(1.1);
            }

            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .modal.show {
                opacity: 1;
            }

            .modal-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) scale(0.7);
                background: linear-gradient(145deg, #1a1a1a, #121212);
                padding: 25px;
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                color: white;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                opacity: 0;
                transition: all 0.3s ease;
            }

            .modal.show .modal-content {
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }

            .modal-header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid rgba(255, 105, 180, 0.2);
                position: relative;
            }

            .modal-header::after {
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                width: 50px;
                height: 2px;
                background: var(--primary-color);
                transition: width 0.3s ease;
            }

            .modal-header:hover::after {
                width: 100%;
            }

            .program-item {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                transform: translateX(-20px);
                opacity: 0;
                animation: slideIn 0.5s ease forwards;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .program-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 0;
                background: var(--primary-color);
                transition: height 0.3s ease;
            }

            .program-item:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.08);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }

            .program-item:hover::before {
                height: 100%;
            }

            @keyframes slideIn {
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            .program-time {
                color: var(--primary-color);
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .program-time i {
                font-size: 0.9em;
                opacity: 0.8;
            }

            .program-title {
                font-size: 1.2em;
                margin-bottom: 8px;
                color: white;
                font-weight: 500;
            }

            .program-description {
                color: rgba(255, 255, 255, 0.7);
                line-height: 1.5;
                font-size: 0.95em;
            }

            .program-actions {
                display: flex;
                gap: 15px;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
            }

            .program-item:hover .program-actions {
                opacity: 1;
                transform: translateY(0);
            }

            .program-action-btn {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                cursor: pointer;
                font-size: 1rem;
                padding: 8px;
                border-radius: 50%;
                transition: all 0.3s ease;
                position: relative;
            }

            .program-action-btn::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 0;
                height: 0;
                background: rgba(255, 105, 180, 0.1);
                border-radius: 50%;
                transition: all 0.3s ease;
                z-index: -1;
            }

            .program-action-btn:hover::before {
                width: 35px;
                height: 35px;
            }

            .program-action-btn:hover {
                color: var(--primary-color);
                transform: scale(1.1);
            }

            .close-modal {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 5px;
                border-radius: 50%;
                transition: all 0.3s ease;
                position: relative;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .close-modal::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 0;
                height: 0;
                background: rgba(255, 105, 180, 0.1);
                border-radius: 50%;
                transition: all 0.3s ease;
            }

            .close-modal:hover::before {
                width: 100%;
                height: 100%;
            }

            .close-modal:hover {
                color: var(--primary-color);
                transform: rotate(90deg);
            }

            #programList {
                max-height: 60vh;
                overflow-y: auto;
                padding-right: 10px;
                margin: 20px 0;
            }

            #programList::-webkit-scrollbar {
                width: 8px;
            }

            #programList::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }

            #programList::-webkit-scrollbar-thumb {
                background: var(--primary-color);
                border-radius: 4px;
                transition: all 0.3s ease;
            }

            #programList::-webkit-scrollbar-thumb:hover {
                background: #ff45a0;
            }

            /* Styles pour le modal de partage */
            .share-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 1000;
            }

            .share-modal-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(145deg, #1a1a1a, #121212);
                padding: 25px;
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                color: white;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }

            .share-buttons {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-top: 20px;
            }

            .social-share-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                padding: 12px;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .social-share-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }

            .facebook-btn {
                background: #1877f2;
            }

            .twitter-btn {
                background: #1da1f2;
            }

            .whatsapp-btn {
                background: #25d366;
            }

            .telegram-btn {
                background: #0088cc;
            }
        </style>
    </head>
    <body>
        <header>
            <i class="fas fa-tv tv-icon"></i>
            <h1>Play TV 4K</h1>
        </header>
        <div class="container">
            <div class="search-container">
                <i class="fas fa-search search-icon"></i>
                <input type="text" 
                       class="search-input" 
                       placeholder="Rechercher une chaîne..." 
                       id="searchInput"
                       autocomplete="off">
            </div>
            <div class="channel-list">
    '''

    for channel in channels:
        html_content += f'''
            <a href="/player?url={channel['url']}&name={channel['name']}" class="channel-item">
                <img class="channel-logo" src="{channel['logo']}" 
                     onerror="this.src='https://via.placeholder.com/40x40?text=TV&bg=252525&color=ff69b4'" 
                     alt="{channel['name']}">
                <span class="channel-name">{channel['name']}</span>
                <button class="program-btn" onclick="showProgram(event, '{channel['name']}')" title="Voir le programme">
                    <i class="fas fa-tv"></i>
                </button>
                <button class="share-btn" onclick="showShareModal(event, '{channel['name']}', '{channel['url']}')" title="Partager">
                    <i class="fas fa-share-alt"></i>
                </button>
            </a>
        '''

    html_content += '''
            </div>
        </div>

        <!-- Modal Programme -->
        <div id="programModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <button onclick="closeModal()" class="close-modal">&times;</button>
                    <h2 id="modalTitle" style="margin: 0 auto;"></h2>
                    <button onclick="showAdminLogin()" class="edit-btn" title="Admin">
                        <i class="fas fa-lock" style="color: white;"></i>
                    </button>
                </div>

                <div id="programList" style="margin: 20px 0;"></div>

                <!-- Formulaire de connexion admin -->
                <div id="adminLoginForm" style="display: none; margin: 20px 0;">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px;">Mot de passe administrateur</label>
                        <input type="password" id="adminPassword" style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;">
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px;">
                        <button onclick="cancelAdminLogin()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); border: none; border-radius: 4px; color: white; cursor: pointer;">Annuler</button>
                        <button onclick="verifyAdminPassword()" style="padding: 8px 16px; background: #ff69b4; border: none; border-radius: 4px; color: white; cursor: pointer;">Connexion</button>
                    </div>
                </div>

                <!-- Boutons admin (visibles uniquement après authentification) -->
                <div id="adminControls" style="display: none; margin: 20px 0; text-align: right;">
                    <button onclick="showAddProgramForm()" style="padding: 8px 16px; background: #ff69b4; border: none; border-radius: 4px; color: white; cursor: pointer; margin-right: 10px;">
                        <i class="fas fa-plus"></i> Ajouter
                    </button>
                    <button onclick="adminLogout()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); border: none; border-radius: 4px; color: white; cursor: pointer;">
                        <i class="fas fa-sign-out-alt"></i> Déconnexion
                    </button>
                </div>

                <!-- Formulaire d'édition -->
                <form id="programEditForm" style="display: none;" onsubmit="saveProgram(event)">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px;">Heure</label>
                        <input type="time" id="programTime" required style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px;">Titre</label>
                        <input type="text" id="programTitle" required style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px;">Description</label>
                        <textarea id="programDescription" rows="3" style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;"></textarea>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px;">
                        <button type="button" onclick="toggleEditForm()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); border: none; border-radius: 4px; color: white; cursor: pointer;">Annuler</button>
                        <button type="submit" style="padding: 8px 16px; background: #ff69b4; border: none; border-radius: 4px; color: white; cursor: pointer;">Enregistrer</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal de partage -->
        <div id="shareModal" class="share-modal">
            <div class="share-modal-content">
                <div class="modal-header">
                    <button onclick="closeShareModal()" class="close-modal">&times;</button>
                    <h2 id="shareModalTitle" style="margin: 0 auto;">Partager</h2>
                </div>
                <div class="share-buttons">
                    <button onclick="shareOnFacebook()" class="social-share-btn facebook-btn">
                        <i class="fab fa-facebook-f"></i> Facebook
                    </button>
                    <button onclick="shareOnTwitter()" class="social-share-btn twitter-btn">
                        <i class="fab fa-twitter"></i> Twitter
                    </button>
                    <button onclick="shareOnWhatsApp()" class="social-share-btn whatsapp-btn">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </button>
                    <button onclick="shareOnTelegram()" class="social-share-btn telegram-btn">
                        <i class="fab fa-telegram-plane"></i> Telegram
                    </button>
                </div>
            </div>
        </div>

        <script>
            let currentChannel = null;
            let programs = [];
            let currentProgramIndex = null;
            let isAdmin = false;
            let currentShareUrl = '';
            let currentShareTitle = '';

            function displayPrograms() {
                const programList = document.getElementById('programList');
                programList.innerHTML = programs.map((program, index) => `
                    <div class="program-item" style="animation-delay: ${index * 0.1}s">
                        <div class="program-time">
                            <i class="far fa-clock"></i>
                            ${program.time}
                        </div>
                        <div class="program-title">${program.title}</div>
                        <div class="program-description">${program.description}</div>
                        ${isAdmin ? `
                        <div class="program-actions">
                            <button onclick="editProgram(${index})" class="program-action-btn" title="Modifier">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteProgram(${index})" class="program-action-btn" title="Supprimer">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ` : ''}
                    </div>
                `).join('');
            }

            function showProgram(event, channelName) {
                event.preventDefault();
                currentChannel = channelName;
                const modal = document.getElementById('programModal');
                const modalTitle = document.getElementById('modalTitle');
                
                modalTitle.textContent = channelName;
                modal.style.display = 'block';
                setTimeout(() => modal.classList.add('show'), 10);
                
                document.getElementById('programEditForm').style.display = 'none';
                document.getElementById('adminLoginForm').style.display = 'none';
                document.getElementById('adminControls').style.display = isAdmin ? 'block' : 'none';
                
                fetch(`/api/program/${encodeURIComponent(channelName)}`)
                    .then(response => response.json())
                    .then(data => {
                        programs = data;
                        displayPrograms();
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        document.getElementById('programList').innerHTML = 
                            '<div style="text-align: center; color: rgba(255,255,255,0.7);">Erreur lors du chargement du programme</div>';
                    });
            }

            function showAdminLogin() {
                if (!isAdmin) {
                    document.getElementById('adminLoginForm').style.display = 'block';
                    document.getElementById('adminPassword').value = '';
                    document.getElementById('adminPassword').focus();
                }
            }

            function cancelAdminLogin() {
                document.getElementById('adminLoginForm').style.display = 'none';
            }

            function verifyAdminPassword() {
                const password = document.getElementById('adminPassword').value;
                if (password === 'clientadmin') {
                    isAdmin = true;
                    document.getElementById('adminLoginForm').style.display = 'none';
                    document.getElementById('adminControls').style.display = 'block';
                    displayPrograms(); // Rafraîchir l'affichage pour montrer les boutons admin
                } else {
                    alert('Mot de passe incorrect');
                }
            }

            function adminLogout() {
                isAdmin = false;
                document.getElementById('adminControls').style.display = 'none';
                document.getElementById('programEditForm').style.display = 'none';
                displayPrograms(); // Rafraîchir l'affichage pour cacher les boutons admin
            }

            function showAddProgramForm() {
                if (!isAdmin) return;
                currentProgramIndex = null;
                document.getElementById('programTime').value = '';
                document.getElementById('programTitle').value = '';
                document.getElementById('programDescription').value = '';
                document.getElementById('programEditForm').style.display = 'block';
            }

            function toggleEditForm() {
                const form = document.getElementById('programEditForm');
                const isHidden = form.style.display === 'none';
                form.style.display = isHidden ? 'block' : 'none';
                
                if (isHidden) {
                    // Si on ouvre un nouveau formulaire
                    if (currentProgramIndex === null) {
                        document.getElementById('programActions').style.display = 'none';
                        document.getElementById('programTime').value = '';
                        document.getElementById('programTitle').value = '';
                        document.getElementById('programDescription').value = '';
                    }
                } else {
                    // Si on ferme le formulaire
                    currentProgramIndex = null;
                }
            }

            function editProgram(index) {
                currentProgramIndex = index;
                const program = programs[index];
                document.getElementById('programTime').value = program.time;
                document.getElementById('programTitle').value = program.title;
                document.getElementById('programDescription').value = program.description;
                document.getElementById('programActions').style.display = 'block';
                toggleEditForm();
            }

            function deleteProgram(index) {
                if (confirm('Voulez-vous vraiment supprimer ce programme ?')) {
                    try {
                        const response = fetch(`/api/program/${encodeURIComponent(currentChannel)}/${index}`, {
                            method: 'DELETE'
                        });
                        if (response.ok) {
                            programs.splice(index, 1);
                            displayPrograms();
                        }
                    } catch (error) {
                        alert('Erreur lors de la suppression');
                    }
                }
            }

            function saveProgram(event) {
                event.preventDefault();
                const time = document.getElementById('programTime').value;
                const title = document.getElementById('programTitle').value;
                const description = document.getElementById('programDescription').value;

                const newProgram = { time, title, description };

                if (currentProgramIndex !== null) {
                    // Modification d'un programme existant
                    programs[currentProgramIndex] = newProgram;
                } else {
                    // Ajout d'un nouveau programme
                    programs.push(newProgram);
                }

                programs.sort((a, b) => a.time.localeCompare(b.time));

                fetch(`/api/program/${encodeURIComponent(currentChannel)}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(programs)
                })
                .then(response => {
                    if (response.ok) {
                        displayPrograms();
                        toggleEditForm();
                        currentProgramIndex = null;
                    } else {
                        throw new Error('Erreur lors de la sauvegarde');
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    alert('Erreur lors de la sauvegarde');
                });
            }

            function closeModal() {
                const modal = document.getElementById('programModal');
                modal.classList.remove('show');
                setTimeout(() => {
                    modal.style.display = 'none';
                    document.getElementById('programEditForm').style.display = 'none';
                }, 300);
            }

            function showShareModal(event, channelName, channelUrl) {
                event.preventDefault();
                const shareModal = document.getElementById('shareModal');
                const shareModalTitle = document.getElementById('shareModalTitle');
                
                // Construire l'URL complète de partage
                const baseUrl = window.location.origin;
                currentShareUrl = `${baseUrl}/player?url=${encodeURIComponent(channelUrl)}&name=${encodeURIComponent(channelName)}`;
                currentShareTitle = `Regardez ${channelName} en direct sur PlayTV 4K!`;
                
                shareModalTitle.textContent = `Partager ${channelName}`;
                shareModal.style.display = 'block';
            }

            function closeShareModal() {
                document.getElementById('shareModal').style.display = 'none';
            }

            function shareOnFacebook() {
                const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentShareUrl)}`;
                window.open(url, '_blank');
            }

            function shareOnTwitter() {
                const url = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentShareUrl)}&text=${encodeURIComponent(currentShareTitle)}`;
                window.open(url, '_blank');
            }

            function shareOnWhatsApp() {
                const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(currentShareTitle + ' ' + currentShareUrl)}`;
                window.open(url, '_blank');
            }

            function shareOnTelegram() {
                const url = `https://t.me/share/url?url=${encodeURIComponent(currentShareUrl)}&text=${encodeURIComponent(currentShareTitle)}`;
                window.open(url, '_blank');
            }

            // Fermer le modal de partage si on clique en dehors
            window.onclick = function(event) {
                const shareModal = document.getElementById('shareModal');
                if (event.target == shareModal) {
                    shareModal.style.display = 'none';
                }
            };

            // Gestionnaire de recherche
            document.getElementById('searchInput').addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                const channels = document.querySelectorAll('.channel-item');
                channels.forEach(channel => {
                    const channelName = channel.querySelector('.channel-name').textContent.toLowerCase();
                    channel.style.display = channelName.includes(searchTerm) ? '' : 'none';
                });
            });
        </script>
    </body>
    </html>
    '''

    return html_content


@app.route('/player')
def player():
    return send_file('player.html')


@app.route('/api/program/<channel_name>', methods=['GET', 'POST'])
def channel_program(channel_name):
    if request.method == 'POST':
        programs = request.json
        channel_programs[channel_name] = programs
        return jsonify({"status": "success"})
    else:
        programs = get_program(channel_name)
        return jsonify(programs)


@app.route('/api/program/<channel_name>/<int:index>', methods=['DELETE'])
def delete_program(channel_name, index):
    try:
        if channel_name in channel_programs and 0 <= index < len(channel_programs[channel_name]):
            channel_programs[channel_name].pop(index)
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Programme non trouvé"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@socketio.on('join_channel')
def on_join(data):
    channel_url = data.get('channel_url')
    if channel_url:
        # Quitter le canal précédent si existe
        for room in viewers.keys():
            leave_room(room)

        # Rejoindre le nouveau canal
        join_room(channel_url)

        # Initialiser ou incrémenter le compteur
        if channel_url not in viewers:
            viewers[channel_url] = 0
        viewers[channel_url] += 1

        # Émettre la mise à jour vers tous les clients du canal
        emit('viewer_update', {'count': viewers[channel_url]},
             room=channel_url)


@socketio.on('leave_channel')
def on_leave(data):
    channel_url = data.get('channel_url')
    if channel_url and channel_url in viewers:
        leave_room(channel_url)
        viewers[channel_url] = max(0, viewers[channel_url] - 1)
        emit('viewer_update', {'count': viewers[channel_url]},
             room=channel_url)


@socketio.on('disconnect')
def on_disconnect():
    for channel_url in viewers.keys():
        if channel_url in viewers and viewers[channel_url] > 0:
            viewers[channel_url] = max(0, viewers[channel_url] - 1)
            emit('viewer_update', {'count': viewers[channel_url]},
                 room=channel_url)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
