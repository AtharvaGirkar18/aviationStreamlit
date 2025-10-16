
import hashlib
import getpass


def hash_password(password):
    
    return hashlib.sha256(password.encode()).hexdigest()


def create_user():
    
    print("\n" + "="*50)
    print("🔐 Aviation BI Chatbot - User Creation")
    print("="*50 + "\n")
    
    username = input("Enter username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match!")
        return
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters long!")
        return
    
    hashed = hash_password(password)
    
    print("\n✅ User created successfully!\n")
    print("Add these lines to your .env file:")
    print("-" * 50)
    print(f"USER_USERNAME={username}")
    print(f"USER_PASSWORD={password}")  
    print("-" * 50)
    print(f"\n🔒 Hashed password: {hashed}")
    print("\nFor enhanced security, store the hashed version and modify")
    print("the check_credentials() function in app.py to compare hashes.\n")


def verify_password():
   
    print("\n" + "="*50)
    print("🔍 Password Verification")
    print("="*50 + "\n")
    
    password = getpass.getpass("Enter password to hash: ")
    hashed = hash_password(password)
    
    print(f"\n🔒 SHA-256 Hash: {hashed}\n")


def main():
    
    while True:
        print("\n" + "="*50)
        print("Aviation BI Chatbot - User Management")
        print("="*50)
        print("\n1. Create new user")
        print("2. Generate password hash")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            create_user()
        elif choice == "2":
            verify_password()
        elif choice == "3":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
