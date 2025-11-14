from structure import loginPage

def main():
    user = loginPage.login()
    if user:
        print(f"Welcome, {user.username}!")
        # later you can redirect to chatPage here

if __name__ == "__main__":
    main()
