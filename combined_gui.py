import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import random
from datetime import datetime
import pandas as pd
import pywhatkit as kit
from instagrapi import Client
import os
import json

TRACKING_FILE = "bot_tracking.json"
IG_SESSION_FILE = "ig_session.json"
SETTINGS_FILE = "settings.json"

import uuid
import tkinter.simpledialog as simpledialog

ALLOWED_PC_ID = 53132166905220

class CombinedBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Hide root temporarily
        
        # Security Checks (Hardware Lock)
        if uuid.getnode() != ALLOWED_PC_ID:
            messagebox.showerror("Unauthorized Device", "This software is licensed only for the original computer.\nContact the developer.")
            self.root.destroy()
            sys.exit()
            
        # Password Check
        pwd = simpledialog.askstring("Security Check", "Enter Master Password to access bot:", show='*')
        if pwd != "arsal123":
            messagebox.showerror("Access Denied", "Incorrect Password!")
            self.root.destroy()
            sys.exit()

        self.root.deiconify() # Show root again
        self.root.title("Ultimate Outreach Bot (Pro Edition)")
        self.root.geometry("700x850")
        self.root.configure(bg="#fdfdfd")
        
        self.wa_csv_path = None
        self.ig_csv_path = None
        self.ig_client = Client()
        
        self.tracking = self.load_tracking()
        self.settings = self.load_settings()
        
        self.create_widgets()
        
        self.log_wa("🚀 Welcome to WhatsApp Bulk Sender!\nℹ️ Daily Limit: 5 messages (Safe Mode)\n")
        self.log_ig("🚀 Welcome to Instagram Auto DM Bot!\nℹ️ Daily Limit: 10 messages (Safe Mode)\n")

    def load_tracking(self):
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, 'r') as f:
                return json.load(f)
        return {
            "whatsapp": {"date": "", "sent_today": 0, "processed": []},
            "instagram": {"date": "", "sent_today": 0, "processed": []}
        }

    def save_tracking(self):
        with open(TRACKING_FILE, 'w') as f:
            json.dump(self.tracking, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def check_daily_limit(self, platform, limit):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.tracking[platform]["date"] != today:
            self.tracking[platform]["date"] = today
            self.tracking[platform]["sent_today"] = 0
            self.save_tracking()
            
        if self.tracking[platform]["sent_today"] >= limit:
            return False
        return True

    def log_wa(self, msg):
        self.wa_log_text.insert(tk.END, msg + "\n")
        self.wa_log_text.see(tk.END)
        self.wa_log_text.update_idletasks()

    def log_ig(self, msg):
        self.ig_log_text.insert(tk.END, msg + "\n")
        self.ig_log_text.see(tk.END)
        self.ig_log_text.update_idletasks()

    def countdown_sleep(self, seconds, status_label):
        for i in range(seconds, 0, -1):
            status_label.config(text=f"⏳ Waiting: {i} seconds remaining...")
            time.sleep(1)
        status_label.config(text="Status: Sending Next...")

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.wa_frame = ttk.Frame(notebook)
        notebook.add(self.wa_frame, text="🟢 WhatsApp Bot")
        self.create_whatsapp_tab()
        
        self.ig_frame = ttk.Frame(notebook)
        notebook.add(self.ig_frame, text="🟣 Instagram Bot")
        self.create_instagram_tab()

    def create_whatsapp_tab(self):
        main_frame = tk.Frame(self.wa_frame, bg="#fdfdfd", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        file_frame = tk.Frame(main_frame, bg="#fdfdfd")
        file_frame.pack(fill=tk.X, pady=5)
        self.wa_file_label = ttk.Label(file_frame, text="No CSV Selected")
        self.wa_file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse CSV", command=self.browse_wa_csv).pack(side=tk.RIGHT)
        
        ttk.Label(main_frame, text="Message Template (e.g. {Doctor Name}, {City}):").pack(anchor=tk.W, pady=(15, 5))
        self.wa_msg_text = tk.Text(main_frame, height=6, font=("Arial", 10), wrap=tk.WORD, bd=1, relief="solid")
        self.wa_msg_text.pack(fill=tk.X)
        self.wa_msg_text.insert(tk.END, "Assalam o Alaikum {name} bhai! 👋\n\nMain [Tumhara Naam] bol raha hoon.\n\nAgar interest ho toh reply karen! 🙏")
        
        delay_frame = tk.Frame(main_frame, bg="#fdfdfd")
        delay_frame.pack(fill=tk.X, pady=15)
        ttk.Label(delay_frame, text="Min Delay (sec):").pack(side=tk.LEFT)
        self.wa_min_delay = ttk.Entry(delay_frame, width=8)
        self.wa_min_delay.insert(0, "45")
        self.wa_min_delay.pack(side=tk.LEFT, padx=(5, 20))
        ttk.Label(delay_frame, text="Max Delay (sec):").pack(side=tk.LEFT)
        self.wa_max_delay = ttk.Entry(delay_frame, width=8)
        self.wa_max_delay.insert(0, "90")
        self.wa_max_delay.pack(side=tk.LEFT, padx=5)
        
        self.wa_status_label = ttk.Label(main_frame, text="Status: Ready", font=("Arial", 11, "bold"), foreground="#25D366")
        self.wa_status_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.wa_start_btn = tk.Button(main_frame, text="🚀 START WHATSAPP AUTOMATION", bg="#25D366", fg="white", font=("Arial", 10, "bold"), command=self.start_wa_thread)
        self.wa_start_btn.pack(fill=tk.X, pady=10, ipady=5)
        
        ttk.Label(main_frame, text="WhatsApp Logs:").pack(anchor=tk.W)
        self.wa_log_text = tk.Text(main_frame, height=12, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9), bd=0)
        self.wa_log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if os.path.exists("contacts.csv"):
            self.wa_csv_path = "contacts.csv"
            self.wa_file_label.config(text="Selected: contacts.csv")

    def create_instagram_tab(self):
        main_frame = tk.Frame(self.ig_frame, bg="#fdfdfd", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        login_frame = tk.LabelFrame(main_frame, text="Login Details (Saved Automatically)", bg="#fdfdfd", padx=10, pady=10)
        login_frame.pack(fill=tk.X, pady=5)
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky="w")
        self.ig_user = ttk.Entry(login_frame, width=20)
        self.ig_user.insert(0, self.settings.get("ig_username", ""))
        self.ig_user.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(login_frame, text="Password:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.ig_pass = ttk.Entry(login_frame, show="*", width=20)
        self.ig_pass.insert(0, self.settings.get("ig_password", ""))
        self.ig_pass.grid(row=0, column=3, padx=5, pady=5)
        
        file_frame = tk.Frame(main_frame, bg="#fdfdfd")
        file_frame.pack(fill=tk.X, pady=10)
        self.ig_file_label = ttk.Label(file_frame, text="No CSV Selected")
        self.ig_file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse CSV", command=self.browse_ig_csv).pack(side=tk.RIGHT)
        
        ttk.Label(main_frame, text="Message Template (e.g. {Doctor Name}, {City}):").pack(anchor=tk.W, pady=(15, 5))
        self.ig_msg_text = tk.Text(main_frame, height=5, font=("Arial", 10), wrap=tk.WORD, bd=1, relief="solid")
        self.ig_msg_text.pack(fill=tk.X)
        self.ig_msg_text.insert(tk.END, "Hi {name}! Saw your work at {business}.")
        
        delay_frame = tk.Frame(main_frame, bg="#fdfdfd")
        delay_frame.pack(fill=tk.X, pady=10)
        ttk.Label(delay_frame, text="Min Delay:").pack(side=tk.LEFT)
        self.ig_min_delay = ttk.Entry(delay_frame, width=8)
        self.ig_min_delay.insert(0, "300")
        self.ig_min_delay.pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(delay_frame, text="Max Delay:").pack(side=tk.LEFT)
        self.ig_max_delay = ttk.Entry(delay_frame, width=8)
        self.ig_max_delay.insert(0, "600")
        self.ig_max_delay.pack(side=tk.LEFT, padx=5)
        
        self.ig_status_label = ttk.Label(main_frame, text="Status: Ready", font=("Arial", 11, "bold"), foreground="#E1306C")
        self.ig_status_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.ig_start_btn = tk.Button(main_frame, text="🚀 START INSTAGRAM", bg="#E1306C", fg="white", font=("Arial", 10, "bold"), command=self.start_ig_thread)
        self.ig_start_btn.pack(fill=tk.X, pady=10, ipady=5)
        
        ttk.Label(main_frame, text="Instagram Logs:").pack(anchor=tk.W)
        self.ig_log_text = tk.Text(main_frame, height=10, bg="#1e1e1e", fg="#ffcc00", font=("Consolas", 9), bd=0)
        self.ig_log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if os.path.exists("ig_contacts.csv"):
            self.ig_csv_path = "ig_contacts.csv"
            self.ig_file_label.config(text="Selected: ig_contacts.csv")

    def browse_wa_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.wa_csv_path = filepath
            self.wa_file_label.config(text=f"Selected: {os.path.basename(filepath)}")

    def browse_ig_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.ig_csv_path = filepath
            self.ig_file_label.config(text=f"Selected: {os.path.basename(filepath)}")

    def start_wa_thread(self):
        if not self.wa_csv_path:
            messagebox.showerror("Error", "Please select WhatsApp CSV file first!")
            return
        self.wa_start_btn.config(state=tk.DISABLED, text="⏳ RUNNING...")
        threading.Thread(target=self.run_wa, daemon=True).start()

    def start_ig_thread(self):
        if not self.ig_csv_path:
            messagebox.showerror("Error", "Please select Instagram CSV file first!")
            return
        if not self.ig_user.get() or not self.ig_pass.get():
            messagebox.showerror("Error", "Please enter Instagram Username and Password!")
            return
        self.ig_start_btn.config(state=tk.DISABLED, text="⏳ RUNNING...")
        threading.Thread(target=self.run_ig, daemon=True).start()

    def run_wa(self):
        try:
            df = pd.read_csv(self.wa_csv_path)
            template = self.wa_msg_text.get("1.0", tk.END).strip()
            min_d = int(self.wa_min_delay.get())
            max_d = int(self.wa_max_delay.get())
            
            # Check limits before starting loop
            if not self.check_daily_limit("whatsapp", 5):
                self.wa_status_label.config(text="Status: Limit Reached for Today")
                self.log_wa("🛑 Daily limit of 5 WhatsApp messages reached! Come back tomorrow.")
                return

            self.log_wa(f"[INFO] Scanning {len(df)} contacts in CSV...")
            time.sleep(1)
            
            messages_sent_run = 0

            for index, row in df.iterrows():
                if not self.check_daily_limit("whatsapp", 5):
                    self.log_wa("🛑 Daily limit (5) reached during sending. Pausing until tomorrow.")
                    break

                # Support both old column names and new doctor format
                number = str(row.get('Phone', row.get('number', ''))).strip()
                name = str(row.get('Doctor Name', row.get('name', ''))).strip()
                
                if not number.startswith('+'):
                    continue
                
                # Check if already processed
                if number in self.tracking["whatsapp"]["processed"]:
                    self.log_wa(f"⏭️ Skipping {name} ({number}) - Already sent before.")
                    continue
                
                # Dynamic Template Replacement
                msg = template
                for col in df.columns:
                    msg = msg.replace(f"{{{col}}}", str(row[col]).strip())
                
                now = datetime.now()
                total_seconds = (messages_sent_run * ((min_d+max_d)//2)) + 60
                total_minutes = now.minute + (total_seconds // 60)
                hour = (now.hour + (total_minutes // 60)) % 24
                minute = total_minutes % 60
                
                self.wa_status_label.config(text=f"Status: Sending to {name}...")
                self.log_wa(f"📤 Sending to {name} ({number}) at {hour}:{minute:02d}...")
                
                try:
                    kit.sendwhatmsg(number, msg, hour, int(minute), wait_time=20, tab_close=True, close_time=3)
                    self.log_wa("✅ Message Sent!")
                    
                    # Mark as processed and save
                    self.tracking["whatsapp"]["processed"].append(number)
                    self.tracking["whatsapp"]["sent_today"] += 1
                    self.save_tracking()
                    messages_sent_run += 1
                    
                    if self.check_daily_limit("whatsapp", 5):
                        delay = random.randint(min_d, max_d)
                        self.countdown_sleep(delay, self.wa_status_label)
                except Exception as e:
                    self.log_wa(f"❌ Failed to send to {number}: {e}")
            
            self.wa_status_label.config(text="Status: Done for now.")
            self.log_wa("\n🎉 PROCESS COMPLETE OR LIMIT REACHED!")
            messagebox.showinfo("Complete", f"WhatsApp Run Done!\nSent in this run: {messages_sent_run}")
        except Exception as e:
            self.log_wa(f"❌ ERROR: {e}")
        finally:
            self.wa_start_btn.config(state=tk.NORMAL, text="🚀 START WHATSAPP AUTOMATION")

    def run_ig(self):
        try:
            username = self.ig_user.get()
            password = self.ig_pass.get()
            
            # Save credentials for next time
            self.settings["ig_username"] = username
            self.settings["ig_password"] = password
            self.save_settings()
            
            self.ig_status_label.config(text="Status: Logging in...")
            self.log_ig(f"🔄 Logging into @{username}...")
            
            # Load session if exists to avoid 2FA/suspicion
            if os.path.exists(IG_SESSION_FILE):
                self.ig_client.load_settings(IG_SESSION_FILE)
            
            self.ig_client.login(username, password)
            self.ig_client.dump_settings(IG_SESSION_FILE) # Save updated session
            self.log_ig("✅ Login Successful!")
            
            df = pd.read_csv(self.ig_csv_path)
            template = self.ig_msg_text.get("1.0", tk.END).strip()
            min_d = int(self.ig_min_delay.get())
            max_d = int(self.ig_max_delay.get())
            
            if not self.check_daily_limit("instagram", 10):
                self.ig_status_label.config(text="Status: Limit Reached for Today")
                self.log_ig("🛑 Daily limit of 10 Instagram messages reached! Come back tomorrow.")
                return

            self.log_ig(f"[INFO] Scanning {len(df)} target users...")
            
            messages_sent_run = 0

            for index, row in df.iterrows():
                if not self.check_daily_limit("instagram", 10):
                    self.log_ig("🛑 Daily limit (10) reached during sending. Pausing until tomorrow.")
                    break

                # Support both old column names and new doctor format
                target = str(row.get('Instagram Username', row.get('username', ''))).strip().replace('@', '')
                name = str(row.get('Doctor Name', row.get('name', ''))).strip()
                
                if not target: continue
                
                # Check if already processed
                if target in self.tracking["instagram"]["processed"]:
                    self.log_ig(f"⏭️ Skipping @{target} - Already sent before.")
                    continue
                
                # Dynamic Template Replacement
                msg = template
                for col in df.columns:
                    msg = msg.replace(f"{{{col}}}", str(row[col]).strip())
                self.ig_status_label.config(text=f"Status: Finding ID for @{target}...")
                
                try:
                    user_id = self.ig_client.user_id_from_username(target)
                    self.log_ig(f"📤 Found ID for @{target}. Sending DM...")
                    self.ig_status_label.config(text=f"Status: Sending DM to @{target}...")
                    
                    self.ig_client.direct_send(msg, user_ids=[user_id])
                    self.log_ig("    ✅ Message Sent!")
                    
                    # Mark as processed
                    self.tracking["instagram"]["processed"].append(target)
                    self.tracking["instagram"]["sent_today"] += 1
                    self.save_tracking()
                    messages_sent_run += 1
                    
                    if self.check_daily_limit("instagram", 10):
                        delay = random.randint(min_d, max_d)
                        self.countdown_sleep(delay, self.ig_status_label)
                except Exception as e:
                    self.log_ig(f"    ❌ Failed: {e}")
                    self.countdown_sleep(15, self.ig_status_label) # Short delay on fail
            
            self.ig_status_label.config(text="Status: Done for now.")
            self.log_ig("\n🎉 PROCESS COMPLETE OR LIMIT REACHED!")
            messagebox.showinfo("Complete", f"Instagram Run Done!\nSent in this run: {messages_sent_run}")
        except Exception as e:
            self.log_ig(f"❌ ERROR: {e}")
            self.ig_status_label.config(text="Status: Error")
        finally:
            self.ig_start_btn.config(state=tk.NORMAL, text="🚀 START INSTAGRAM")

if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedBotGUI(root)
    root.mainloop()
