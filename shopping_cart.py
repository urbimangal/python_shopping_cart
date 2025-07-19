import json

class Product:
    def __init__(self, product_id, name, price, quantity_available):
        self._product_id=product_id
        self._name=name
        self._price=price
        self._quantity_available=quantity_available

    def decrease_quantity(self, amount):
        if 0<amount<=self._quantity_available:
            self._quantity_available-=amount
            return True
        return False

    def increase_quantity(self, amount):
        if amount>0:
            self._quantity_available+=amount

    def display_details(self):
        return f"ID: {self._product_id}, Name: {self._name}, Price: ₹{self._price}, Stock: {self._quantity_available}"

    def to_dict(self):
        return {
            "type": "generic",
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity_available": self._quantity_available
        }

class PhysicalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, weight):
        Product.__init__(self, product_id, name, price, quantity_available)
        self._weight=weight

    def display_details(self):
        return f"{Product.display_details(self)}, Weight: {self._weight}kg"

    def to_dict(self):
        d=Product.to_dict(self)
        d["type"]="physical"
        d["weight"]=self._weight
        return d

class DigitalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, download_link):
        Product.__init__(self, product_id, name, price, quantity_available)
        self._download_link=download_link

    def display_details(self):
        return f"ID: {self._product_id}, Name: {self._name}, Price: ₹{self._price}, Link: {self._download_link}"

    def to_dict(self):
        d=Product.to_dict(self)
        d["type"]="digital"
        d["download_link"]=self._download_link
        return d

class CartItem:
    def __init__(self, product, quantity):
        self._product=product
        self._quantity=quantity

    def calculate_subtotal(self):
        return self._quantity*self._product._price

    def __str__(self):
        return f"Item: {self._product._name}, Quantity: {self._quantity}, Price: ₹{self._product._price}, Subtotal: ₹{self.calculate_subtotal()}"

    def to_dict(self):
        return {"product_id": self._product._product_id, "quantity": self._quantity}

class ShoppingCart:
    def __init__(self, catalog_file="products.json", cart_file="cart.json"):
        self._product_catalog_file=catalog_file
        self._cart_state_file=cart_file
        self._items={}
        self.catalog=self._load_catalog()
        self._load_cart_state()

    def _load_catalog(self):
        catalog={}
        try:
            with open(self._product_catalog_file,"r") as f:
                data=json.load(f)
                for item in data:
                    if item["type"]=="physical":
                        p=PhysicalProduct(item["product_id"],item["name"],item["price"],item["quantity_available"],item["weight"])
                    elif item["type"]=="digital":
                        p=DigitalProduct(item["product_id"],item["name"],item["price"],item["quantity_available"],item["download_link"])
                    else:
                        p=Product(item["product_id"],item["name"],item["price"],item["quantity_available"])
                    catalog[p._product_id]=p
        except: pass
        return catalog

    def _load_cart_state(self):
        try:
            with open(self._cart_state_file,"r") as f:
                data=json.load(f)
                for item in data:
                    pid=item["product_id"]
                    qty=item["quantity"]
                    if pid in self.catalog:
                        self._items[pid]=CartItem(self.catalog[pid],qty)
        except: pass

    def _save_catalog(self):
        with open(self._product_catalog_file,"w") as f:
            data=[p.to_dict() for p in self.catalog.values()]
            json.dump(data,f)

    def _save_cart_state(self):
        with open(self._cart_state_file,"w") as f:
            data=[c.to_dict() for c in self._items.values()]
            json.dump(data,f)

    def add_item(self, product_id, quantity):
        if product_id in self.catalog:
            product=self.catalog[product_id]
            if product._quantity_available>=quantity:
                if product_id in self._items:
                    self._items[product_id]._quantity+=quantity
                else:
                    self._items[product_id]=CartItem(product, quantity)
                product.decrease_quantity(quantity)
                self._save_cart_state()
                return True
        return False

    def update_quantity(self, product_id, new_quantity):
        if product_id in self._items:
            cart_item=self._items[product_id]
            current=cart_item._quantity
            product=cart_item._product
            diff=new_quantity-current
            if diff>0:
                if product._quantity_available>=diff:
                    product.decrease_quantity(diff)
                    cart_item._quantity=new_quantity
            else:
                product.increase_quantity(-diff)
                cart_item._quantity=new_quantity
            if new_quantity==0:
                del self._items[product_id]
            self._save_cart_state()
            return True
        return False

    def remove_item(self, product_id):
        if product_id in self._items:
            item=self._items.pop(product_id)
            item._product.increase_quantity(item._quantity)
            self._save_cart_state()
            return True
        return False

    def get_total(self):
        return sum(item.calculate_subtotal() for item in self._items.values())

    def display_cart(self):
        for item in self._items.values():
            print(item)
        print(f"Total: ₹{self.get_total()}")

    def display_products(self):
        for product in self.catalog.values():
            print(product.display_details())

def run():
    cart=ShoppingCart()
    while True:
        print("\n1. View Products")
        print("2. Add Product to Cart")
        print("3. View Cart")
        print("4. Update Quantity")
        print("5. Remove Item")
        print("6. Checkout")
        print("7. Exit")
        choice=input("Enter your choice: ")

        if choice=="1":
            print("Available Products:-")
            cart.display_products()

        elif choice=="2":
            pid=input("Enter product ID: ")
            try:
                qty=int(input("Enter quantity: "))
                if cart.add_item(pid, qty):
                    print("Item added.")
                else:
                    print("Failed to add item")
            except:
                print("Invalid input!")

        elif choice=="3":
            cart.display_cart()

        elif choice=="4":
            pid=input("Enter product ID: ")
            try:
                qty=int(input("Enter new quantity: "))
                if cart.update_quantity(pid, qty):
                    print("Quantity updated")
                else:
                    print("Failed to update")
            except:
                print("Invalid input!")

        elif choice=="5":
            if cart._items=={}:
                print("Cart is empty!")
            else:
                pid=input("Enter product ID to remove: ")
                if cart.remove_item(pid):
                    print("Item removed")
                else:
                    print("Item not found in cart!")

        elif choice=="6":
            if cart._items=={}:
                print("Cart is empty!")
            else:
                cart.display_cart()
                print("Proceeding to checkout...")
                print("Thank you for shopping!")
                cart._items={}
                cart._save_cart_state()

        elif choice=="7":
            print("Exiting... Thank you for shopping!")
            break
        else:
            print("Invalid choice! Please enter a valid number")

run()
