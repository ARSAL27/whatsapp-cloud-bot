const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const { IgApiClient } = require('instagram-private-api');
const qrcode = require('qrcode');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const cors = require('cors');
const path = require('path');

const app = express();
const port = process.env.PORT || 7860;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const upload = multer({ dest: 'uploads/' });

// --- WHATSAPP SETUP ---
let qrCodeData = '';
let waStatus = 'Disconnected';

const waClient = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { 
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null,
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    }
});

waClient.on('qr', (qr) => {
    qrCodeData = qr;
    waStatus = 'Scan Required';
});

waClient.on('ready', () => {
    waStatus = 'Connected';
    qrCodeData = '';
});

waClient.initialize();

// --- INSTAGRAM SETUP ---
const ig = new IgApiClient();
let igStatus = 'Not Logged In';
let igUser = null;

// --- API ROUTES ---

// WhatsApp Status
app.get('/api/wa/status', (req, res) => {
    res.json({ status: waStatus, qr: qrCodeData });
});

// Instagram Login
app.post('/api/ig/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        ig.state.generateDevice(username);
        const auth = await ig.account.login(username, password);
        igUser = auth;
        igStatus = `Logged in as ${username}`;
        res.json({ success: true, user: username });
    } catch (err) {
        res.status(400).json({ success: false, error: err.message });
    }
});

app.get('/api/ig/status', (req, res) => {
    res.json({ status: igStatus });
});

// Sending Logic
app.post('/api/send', upload.single('csv'), (req, res) => {
    const { platform, template, minDelay, maxDelay } = req.body;
    const results = [];
    const filePath = req.file.path;

    fs.createReadStream(filePath)
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', async () => {
            res.json({ success: true, message: `Starting ${platform} automation for ${results.length} contacts.` });
            
            for (let i = 0; i < results.length; i++) {
                const contact = results[i];
                let msg = template;
                
                // Dynamic replacement
                Object.keys(contact).forEach(key => {
                    msg = msg.replace(new RegExp(`{${key}}`, 'g'), contact[key]);
                });

                try {
                    if (platform === 'whatsapp' && waStatus === 'Connected') {
                        const number = contact.Phone || contact.number;
                        const finalNum = number.includes('@c.us') ? number : `${number.replace('+', '')}@c.us`;
                        await waClient.sendMessage(finalNum, msg);
                    } else if (platform === 'instagram' && igUser) {
                        const targetUser = contact['Instagram Username'] || contact.username;
                        const userId = await ig.user.getIdByUsername(targetUser.replace('@', ''));
                        await ig.direct.sendText(userId, msg);
                    }
                } catch (err) {
                    console.error(`Error sending to ${contact.name || contact['Doctor Name']}:`, err.message);
                }

                const delay = Math.floor(Math.random() * (maxDelay - minDelay + 1) + parseInt(minDelay));
                await new Promise(resolve => setTimeout(resolve, delay * 1000));
            }
            fs.unlinkSync(filePath);
        });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
