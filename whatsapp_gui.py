import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import time
import random
from datetime import datetime
import pandas as pd
import pywhatkit as kit
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

class WhatsAppBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bulk Sender - Pro Edition")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f2f5")
        
        self.csv_path = None
        
        self.create_widgets()
        
        # Redirect stdout to the log widget
        sys.stdout = PrintLogger(self.log_text)
        
        print("🚀 Welcome to WhatsApp Bulk Sender GUI!")
        print("========================================")
        print("1. Select your Contacts CSV file.")
        print("2. Write your message template.")
        print("3. Click 'Start Automation' and relax!\n")

    def create_widgets(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#25D366", foreground="white", font=("Arial", 10, "bold"))
        style.map("TButton", background=[('active', '#128C7E')])
        style.configure("TLabel", background="#f0f2f5", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground="#075E54")
        
        # Main Frame
        main_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="WhatsApp Bulk Outreach Bot", style="Header.TLabel").pack(pady=(0, 15))
        
        # CSV Selection
        file_frame = tk.Frame(main_frame, bg="#f0f2f5")
        file_frame.pack(fill=tk.X, pady=5)
        self.file_label = ttk.Label(file_frame, text="No CSV Selected (Using Default: contacts.csv)")
        self.file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse CSV", command=self.browse_csv).pack(side=tk.RIGHT)
        
        # Message Template
        ttk.Label(main_frame, text="Message Template (Use {name} and {business} for dynamic text):").pack(anchor=tk.W, pady=(15, 5))
        self.msg_text = tk.Text(main_frame, height=8, font=("Arial", 10), wrap=tk.WORD, bd=1, relief="solid")
        self.msg_text.pack(fill=tk.X)
        default_msg = "Assalam o Alaikum {name} bhai! 👋\n\nMain [Tumhara Naam] bol raha hoon.\n\nAgar interest ho toh reply karen, baat karte hain! 🙏"
        self.msg_text.insert(tk.END, default_msg)
        
        # Delay Settings
        delay_frame = tk.Frame(main_frame, bg="#f0f2f5")
        delay_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(delay_frame, text="Min Delay (sec):").pack(side=tk.LEFT)
        self.min_delay = ttk.Entry(delay_frame, width=8)
        self.min_delay.insert(0, "25")
        self.min_delay.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(delay_frame, text="Max Delay (sec):").pack(side=tk.LEFT)
        self.max_delay = ttk.Entry(delay_frame, width=8)
        self.max_delay.insert(0, "45")
        self.max_delay.pack(side=tk.LEFT, padx=5)
        
        # Start Button
        self.start_btn = ttk.Button(main_frame, text="🚀 START AUTOMATION", command=self.start_thread)
        self.start_btn.pack(fill=tk.X, pady=15, ipady=5)
        
        # Logs
        ttk.Label(main_frame, text="Activity Logs:").pack(anchor=tk.W)
        self.log_text = tk.Text(main_frame, height=12, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9), bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Fallback to local contacts.csv if exists
        if os.path.exists("contacts.csv"):
            self.csv_path = "contacts.csv"
            self.file_label.config(text="Selected: contacts.csv")

    def browse_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.csv_path = filepath
            self.file_label.config(text=f"Selected: {os.path.basename(filepath)}")

    def start_thread(self):
        if not self.csv_path or not os.path.exists(self.csv_path):
            messagebox.showerror("Error", "Please select a valid CSV file first!")
            return
            
        self.start_btn.config(state=tk.DISABLED, text="⏳ RUNNING...")
        threading.Thread(target=self.run_automation, daemon=True).start()

    def get_send_time(self, index, delay_avg=35):
        now = datetime.now()
        total_seconds = (index * delay_avg) + 60  # start 1 min from now
        total_minutes = now.minute + (total_seconds // 60)
        
        hour = now.hour + (total_minutes // 60)
        minute = total_minutes % 60
        hour = hour % 24
        
        return int(hour), int(minute)

    def run_automation(self):
        try:
            df = pd.read_csv(self.csv_path)
            template = self.msg_text.get("1.0", tk.END).strip()
            min_d = int(self.min_delay.get())
            max_d = int(self.max_delay.get())
            
            total = len(df)
            success = 0
            failed = 0
            
            print(f"\n[INFO] Loaded {total} contacts.")
            print("[INFO] Please ensure WhatsApp Web is logged in your browser!")
            time.sleep(3)
            
            for index, row in df.iterrows():
                number = str(row.get('number', '')).strip()
                name = str(row.get('name', '')).strip()
                business = str(row.get('business', '')).strip()
                
                if not number.startswith('+'):
                    print(f"⚠️ Skipped {name} - Invalid Number: {number}")
                    failed += 1
                    continue
                
                message = template.replace("{name}", name).replace("{business}", business)
                
                hour, minute = self.get_send_time(index, delay_avg=(min_d+max_d)//2)
                
                print(f"📤 Sending to {name} ({number}) at {hour}:{minute:02d}...")
                
                try:
                    # pywhatkit needs at least 1-2 mins in the future.
                    kit.sendwhatmsg(
                        number,
                        message,
                        hour,
                        minute,
                        wait_time=20,
                        tab_close=True,
                        close_time=3
                    )
                    success += 1
                    print("✅ Message Sent!")
                    
                    delay = random.randint(min_d, max_d)
                    print(f"⏳ Waiting {delay} seconds before next...\n")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ Failed to send: {str(e)}")
                    failed += 1
                    time.sleep(5)
            
            print("\n🎉 ================= REPORT =================")
            print(f"Total Sent Successfully: {success}")
            print(f"Total Failed: {failed}")
            print("===========================================")
            messagebox.showinfo("Complete", f"Automation Completed!\nSent: {success}\nFailed: {failed}")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.start_btn.config(state=tk.NORMAL, text="🚀 START AUTOMATION")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppBotGUI(root)
    root.mainloop()
