import os

# Inventory file path
FILE_PATH = "inventory.txt"

class VakoInvis:
    def __init__(self, file_path = "inventory.txt"):
        self.file_path = file_path
        self.inventory = self.load()

    def load(self):
        inventory = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                for line in file:
                    item, quantity = line.strip().split(':')
                    inventory[item] = int(quantity)
        return inventory
    
    def save(self):
        with open(self.file_path, "w") as file:
            for item, quantity in self.inventory.items():
                file.write(f"{item}:{quantity}\n")
    
    def remove(self, item, q):
        if item in self.inventory:
            old_q = self.inventory[item]
            self.inventory[item] = max(old_q - q, 0)
        else:
            print("No such item in the inventory")
            return False
        self.save()
        return True


    def add(self, item, q, new=False):
        if new:
            self.inventory[item] = q
            self.save()
            return True

        if item in self.inventory:
            self.inventory[item] += q
            self.save()
            return True

        # if item wasn't found
        print("No such item in the inventory")
        return False
    
    def print_out(self, item=None):
        if item != None:
            print(f"{item} => {self.inventory[item]}")
            return
        
        for i in self.inventory:
            print(f" {i} => {self.inventory[i]}")


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
            item = input("Enter item name: ")
            quantity = int(input("Enter quantity to remove: "))
            invis.remove(item, quantity)

        elif choice == "3":
            invis.print_out()

        elif choice == "4":
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()