import json
import os
import time
from datetime import datetime
import getpass

# ==================== DATA STRUCTURES ====================
class User:
    def __init__(self, username=None, anonymous=True, experience="", resources=None):
        self.username = username or "Anonymous_" + str(hash(time.time()))[:8]
        self.anonymous = anonymous
        self.experience = experience
        self.resources = resources or []
        self.joined_date = datetime.now().strftime("%Y-%m-%d")
        self.followed_tools = []
        
class Tool:
    def __init__(self, name, platform, category, subcategory, description, difficulty):
        self.name = name
        self.platform = platform
        self.category = category
        self.subcategory = subcategory
        self.description = description
        self.difficulty = difficulty  # Beginner, Intermediate, Advanced
        
# ==================== TOOLS DATABASE ====================
def initialize_tools_database():
    tools = {
        "Phone": {
            "Android": {
                "Persistence": [
                    Tool("Metasploit Android Payload", "Phone", "Persistence", "Android", 
                         "Generate persistent backdoor for Android", "Intermediate"),
                    Tool("AhMyth Android RAT", "Phone", "Persistence", "Android",
                         "Remote Administration Tool for Android", "Advanced")
                ],
                "Reverse Engineering": [
                    Tool("JADX", "Phone", "Reverse Engineering", "Android",
                         "Dex to Java decompiler", "Beginner"),
                    Tool("APKTool", "Phone", "Reverse Engineering", "Android",
                         "Reverse engineering APK files", "Intermediate")
                ],
                "Forensics": [
                    Tool("MobSF", "Phone", "Forensics", "Android",
                         "Mobile Security Framework", "Intermediate")
                ]
            },
            "iOS": {
                "Persistence": [
                    Tool("Cydia Impactor", "Phone", "Persistence", "iOS",
                         "Jailbreak tool for iOS", "Advanced")
                ],
                "Reverse Engineering": [
                    Tool("Hopper Disassembler", "Phone", "Reverse Engineering", "iOS",
                         "Reverse engineering platform", "Advanced")
                ]
            }
        },
        
        "Linux": {
            "Kali Linux": {
                "Information Gathering": [
                    Tool("Nmap", "Linux", "Information Gathering", "Kali Linux",
                         "Network discovery and security auditing", "Beginner"),
                    Tool("theHarvester", "Linux", "Information Gathering", "Kali Linux",
                         "Email, subdomain, and name scraping", "Beginner")
                ],
                "Vulnerability Analysis": [
                    Tool("OpenVAS", "Linux", "Vulnerability Analysis", "Kali Linux",
                         "Open source vulnerability scanner", "Intermediate"),
                    Tool("Nikto", "Linux", "Vulnerability Analysis", "Kali Linux",
                         "Web server scanner", "Beginner")
                ],
                "Web Application Analysis": [
                    Tool("Burp Suite", "Linux", "Web Application Analysis", "Kali Linux",
                         "Web vulnerability scanner", "Intermediate"),
                    Tool("SQLmap", "Linux", "Web Application Analysis", "Kali Linux",
                         "Automatic SQL injection tool", "Intermediate")
                ],
                "Password Attacks": [
                    Tool("John the Ripper", "Linux", "Password Attacks", "Kali Linux",
                         "Password cracker", "Intermediate"),
                    Tool("Hashcat", "Linux", "Password Attacks", "Kali Linux",
                         "Advanced password recovery", "Advanced")
                ],
                "Wireless Attacks": [
                    Tool("Aircrack-ng", "Linux", "Wireless Attacks", "Kali Linux",
                         "WiFi security auditing tools", "Intermediate")
                ],
                "Reverse Engineering": [
                    Tool("Ghidra", "Linux", "Reverse Engineering", "Kali Linux",
                         "Software reverse engineering suite", "Advanced"),
                    Tool("Radare2", "Linux", "Reverse Engineering", "Kali Linux",
                         "Unix-like reverse engineering framework", "Advanced")
                ],
                "Exploitation Tools": [
                    Tool("Metasploit Framework", "Linux", "Exploitation Tools", "Kali Linux",
                         "Penetration testing platform", "Intermediate"),
                    Tool("BeEF", "Linux", "Exploitation Tools", "Kali Linux",
                         "Browser Exploitation Framework", "Intermediate")
                ],
                "Post Exploitation": [
                    Tool("Meterpreter", "Linux", "Post Exploitation", "Kali Linux",
                         "Advanced payload for Metasploit", "Advanced"),
                    Tool("Empire", "Linux", "Post Exploitation", "Kali Linux",
                         "Post-exploitation framework", "Advanced")
                ],
                "Forensics": [
                    Tool("Autopsy", "Linux", "Forensics", "Kali Linux",
                         "Digital forensics platform", "Intermediate"),
                    Tool("Volatility", "Linux", "Forensics", "Kali Linux",
                         "Memory forensics framework", "Advanced")
                ],
                "Social Engineering": [
                    Tool("Social Engineer Toolkit (SET)", "Linux", "Social Engineering", "Kali Linux",
                         "Penetration testing for social engineering", "Intermediate")
                ],
                "Sniffing & Spoofing": [
                    Tool("Wireshark", "Linux", "Sniffing & Spoofing", "Kali Linux",
                         "Network protocol analyzer", "Beginner"),
                    Tool("Ettercap", "Linux", "Sniffing & Spoofing", "Kali Linux",
                         "Comprehensive MITM attack suite", "Intermediate")
                ]
            },
            "Ubuntu": {
                "Container Security": [
                    Tool("Docker Bench Security", "Linux", "Container Security", "Ubuntu",
                         "Security checks for Docker containers", "Intermediate"),
                    Tool("Clair", "Linux", "Container Security", "Ubuntu",
                         "Static analysis for Docker containers", "Advanced")
                ]
            },
            "Termux": {
                "Mobile Hacking": [
                    Tool("Termux-API", "Linux", "Mobile Hacking", "Termux",
                         "Access phone features from Termux", "Beginner"),
                    Tool("Nmap (Termux)", "Linux", "Mobile Hacking", "Termux",
                         "Network scanner for Android", "Beginner")
                ]
            }
        },
        
        "Windows": {
            "General": {
                "Reverse Engineering": [
                    Tool("IDA Pro", "Windows", "Reverse Engineering", "General",
                         "Interactive disassembler", "Advanced"),
                    Tool("x64dbg", "Windows", "Reverse Engineering", "General",
                         "Open-source debugger", "Intermediate")
                ],
                "Forensics": [
                    Tool("FTK Imager", "Windows", "Forensics", "General",
                         "Forensic imaging tool", "Intermediate"),
                    Tool("Autopsy (Windows)", "Windows", "Forensics", "General",
                         "Digital forensics", "Intermediate")
                ]
            }
        },
        
        "Web": {
            "General": {
                "Bug Bounty": [
                    Tool("Burp Suite Professional", "Web", "Bug Bounty", "General",
                         "Web vulnerability scanner", "Intermediate"),
                    Tool("OWASP ZAP", "Web", "Bug Bounty", "General",
                         "Web app security scanner", "Beginner")
                ],
                "Reconnaissance": [
                    Tool("Sublist3r", "Web", "Reconnaissance", "General",
                         "Subdomain enumeration tool", "Beginner"),
                    Tool("Wayback Machine", "Web", "Reconnaissance", "General",
                         "Historical web page archive", "Beginner")
                ]
            }
        }
    }
    return tools

# ==================== DISPLAY FUNCTIONS ====================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print("═" * 60)
    print(f"🛡️  {title:^54} 🛡️")
    print("═" * 60)

def print_logo():
    logo = """
     ___    _   _   _     _____   _     _   _   _____   _____   
    |  _|  | | | | | |   |  ___| | |   | | | | |  _  | |  _  |  
    | |    | |_| | | |   | |__   | |   | |_| | | |_| | | |_| |  
    | |    |  _  | | |   |  __|  | |   |  _  | |  ___| |  _  |  
    | |__  | | | | | |__ | |___  | |__ | | | | | |     | | | |  
    |____| |_| |_| |____||_____| |____||_| |_| |_|     |_| |_|  
    
    """
    print(logo)
    print(" " * 15 + "Social Platform for Ethical Hackers")
    print("═" * 60)

# ==================== WELCOME PAGE ====================
def welcome_page():
    print_logo()
    print("\n" + "=" * 60)
    print("WELCOME TO HACKER HUB")
    print("=" * 60)
    print("\nChoose your entry method:")
    print("1. 📝 Sign Up (Create an account)")
    print("2. 🎭 Continue Anonymously")
    print("3. 🔐 Login (Existing users)")
    print("4. ❌ Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        if choice == "1":
            return sign_up()
        elif choice == "2":
            return anonymous_entry()
        elif choice == "3":
            return login()
        elif choice == "4":
            print("\n👋 Stay secure! Goodbye!")
            exit()
        else:
            print("❌ Invalid choice. Please try again.")

def sign_up():
    print_header("CREATE ACCOUNT")
    print("Create your secure profile\n")
    
    while True:
        username = input("Choose a username: ").strip()
        if len(username) < 3:
            print("❌ Username must be at least 3 characters")
            continue
        break
    
    while True:
        email = input("Email: ").strip()
        if "@" not in email or "." not in email:
            print("❌ Please enter a valid email")
            continue
        break
    
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm Password: ")
    
    if password != confirm:
        print("\n❌ Passwords don't match!")
        time.sleep(2)
        return sign_up()
    
    # In a real app, you'd hash the password and store in database
    print("\n✅ Account created successfully!")
    time.sleep(1)
    
    user = User(username, anonymous=False)
    return experience_selection(user)

def anonymous_entry():
    print_header("ANONYMOUS ENTRY")
    print("\n⚠️  You are entering anonymously")
    print("• Your activity won't be saved")
    print("• You cannot post or comment")
    print("• You can browse tools and resources\n")
    
    input("Press Enter to continue...")
    user = User(anonymous=True)
    return experience_selection(user)

def login():
    print_header("LOGIN")
    print("\nNote: This is a prototype. In production,")
    print("this would connect to a secure database.\n")
    
    # Mock login for demo
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    
    print(f"\n✅ Logged in as {username}")
    time.sleep(1)
    
    user = User(username, anonymous=False)
    return main_menu(user)

# ==================== EXPERIENCE & RESOURCES ====================
def experience_selection(user):
    print_header("EXPERIENCE LEVEL")
    print("\nSelect your experience level:\n")
    print("1. 🟢 Beginner - Just starting out")
    print("2. 🟡 Intermediate - Some experience")
    print("3. 🔴 Advanced - Professional/Penetration Tester")
    print("4. ⚫ Elite - Security Researcher/Red Team")
    
    levels = {
        "1": "Beginner",
        "2": "Intermediate", 
        "3": "Advanced",
        "4": "Elite"
    }
    
    while True:
        choice = input("\nSelect (1-4): ").strip()
        if choice in levels:
            user.experience = levels[choice]
            break
        print("❌ Invalid choice")
    
    return resource_selection(user)

def resource_selection(user):
    print_header("AVAILABLE RESOURCES")
    print(f"\nWelcome, {user.username} ({user.experience} level)")
    print("\nSelect your available resources (comma-separated):\n")
    print("1. 📱 Phone (Android/iOS)")
    print("2. 💻 PC/Laptop (Windows/Mac/Linux)")
    print("3. 🖥️  Hacking Lab (Virtual Machines)")
    print("4. ☁️  Cloud Resources (AWS/Azure/DigitalOcean)")
    print("5. 🐧 Dedicated Linux Machine")
    print("6. 🎯 All of the above")
    
    resource_map = {
        "1": "Phone",
        "2": "PC/Laptop", 
        "3": "Hacking Lab",
        "4": "Cloud Resources",
        "5": "Dedicated Linux Machine",
        "6": "All Resources"
    }
    
    while True:
        choices = input("\nEnter choices (e.g., 1,3,5): ").strip()
        selected = [c.strip() for c in choices.split(",") if c.strip()]
        
        valid = True
        user_resources = []
        
        for choice in selected:
            if choice in resource_map:
                if choice == "6":
                    user_resources = ["Phone", "PC/Laptop", "Hacking Lab", 
                                    "Cloud Resources", "Dedicated Linux Machine"]
                    break
                user_resources.append(resource_map[choice])
            else:
                print(f"❌ Invalid choice: {choice}")
                valid = False
                break
        
        if valid and user_resources:
            user.resources = user_resources
            break
    
    print(f"\n✅ Resources selected: {', '.join(user.resources)}")
    time.sleep(1)
    return main_menu(user)

# ==================== TOOLS BROWSER ====================
def browse_tools(user, tools_db):
    while True:
        print_header("TOOLS DIRECTORY")
        print(f"User: {user.username} | Experience: {user.experience}\n")
        print("Select platform:\n")
        
        platforms = list(tools_db.keys())
        for i, platform in enumerate(platforms, 1):
            print(f"{i}. {platform}")
        
        print(f"{len(platforms)+1}. 🔍 Search Tools")
        print(f"{len(platforms)+2}. 📋 My Followed Tools")
        print(f"{len(platforms)+3}. ↩️ Back to Main Menu")
        
        try:
            choice = int(input(f"\nSelect (1-{len(platforms)+3}): "))
            
            if 1 <= choice <= len(platforms):
                platform_name = platforms[choice-1]
                platform_tools(tools_db[platform_name], platform_name, user, tools_db)
            elif choice == len(platforms)+1:
                search_tools(user, tools_db)
            elif choice == len(platforms)+2:
                show_followed_tools(user)
            elif choice == len(platforms)+3:
                return
            else:
                print("❌ Invalid choice")
                time.sleep(1)
        except ValueError:
            print("❌ Please enter a number")
            time.sleep(1)

def platform_tools(platform_data, platform_name, user, tools_db):
    while True:
        print_header(f"{platform_name.upper()} TOOLS")
        print("Select category/distribution:\n")
        
        categories = list(platform_data.keys())
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        print(f"{len(categories)+1}. ↩️ Back")
        
        try:
            choice = int(input(f"\nSelect (1-{len(categories)+1}): "))
            
            if 1 <= choice <= len(categories):
                category_name = categories[choice-1]
                category_tools(platform_data[category_name], f"{platform_name} - {category_name}", 
                              user, tools_db, platform_name, category_name)
            elif choice == len(categories)+1:
                return
            else:
                print("❌ Invalid choice")
                time.sleep(1)
        except ValueError:
            print("❌ Please enter a number")
            time.sleep(1)

def category_tools(category_data, full_path, user, tools_db, platform, category):
    while True:
        print_header(f"{full_path.upper()}")
        print("Select subcategory:\n")
        
        subcategories = list(category_data.keys())
        for i, subcat in enumerate(subcategories, 1):
            tool_count = len(category_data[subcat])
            print(f"{i}. {subcat} ({tool_count} tools)")
        
        print(f"{len(subcategories)+1}. ↩️ Back")
        
        try:
            choice = int(input(f"\nSelect (1-{len(subcategories)+1}): "))
            
            if 1 <= choice <= len(subcategories):
                subcat_name = subcategories[choice-1]
                display_tools(category_data[subcat_name], f"{full_path} - {subcat_name}", 
                             user, platform, category, subcat_name)
            elif choice == len(subcategories)+1:
                return
            else:
                print("❌ Invalid choice")
                time.sleep(1)
        except ValueError:
            print("❌ Please enter a number")
            time.sleep(1)

def display_tools(tools_list, full_path, user, platform, category, subcategory):
    print_header(f"{full_path.upper()}")
    print(f"Found {len(tools_list)} tools\n")
    
    for i, tool in enumerate(tools_list, 1):
        followed = "⭐" if tool.name in user.followed_tools else " "
        print(f"{i}. {followed} {tool.name}")
        print(f"   📝 {tool.description}")
        print(f"   🎯 Difficulty: {tool.difficulty}")
        print()
    
    print("\nOptions:")
    print("1-{}. View tool details".format(len(tools_list)))
    print("F. Follow/Unfollow a tool")
    print("B. ↩️ Back")
    
    while True:
        choice = input("\nSelect: ").strip().upper()
        
        if choice == 'B':
            return
        elif choice == 'F':
            if user.anonymous:
                print("❌ Anonymous users cannot follow tools")
                time.sleep(1)
                continue
            
            try:
                tool_num = int(input("Tool number to follow/unfollow: ")) - 1
                if 0 <= tool_num < len(tools_list):
                    tool = tools_list[tool_num]
                    if tool.name in user.followed_tools:
                        user.followed_tools.remove(tool.name)
                        print(f"✅ Unfollowed {tool.name}")
                    else:
                        user.followed_tools.append(tool.name)
                        print(f"✅ Following {tool.name}")
                    time.sleep(1)
                    display_tools(tools_list, full_path, user, platform, category, subcategory)
                    return
            except ValueError:
                print("❌ Invalid number")
        elif choice.isdigit():
            try:
                tool_num = int(choice) - 1
                if 0 <= tool_num < len(tools_list):
                    view_tool_details(tools_list[tool_num], user)
                    display_tools(tools_list, full_path, user, platform, category, subcategory)
                    return
            except ValueError:
                print("❌ Invalid selection")

def view_tool_details(tool, user):
    print_header(f"TOOL DETAILS: {tool.name}")
    print(f"\n🔧 Name: {tool.name}")
    print(f"📁 Platform: {tool.platform}")
    print(f"📂 Category: {tool.category}")
    print(f"📋 Subcategory: {tool.subcategory}")
    print(f"📝 Description: {tool.description}")
    print(f"🎯 Difficulty: {tool.difficulty}")
    print(f"👤 Recommended for: {tool.difficulty} level users")
    
    if user.experience in ["Beginner", "Intermediate"] and tool.difficulty == "Advanced":
        print("\n⚠️  Warning: This tool is advanced. Consider building")
        print("   foundational skills first.")
    
    print("\nSuggested Learning Path:")
    if tool.difficulty == "Beginner":
        print("• YouTube tutorials")
        print("• Official documentation")
        print("• Try in lab environment")
    elif tool.difficulty == "Intermediate":
        print("• Advanced courses (Udemy, Cybrary)")
        print("• Practice on HackTheBox/TryHackMe")
        print("• Read security blogs")
    else:
        print("• Official security certifications")
        print("• Advanced labs (Pentester Academy)")
        print("• Contribute to open-source security tools")
    
    print("\nPress Enter to continue...")
    input()

def search_tools(user, tools_db):
    print_header("SEARCH TOOLS")
    print("\nSearch for tools by name, category, or keyword\n")
    
    search_term = input("Enter search term: ").strip().lower()
    
    if not search_term:
        return
    
    results = []
    
    # Search through all tools
    for platform in tools_db.values():
        for category in platform.values():
            for subcategory in category.values():
                for tool in subcategory:
                    if (search_term in tool.name.lower() or 
                        search_term in tool.description.lower() or
                        search_term in tool.category.lower() or
                        search_term in tool.subcategory.lower()):
                        results.append(tool)
    
    if not results:
        print(f"\n❌ No results found for '{search_term}'")
        time.sleep(2)
        return
    
    print(f"\n🔍 Found {len(results)} results:\n")
    
    for i, tool in enumerate(results[:10], 1):  # Show first 10 results
        print(f"{i}. {tool.name}")
        print(f"   {tool.description[:80]}...")
        print(f"   📍 {tool.platform} > {tool.category} > {tool.subcategory}")
        print()
    
    if len(results) > 10:
        print(f"... and {len(results)-10} more results")
    
    print("\n1. View a tool")
    print("2. New search")
    print("3. Back")
    
    while True:
        choice = input("\nSelect: ").strip()
        if choice == "1":
            try:
                tool_num = int(input("Enter tool number: ")) - 1
                if 0 <= tool_num < len(results):
                    view_tool_details(results[tool_num], user)
                    return search_tools(user, tools_db)
            except ValueError:
                print("❌ Invalid number")
        elif choice == "2":
            return search_tools(user, tools_db)
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")

def show_followed_tools(user):
    if not user.followed_tools:
        print_header("MY FOLLOWED TOOLS")
        print("\nYou're not following any tools yet.")
        print("Browse tools and click 'F' to follow them!")
        print("\nPress Enter to continue...")
        input()
        return
    
    print_header("MY FOLLOWED TOOLS")
    print(f"\nFollowing {len(user.followed_tools)} tools:\n")
    
    # In a real app, you'd fetch tool details from database
    for i, tool_name in enumerate(user.followed_tools, 1):
        print(f"{i}. ⭐ {tool_name}")
    
    print("\nNote: In the full version, this would show:")
    print("• Tool updates and news")
    print("• New CVEs for your tools")
    print("• Community discussions")
    print("• Tutorial recommendations")
    
    print("\nPress Enter to continue...")
    input()

# ==================== COMMUNITY FEATURES ====================
def community_forum(user):
    print_header("COMMUNITY FORUM")
    
    if user.anonymous:
        print("\n❌ Anonymous users cannot access the forum")
        print("Sign up to participate in discussions!")
        time.sleep(2)
        return
    
    print("\nForum Categories:\n")
    print("1. 📢 Announcements")
    print("2. 🆘 Help & Support")
    print("3. 🛠️ Tool Discussions")
    print("4. 🎓 Learning Resources")
    print("5. 💼 Jobs & Opportunities")
    print("6. 🔓 CTF Challenges")
    print("7. ↩️ Back")
    
    # In full version, this would connect to a forum system
    print("\n[Forum would load here in full version]")
    
    choice = input("\nSelect category (1-7): ").strip()
    if choice == "7":
        return
    
    print("\n🔧 Feature in development")
    print("The full version would include:")
    print("• Real-time discussions")
    print("• Code sharing")
    print("• Vulnerability reports")
    print("• Mentorship programs")
    print("\nPress Enter to continue...")
    input()

# ==================== MAIN MENU ====================
def main_menu(user):
    tools_db = initialize_tools_database()
    
    while True:
        print_header("HACKER HUB - MAIN MENU")
        
        welcome_msg = f"Welcome, {'👤 ' + user.username if not user.anonymous else '🎭 Anonymous'}"
        print(f"{welcome_msg:^60}")
        print(f"{'Experience: ' + user.experience:^60}")
        print(f"{'Resources: ' + ', '.join(user.resources[:3]):^60}")
        if len(user.resources) > 3:
            print(f"{'(+ ' + str(len(user.resources)-3) + ' more)':^60}")
        
        print("\n" + "═" * 60)
        print("\nWhat would you like to do?\n")
        
        print("1. 🛠️  Browse Hacking Tools")
        print("2. 🔍 Search Tools")
        print("3. 👥 Community Forum")
        print("4. 📚 Learning Path")
        print("5. 🎯 Recommended Tools")
        print("6. ⚙️  Profile Settings")
        
        if user.anonymous:
            print("7. 📝 Sign Up (to unlock all features)")
        
        print("0. 🚪 Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            browse_tools(user, tools_db)
        elif choice == "2":
            search_tools(user, tools_db)
        elif choice == "3":
            community_forum(user)
        elif choice == "4":
            show_learning_path(user)
        elif choice == "5":
            show_recommended_tools(user, tools_db)
        elif choice == "6":
            profile_settings(user)
        elif choice == "7" and user.anonymous:
            user = sign_up()  # Returns a new user object
            tools_db = initialize_tools_database()
        elif choice == "0":
            print("\n👋 Stay ethical, stay secure!")
            print("Remember: With great power comes great responsibility.\n")
            exit()
        else:
            print("❌ Invalid option")
            time.sleep(1)

def show_learning_path(user):
    print_header("LEARNING PATH")
    print(f"\nRecommended path for {user.experience} level\n")
    
    if user.experience == "Beginner":
        print("📚 Foundation Phase (Months 1-3):")
        print("  • Linux basics (Command line, file system)")
        print("  • Networking fundamentals")
        print("  • Basic programming (Python/Bash)")
        print("  • TryHackMe Beginner paths")
        
        print("\n🎯 Next Steps:")
        print("  • Complete OverTheWire Bandit")
        print("  • TryHackMe 'Complete Beginner' path")
        print("  • NetworkChuck YouTube tutorials")
        
    elif user.experience == "Intermediate":
        print("🚀 Skill Building Phase:")
        print("  • Web application security")
        print("  • Active Directory basics")
        print("  • Python for security automation")
        print("  • HackTheBox starting points")
        
        print("\n🎯 Certifications to consider:")
        print("  • eJPT (Junior Penetration Tester)")
        print("  • CompTIA Security+")
        
    elif user.experience in ["Advanced", "Elite"]:
        print("⚡ Advanced Specialization:")
        print("  • Red team operations")
        print("  • Advanced malware analysis")
        print("  • Cloud security (AWS/Azure)")
        print("  • Purple team exercises")
        
        print("\n🎯 Advanced Certifications:")
        print("  • OSCP (Offensive Security Certified Professional)")
        print("  • SANS courses")
        print("  • Crest certifications")
    
    print("\n📅 Weekly Goals:")
    print("  • 2 hours of hands-on practice")
    print("  • 1 CTF challenge")
    print("  • Read 1 security blog post")
    print("  • Write up 1 finding")
    
    print("\nPress Enter to continue...")
    input()

def show_recommended_tools(user, tools_db):
    print_header("RECOMMENDED TOOLS")
    print(f"\nTools matched to your profile:\n")
    print(f"• Experience: {user.experience}")
    print(f"• Resources: {', '.join(user.resources)}\n")
    
    recommendations = []
    
    # Filter tools based on user profile
    for platform in tools_db.values():
        for category in platform.values():
            for subcategory in category.values():
                for tool in subcategory:
                    # Match difficulty to experience
                    if (user.experience == "Beginner" and tool.difficulty == "Beginner") or \
                       (user.experience == "Intermediate" and tool.difficulty in ["Beginner", "Intermediate"]) or \
                       (user.experience in ["Advanced", "Elite"]):
                        # Check if user has resources for this platform
                        platform_lower = tool.platform.lower()
                        user_resources_lower = [r.lower() for r in user.resources]
                        
                        if any(resource in platform_lower for resource in ["phone", "android", "ios"]) and "phone" in user_resources_lower:
                            recommendations.append(tool)
                        elif "linux" in platform_lower and any(r in ["pc/laptop", "hacking lab", "dedicated linux machine"] for r in user_resources_lower):
                            recommendations.append(tool)
                        elif "windows" in platform_lower and "pc/laptop" in user_resources_lower:
                            recommendations.append(tool)
                        elif "web" in platform_lower and "pc/laptop" in user_resources_lower:
                            recommendations.append(tool)
    
    # Show top 5 recommendations
    for i, tool in enumerate(recommendations[:5], 1):
        print(f"{i}. {tool.name}")
        print(f"   {tool.description[:70]}...")
        print(f"   🎯 {tool.difficulty} | 📍 {tool.platform}")
        print()
    
    print("\nPress Enter to continue...")
    input()

def profile_settings(user):
    if user.anonymous:
        print_header("PROFILE SETTINGS")
        print("\n❌ Anonymous users don't have profiles")
        print("Sign up to access profile features!")
        time.sleep(2)
        return
    
    print_header(f"PROFILE: {user.username}")
    print(f"\n👤 Username: {user.username}")
    print(f"📅 Joined: {user.joined_date}")
    print(f"🎯 Experience: {user.experience}")
    print(f"💻 Resources: {', '.join(user.resources)}")
    print(f"⭐ Following: {len(user.followed_tools)} tools")
    
    print("\nOptions:")
    print("1. Edit profile")
    print("2. Change experience level")
    print("3. Update resources")
    print("4. View followed tools")
    print("5. Back")
    
    choice = input("\nSelect: ").strip()
    
    if choice == "1":
        print("\n🔧 Feature in development")
        print("Full version would allow:")
        print("• Bio/avatar customization")
        print("• Skill tags")
        print("• Portfolio links")
        print("• Privacy settings")
    elif choice == "2":
        user.experience = input("New experience level: ").strip()
        print("✅ Experience level updated")
    elif choice == "3":
        print("\nCurrent resources:", ', '.join(user.resources))
        new_resources = input("Enter new resources (comma-separated): ").strip()
        user.resources = [r.strip() for r in new_resources.split(",") if r.strip()]
        print("✅ Resources updated")
    elif choice == "4":
        show_followed_tools(user)
        return profile_settings(user)
    
    print("\nPress Enter to continue...")
    input()

# ==================== MAIN PROGRAM ====================
def main():
    # Set up terminal for better display (optional)
    try:
        os.system('')  # Enable ANSI codes on Windows
    except:
        pass
    
    print("\n" + "="*60)
    print("🚀 HACKER HUB - Loading...")
    print("="*60)
    time.sleep(1)
    
    # Start the app
    user = welcome_page()
    
    # If user is None (shouldn't happen), create anonymous user
    if not user:
        user = User(anonymous=True)
    
    # Enter main menu
    main_menu(user)

# ==================== FUTURE ENHANCEMENTS ====================
"""
Features for future development:

1. Database Integration:
   - PostgreSQL/MySQL for user data
   - Redis for caching tools
   - MongoDB for forum posts

2. Web Version (Flask/Django):
   - REST API for tools
   - Real-time chat with WebSockets
   - OAuth for GitHub/Twitter login

3. Mobile App (React Native/Flutter):
   - Push notifications for tool updates
   - Offline tool database
   - CTF challenge tracker

4. Advanced Features:
   - Virtual lab integration (Docker)
   - CVSS calculator
   - Report generator
   - Collaboration tools
   - Job board with verified companies
   - Certificate verification
   - Bug bounty program integration
"""

if __name__ == "__main__":
    main()