import pywhatkit as kit
import pandas as pd
import time
import random
from datetime import datetime

# ============================================
#   SETTINGS - Yahan apni cheezein daalo
# ============================================

CSV_FILE = "contacts.csv"          # Tumhara contacts file name

DELAY_MIN = 25    # Min seconds wait between messages (kam mat karo)
DELAY_MAX = 45    # Max seconds wait between messages

START_HOUR = 10   # Kitne baje se start karo (24hr format)
START_MINUTE = 0  # Kitne minute se start

# ============================================
#   MESSAGE TEMPLATE - Customize karo
# ============================================

def create_message(name, business=""):
    """
    {name} = contact ka naam automatically aayega
    {business} = unka business naam (agar CSV mein ho)
    """
    message = f"""Assalam o Alaikum {name} bhai! 👋

Main [Tumhara Naam] bol raha hoon — [Tumhara Kaam/Business].

[Yahan apna offer likho — 2-3 lines mein]

Agar interest ho toh reply karen, baat karte hain! 🙏"""
    
    return message

# ============================================
#   MAIN SCRIPT - Yahan se kuch mat badlo
# ============================================

def load_contacts(file):
    """CSV se contacts load karo"""
    try:
        df = pd.read_csv(file)
        print(f"✅ {len(df)} contacts load ho gaye!\n")
        return df
    except FileNotFoundError:
        print(f"❌ ERROR: '{file}' nahi mila!")
        print("contacts.csv banao — format neeche diya hai\n")
        create_sample_csv()
        return None

def create_sample_csv():
    """Sample CSV banata hai agar file nahi ho"""
    sample = pd.DataFrame({
        'number': ['+923001234567', '+923111234567'],
        'name': ['Ahmed Bhai', 'Sara Aapi'],
        'business': ['Kapra Store', 'Food Business']
    })
    sample.to_csv('contacts_sample.csv', index=False)
    print("✅ 'contacts_sample.csv' ban gaya — isko dekho aur apna data daalo")

def get_send_time(index, start_hour, start_minute, delay_avg=35):
    """Har message ke liye alag time calculate karo"""
    total_seconds = index * delay_avg
    total_minutes = start_minute + (total_seconds // 60)
    
    hour = start_hour + (total_minutes // 60)
    minute = total_minutes % 60
    
    # Agar 24 se zyada ho jaye
    hour = hour % 24
    
    return int(hour), int(minute)

def send_messages(df):
    """Sab contacts ko messages bhejo"""
    
    total = len(df)
    success = 0
    failed = 0
    failed_numbers = []
    
    print("=" * 45)
    print(f"  STARTING: {total} messages bhejne hain")
    print(f"  Time: {START_HOUR}:{START_MINUTE:02d} se start")
    print("=" * 45)
    print("\n⚠️  Browser mein WhatsApp Web scan kar lo abhi!\n")
    time.sleep(5)
    
    for index, row in df.iterrows():
        
        number = str(row['number']).strip()
        name = str(row['name']).strip()
        business = str(row.get('business', '')).strip()
        
        # Number validation
        if not number.startswith('+'):
            print(f"⚠️  Skipping {name} — number mein + nahi hai: {number}")
            failed += 1
            failed_numbers.append(number)
            continue
        
        # Message banao
        message = create_message(name, business)
        
        # Time calculate karo
        hour, minute = get_send_time(index, START_HOUR, START_MINUTE)
        
        print(f"📤 [{index+1}/{total}] Bhej raha hoon → {name} ({number})")
        print(f"    Time: {hour}:{minute:02d}")
        
        try:
            kit.sendwhatmsg(
                number,
                message,
                hour,
                minute,
                wait_time=20,        # WhatsApp Web load hone ka wait
                tab_close=True,      # Tab band kar do baad mein
                close_time=3
            )
            
            success += 1
            print(f"    ✅ Sent!\n")
            
            # Random delay — ban se bachao
            delay = random.randint(DELAY_MIN, DELAY_MAX)
            print(f"    ⏳ {delay} seconds wait kar raha hoon...\n")
            time.sleep(delay)
            
        except Exception as e:
            failed += 1
            failed_numbers.append(number)
            print(f"    ❌ Failed: {e}\n")
            time.sleep(10)
    
    # Final Report
    print("\n" + "=" * 45)
    print("  COMPLETE REPORT")
    print("=" * 45)
    print(f"  ✅ Successfully bheje: {success}")
    print(f"  ❌ Failed:            {failed}")
    print(f"  📊 Total:             {total}")
    
    if failed_numbers:
        print(f"\n  Failed Numbers:")
        for num in failed_numbers:
            print(f"    - {num}")
    
    print("\n  Done! 🎉")

# ============================================
#   RUN KARO
# ============================================

if __name__ == "__main__":
    
    print("\n" + "=" * 45)
    print("  WhatsApp Bulk Sender — Free Tool")
    print("=" * 45 + "\n")
    
    # Contacts load karo
    df = load_contacts(CSV_FILE)
    
    if df is not None:
        # Confirm karo
        print(f"Contacts preview:")
        print(df.head())
        print(f"\nKya {len(df)} logon ko message bhejna hai? (yes/no): ", end="")
        
        confirm = input().strip().lower()
        
        if confirm == 'yes':
            send_messages(df)
        else:
            print("❌ Cancel kar diya. Phir chalao jab ready ho!")
