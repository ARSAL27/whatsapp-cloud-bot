import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import time
import random
import pandas as pd
from instagrapi import Client
import os

class PrintLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Bulk Sender (Risky!)")
        self.root.geometry("600x800")
        self.root.configure(bg="#fdfdfd")
        
        self.csv_path = None
        self.cl = Client()
        
        self.create_widgets()
        sys.stdout = PrintLogger(self.log_text)
        
        print("🚀 Welcome to Instagram Outreach Bot!")
        print("⚠️ WARNING: Use an EXTRA/FAKE account.")
        print("⚠️ If you send too many DMs, Instagram WILL ban you.\n")

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#E1306C", foreground="white", font=("Arial", 10, "bold"))
        style.map("TButton", background=[('active', '#C13584')])
        style.configure("TLabel", background="#fdfdfd", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground="#E1306C")
        
        main_frame = tk.Frame(self.root, bg="#fdfdfd", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Instagram Auto DM Bot", style="Header.TLabel").pack(pady=(0, 15))
        
        # Login Details
        login_frame = tk.LabelFrame(main_frame, text="Login Details (Use Fake Account)", bg="#fdfdfd", padx=10, pady=10)
        login_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky="w")
        self.ig_user = ttk.Entry(login_frame, width=25)
        self.ig_user.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.ig_pass = ttk.Entry(login_frame, show="*", width=25)
        self.ig_pass.grid(row=0, column=3, padx=5, pady=5)
        
        # CSV Selection
        file_frame = tk.Frame(main_frame, bg="#fdfdfd")
        file_frame.pack(fill=tk.X, pady=10)
        self.file_label = ttk.Label(file_frame, text="No CSV Selected (Need: username, name, business)")
        self.file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse CSV", command=self.browse_csv).pack(side=tk.RIGHT)
        
        # Message Template
        ttk.Label(main_frame, text="Message Template ({name} and {business}):").pack(anchor=tk.W, pady=(15, 5))
        self.msg_text = tk.Text(main_frame, height=6, font=("Arial", 10), wrap=tk.WORD, bd=1, relief="solid")
        self.msg_text.pack(fill=tk.X)
        default_msg = "Hi {name}! Saw your work at {business}."
        self.msg_text.insert(tk.END, default_msg)
        
        # Delay Settings
        delay_frame = tk.Frame(main_frame, bg="#fdfdfd")
        delay_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(delay_frame, text="Min Delay (sec):").pack(side=tk.LEFT)
        self.min_delay = ttk.Entry(delay_frame, width=8)
        self.min_delay.insert(0, "300") # 5 mins
        self.min_delay.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(delay_frame, text="Max Delay (sec):").pack(side=tk.LEFT)
        self.max_delay = ttk.Entry(delay_frame, width=8)
        self.max_delay.insert(0, "600") # 10 mins
        self.max_delay.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(delay_frame, text="⚠️ Keep delays HIGH (300-600) to avoid bans", foreground="red").pack(side=tk.LEFT, padx=10)
        
        # Start Button
        self.start_btn = ttk.Button(main_frame, text="🚀 LOGIN & START SENDING", command=self.start_thread)
        self.start_btn.pack(fill=tk.X, pady=15, ipady=5)
        
        # Logs
        ttk.Label(main_frame, text="Activity Logs:").pack(anchor=tk.W)
        self.log_text = tk.Text(main_frame, height=12, bg="#1e1e1e", fg="#ffcc00", font=("Consolas", 9), bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if os.path.exists("ig_contacts.csv"):
            self.csv_path = "ig_contacts.csv"
            self.file_label.config(text="Selected: ig_contacts.csv")

    def browse_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.csv_path = filepath
            self.file_label.config(text=f"Selected: {os.path.basename(filepath)}")

    def start_thread(self):
        if not self.csv_path or not os.path.exists(self.csv_path):
            messagebox.showerror("Error", "Please select a valid CSV file first!")
            return
        if not self.ig_user.get() or not self.ig_pass.get():
            messagebox.showerror("Error", "Please enter Instagram Username and Password!")
            return
            
        self.start_btn.config(state=tk.DISABLED, text="⏳ RUNNING...")
        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        try:
            username = self.ig_user.get()
            password = self.ig_pass.get()
            
            print(f"🔄 Logging into Instagram as {username}...")
            # We delay login slightly to mimic human
            time.sleep(2)
            self.cl.login(username, password)
            print("✅ Login Successful!")
            
            df = pd.read_csv(self.csv_path)
            template = self.msg_text.get("1.0", tk.END).strip()
            min_d = int(self.min_delay.get())
            max_d = int(self.max_delay.get())
            
            total = len(df)
            success = 0
            failed = 0
            
            print(f"\n[INFO] Loaded {total} target users.")
            
            for index, row in df.iterrows():
                target_user = str(row.get('username', '')).strip().replace('@', '')
                name = str(row.get('name', '')).strip()
                business = str(row.get('business', '')).strip()
                
                if not target_user:
                    continue
                
                message = template.replace("{name}", name).replace("{business}", business)
                
                print(f"📤 Finding user ID for @{target_user}...")
                try:
                    user_id = self.cl.user_id_from_username(target_user)
                    print(f"   -> Found ID: {user_id}. Sending DM...")
                    
                    self.cl.direct_send(message, user_ids=[user_id])
                    success += 1
                    print("    ✅ Message Sent!")
                    
                    delay = random.randint(min_d, max_d)
                    print(f"⏳ Waiting {delay} seconds before next (Anti-Ban)...\n")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"    ❌ Failed: {str(e)}")
                    failed += 1
                    time.sleep(15)
            
            print("\n🎉 ================= REPORT =================")
            print(f"Total Sent Successfully: {success}")
            print(f"Total Failed: {failed}")
            print("===========================================")
            messagebox.showinfo("Complete", f"Instagram Automation Completed!\nSent: {success}\nFailed: {failed}")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Error", f"Failed: {str(e)}\n\nIf it says Challenge Required, you need to login on your phone and approve it.")
        finally:
            self.start_btn.config(state=tk.NORMAL, text="🚀 LOGIN & START SENDING")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramBotGUI(root)
    root.mainloop()
