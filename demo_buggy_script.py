"""
User Management System - Demo Script
This script demonstrates various common bugs for code review.
"""

import json
import os


class UserManager:
    def __init__(self):
        self.users = []
        self.admin_password = "admin123"  # Bug: Hardcoded credentials
    
    def add_user(self, username, email, age):
        # Bug: No input validation
        user = {
            "username": username,
            "email": email,
            "age": age,
            "created_at": self.get_timestamp()
        }
        self.users.append(user)
        return user
    
    def get_timestamp(self):
        import datetime
        return datetime.datetime.now()  # Bug: Not timezone-aware
    
    def find_user(self, username):
        # Bug: Inefficient O(n) search, should use dict
        for user in self.users:
            if user["username"] == username:
                return user
        return None
    
    def calculate_average_age(self):
        # Bug: Division by zero if no users
        total = sum([user["age"] for user in self.users])
        return total / len(self.users)
    
    def save_to_file(self, filename):
        # Bug: No error handling for file operations
        f = open(filename, 'w')  # Bug: File not closed properly
        json.dump(self.users, f)
    
    def load_from_file(self, filename):
        # Bug: No check if file exists
        with open(filename, 'r') as f:
            self.users = json.load(f)
    
    def delete_user(self, username):
        # Bug: Modifying list while iterating
        for user in self.users:
            if user["username"] == username:
                self.users.remove(user)
    
    def get_adult_users(self):
        # Bug: Magic number, should be constant
        return [user for user in self.users if user["age"] >= 18]
    
    def authenticate(self, password):
        # Bug: Insecure comparison, timing attack vulnerability
        if password == self.admin_password:
            return True
        return False


def main():
    manager = UserManager()
    
    # Bug: No error handling
    manager.add_user("alice", "alice@example.com", 25)
    manager.add_user("bob", "bob@example.com", 17)
    manager.add_user("charlie", "charlie@example", 30)  # Bug: Invalid email format accepted
    
    # Bug: Potential None reference
    user = manager.find_user("david")
    print(f"Found user: {user['username']}")  # Will crash if user not found
    
    # Bug: SQL injection vulnerability if this were a real query
    search_term = input("Enter username to search: ")
    query = f"SELECT * FROM users WHERE username = '{search_term}'"  # Vulnerable
    
    avg_age = manager.calculate_average_age()
    print(f"Average age: {avg_age}")
    
    manager.save_to_file("users.json")


if __name__ == "__main__":
    main()

