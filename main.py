import os
import time
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import GetContactsRequest

# Function to login to Telegram
def login(api_id, api_hash, phone_number):
    print("Step 1: Starting login process...")
    client = TelegramClient('session_name', api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        print("User not authorized. Sending code request...")
        client.send_code_request(phone_number)
        code = input("Enter the code you received on Telegram: ")
        client.sign_in(phone_number, code)
    else:
        print("User already authorized.")
    print("Login successful.")
    return client

# Function to extract all contacts and save them to a file
def extract_and_save_contacts(client):
    print("\nStep 2: Extracting contacts and saving to contacts.txt...")
    try:
        contacts = client(GetContactsRequest(hash=0)).users
        with open("contacts.txt", "w") as file:
            for contact in contacts:
                if contact.username:
                    file.write(f"{contact.username}\n")
        print(f"Found {len(contacts)} contacts and saved to contacts.txt.")
        return contacts
    except Exception as e:
        print(f"Failed to retrieve contacts: {e}")
        return []

# Function to send a message to contacts listed in contacts.txt with rate limiting
def send_message_to_contacts_from_file(client, message):
    print("\nStep 3: Sending message to contacts in contacts.txt with rate limit...")
    try:
        with open("contacts.txt", "r") as file:
            usernames = [line.strip() for line in file.readlines()]
        
        # Confirm with the user before sending the message
        confirm = input(f"Send message to {len(usernames)} contacts listed in contacts.txt? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Message sending canceled.")
            return
        
        # Send the message to each contact with rate limiting (20 messages per second)
        messages_sent = 0
        for username in usernames:
            try:
                print(f"Sending message to {username}...")
                client.send_message(username, message)
                print(f"Message sent to {username} successfully!")
                messages_sent += 1

                # Pause if 20 messages have been sent within the last second
                if messages_sent % 20 == 0:
                    print("Rate limit reached (20 messages per second). Pausing for 1 second...")
                    time.sleep(1)

            except Exception as e:
                print(f"Failed to send message to {username}: {e}")
        print("Message sending complete.")
    except FileNotFoundError:
        print("contacts.txt not found. Make sure to run the contact extraction step first.")

# Function to delete contacts.txt file after sending messages
def delete_contacts_file():
    if os.path.exists("contacts.txt"):
        delete_confirm = input("\nDo you want to delete contacts.txt? (yes/no): ")
        if delete_confirm.lower() == 'yes':
            os.remove("contacts.txt")
            print("contacts.txt deleted successfully.")
        else:
            print("contacts.txt retained.")
    else:
        print("contacts.txt not found.")

# Function to delete the Telegram session file
def delete_session_file():
    session_file = "session_name.session"
    if os.path.exists(session_file):
        delete_confirm = input(f"\nDo you want to delete the session file ({session_file})? (yes/no): ")
        if delete_confirm.lower() == 'yes':
            os.remove(session_file)
            print(f"{session_file} deleted successfully.")
        else:
            print(f"{session_file} retained.")
    else:
        print(f"{session_file} not found.")

# Main function
def main():
    # Input your Telegram API credentials
    api_id = ''       # Replace with your actual API ID
    api_hash = ''    # Replace with your actual API Hash
    phone_number = '+91<number>'  # Replace with your phone number

    # Step 1: Login to Telegram
    if input("Proceed with login? (yes/no): ").lower() == 'yes':
        client = login(api_id, api_hash, phone_number)
    else:
        print("Process aborted.")
        return

    # Step 2: Extract contacts and save them to contacts.txt
    if input("Proceed with extracting contacts? (yes/no): ").lower() == 'yes':
        extract_and_save_contacts(client)
    else:
        print("Process aborted.")
        return

    # Step 3: Read from contacts.txt and send the message
    if input("Proceed with sending messages to contacts? (yes/no): ").lower() == 'yes':
        message = 'Sorry! Please don’t click on the link above, my account was hacked.'
        send_message_to_contacts_from_file(client, message)
    else:
        print("Message sending canceled.")

    # Step 4: Disconnect the client to release the session file
    client.disconnect()
    print("\nClient disconnected.")

    # Step 5: Ask if the user wants to delete contacts.txt
    delete_contacts_file()

    # Step 6: Ask if the user wants to delete the session file
    delete_session_file()

if __name__ == '__main__':
    main()
