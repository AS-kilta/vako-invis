import os
import json

# Inventory file path
FILE_PATH = "inventory.json"

class VakoInvis:
    def __init__(self, file_path = "inventory.json"):
        self.file_path = file_path
        self.inventory = self.load()


    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        return {}
    

    def save(self):
        with open(self.file_path, "w") as file:
            json.dump(self.inventory, file, indent=4)


    def remove(self, item, q, totally=False):
        try:
            if totally:
                self.inventory.pop(item)
                self.save()
                return True

            old_q = self.inventory[item]['quantity']
            self.inventory[item]['quantity'] = max(old_q - q, 0)
            self.save()
            return True
        
        except KeyError:
            print("No such item in the inventory")
            return False
        

    def add(self, item, q, new=False):
        try:
            if new:
                self.inventory[item]['quantity'] = q
                self.save()
                return True

            self.inventory[item]['quantity'] += q
            self.save()
            return True
        
        except KeyError:
            # if item wasn't found
            print("No such item in the inventory")
            return False
        
        
    def update_alarm_limit(self, item, limit):
        try: 
            self.inventory[item]['alarm_limit'] = limit
            self.save()
            return True
        except KeyError:
            print("No such item in the inventory")
            return False
        
    
    def check_alarm_limit(self, item):
        if self.inventory[item]['alarm_limit'] != None and self.inventory[item]['quantity'] < self.inventory[item]['alarm_limit']:
            return False
        return True
        

    def print_out(self, item=None, full_info=None):
        if item is not None:
            print(f"{item} => quantity: {self.inventory[item]['quantity']} "
                    f"{f'and alarm limit : {self.inventory[item]['alarm_limit']}' if full_info is not None else ''}")
            return
        
        for i in self.inventory:
            print(f"{i} => quantity: {self.inventory[i]['quantity']} "
                    f"{f'and alarm limit : {self.inventory[i]['alarm_limit']}' if full_info is not None else ''}")


def main():
    invis = VakoInvis()
    
    while True:
        print("\nInventory Management")
        print("1. Add Item")
        print("2. Remove Item")
        print("3. View Inventory")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            f_new = int(input("Enter 1 if you want to add fully new item and 0 if not: "))
            item = input("Enter item name: ")
            quantity = int(input("Enter quantity: "))
            invis.add(item, quantity, new=(True if f_new == 1 else False))

        elif choice == "2":
            t_in = int(input("Enter 1 if you want to totally remove the item and 0 if not: "))
            item = input("Enter item name: ")
            quantity = int(input("Enter quantity to remove: "))
            invis.remove(item, quantity, totally=(True if t_in == 1 else False))

        elif choice == "3":
            invis.print_out()

        elif choice == "4":
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()