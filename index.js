const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.static('public'));
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

let qrCodeData = null;
let isReady = false;

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('QR RECEIVED', qr);
    qrCodeData = qr;
});

client.on('ready', () => {
    console.log('Client is ready!');
    isReady = true;
    qrCodeData = null;
});

client.on('disconnected', () => {
    console.log('Client disconnected!');
    isReady = false;
});

client.initialize();

app.get('/api/status', (req, res) => {
    res.json({ isReady, qrCodeData });
});

app.post('/api/send', upload.single('csvFile'), async (req, res) => {
    if (!isReady) {
        return res.status(400).json({ error: 'WhatsApp client is not ready. Please scan QR first.' });
    }

    const { template, minDelay, maxDelay } = req.body;
    const file = req.file;

    if (!file) {
        return res.status(400).json({ error: 'CSV file is required.' });
    }

    const contacts = [];
    fs.createReadStream(file.path)
        .pipe(csv())
        .on('data', (row) => contacts.push(row))
        .on('end', async () => {
            res.json({ message: 'Automation started in the background.', total: contacts.length });
            
            // Background sending process
            for (let i = 0; i < contacts.length; i++) {
                const row = contacts[i];
                let number = row.number ? row.number.trim() : '';
                const name = row.name ? row.name.trim() : '';
                const business = row.business ? row.business.trim() : '';

                if (number) {
                    if (number.startsWith('+')) {
                        number = number.replace('+', '') + '@c.us';
                    } else {
                        number = number + '@c.us';
                    }

                    const message = template.replace('{name}', name).replace('{business}', business);
                    
                    try {
                        await client.sendMessage(number, message);
                        console.log(`Sent to ${name} (${number})`);
                    } catch (error) {
                        console.error(`Failed to send to ${name}:`, error);
                    }
                }

                // Random delay
                const delay = Math.floor(Math.random() * (parseInt(maxDelay) - parseInt(minDelay) + 1) + parseInt(minDelay)) * 1000;
                await new Promise(r => setTimeout(r, delay));
            }
            console.log('Bulk sending completed!');
            fs.unlinkSync(file.path); // Clean up
        });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
