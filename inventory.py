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
        """
        Removes a specified quantity of an item from the inventory.
        Parameters:
        item (str): The item to be removed from the inventory.
        q (int): The quantity of the item to be removed.
        totally (bool): If True, removes the item completely from the inventory. Defaults to False.
        Returns:
        bool: True if the item was successfully removed or quantity was updated, False if the item was not found in the inventory.
        Raises:
        KeyError: If the item is not found in the inventory.
        """
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
        """
        Adds a specified quantity of an item to the inventory.
        Parameters:
        item (str): The name of the item to add.
        q (int): The quantity of the item to add.
        new (bool): If True, sets the quantity of the item to q. If False, adds q to the existing quantity.
        Returns:
        bool: True if the operation was successful, False if the item was not found in the inventory.
        """
        try:
            if new or item not in self.inventory:
                self.inventory[item] = {'quantity': q, 'alarm_limit': 0}
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
        """
        Updates the alarm limit for a specified item in the inventory.

        Args:
            item (str): The name of the item to update.
            limit (int): The new alarm limit to set for the item.

        Returns:
            bool: True if the update was successful, False if the item does not exist in the inventory.

        Raises:
            KeyError: If the specified item does not exist in the inventory.
        """
        try: 
            self.inventory[item]['alarm_limit'] = limit
            self.save()
            return True
        except KeyError:
            print("No such item in the inventory")
            return False
        
    
    def check_alarm_limit(self, item):
        """
        Checks if the quantity of a given item is above its alarm limit.

        Args:zw
            item (str): The name of the item to check.

        Returns:
            bool: False if the item's quantity is below its alarm limit and the alarm limit is set, True otherwise.
        """
        if self.inventory[item]['alarm_limit'] != None and self.inventory[item]['quantity'] < self.inventory[item]['alarm_limit']:
            return False
        return True
        

    def print_out(self, item=None, full_info=None):
        """
        Prints the inventory details for a specific item or all items.
        Args:
            item (str, optional): The name of the item to print. If None, prints all items.
            full_info (bool, optional): If True, includes the alarm limit in the output.
        Returns:
            None
        """
        if item is not None:
            alarm = self.inventory[item]['alarm_limit']   # for some reason docker gives error if this is put into f string
            print(f"{item} => quantity: {self.inventory[item]['quantity']} "
                    f"{f'and alarm limit : {alarm}' if full_info is not None else ''}")
            return
        
        for i in self.inventory:
            alarm = self.inventory[i]['alarm_limit']   # for some reason docker gives error if this is put into f string
            print(f"{i} => quantity: {self.inventory[i]['quantity']} "
                    f"{f'and alarm limit : {alarm}' if full_info is not None else ''}")


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