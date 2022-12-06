from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 100
num_categories = 20
num_products = 2000
num_orders = 100

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

#generates num_users users. 50% chance that the user is a seller. 
#returns the user_ids of sellers as a list of integers
def gen_users():
    sellers = []
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address']
            seller = False
            balance = uid
            if fake.random_int(min=0, max=1) == 1:
                sellers.append(uid)
                seller = True
            writer.writerow([uid, email, password, firstname, lastname, address, seller, balance])
        print(f'{num_users} users generated')
    return sellers

#generates num_products products. Returns list of product ids
#Randomly assigns a seller to the product
#price is randomly generated between $0.00 and $500.99
#also generates a random category for the products -> this is added to the Categories table
#all images are "image not found"
#50% chance that item is available. if so, quantity is zero
def gen_products(sellers):
    available_pids = {}
    categoriesFile = open('Categories.csv', 'w')
    categories = set()
    categories_writer = get_csv_writer(categoriesFile)
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            user_id = fake.random_element(elements=sellers)
            name = fake.sentence(nb_words=4)[:-1]
            nameParts = name.split()
            category = fake.random_element(elements=nameParts)
            if category not in categories:
                categories.add(category)
                categories_writer.writerow([category])
            description = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(min=0,max=500))}.{fake.random_int(min=0,max=99):02}'
            imageurl = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwWxCMRrygVbR-7SLPx5N44x4I6BQjDDzWVAvEUZI3&s"
            quantity = 0
            available = fake.random_element(elements=('true', 'false'))
            
            ### prob should not be a column, can calc it when needed
            rating = f'{str(fake.random_int(max=5))}.{fake.random_int(max=9)}'
                
            if available == 'true':
                quantity = fake.random_int(min=1,max=1000)
            available_pids[pid] = float(price)
            writer.writerow([pid, user_id, category, name, description, price, imageurl, quantity, available, rating])
        print(f'{num_products} products generated')
        categoriesFile.close()
    return available_pids

#generates 1-10 purchases for each order. returns a map<order_id, list of (product_id, quantity) tuples>
#randomly selects products from available_pids
#randomly generate quantity bought and fulfillment_status
def gen_purchases(available_pids):
    purchases = {}
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_orders):
            purchases[id] = []
            for purchase in range(fake.random_int(min=1, max=10)):
                pid = fake.random_element(elements=available_pids.keys())
                quantity = fake.random_int(min=1, max=10)
                fStatus = fake.random_element(elements=('ordered', 'shipped', 'delivered'))
                purchases[id].append((pid,quantity))
                writer.writerow([id, pid, quantity, fStatus])
        print(f'purchases generated')
    return purchases

#given purchases and product_ids, return map<user_id, list of pids>
#purchases are randomly assigned to users

def gen_orders(purchases, products):
    orders = {}
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('orders...', end=' ', flush=True)
        for order_id, purchase_list in purchases.items():
            uid = fake.random_int(min=0, max=num_users-1)
            if uid not in orders:
                orders[uid] = []
            timestamp = fake.date_time()
            

            total_items = 0
            total_price = 0
            for pid, quantity in purchase_list:
                total_items += quantity
                total_price += (quantity * products[pid])
                orders[uid].append(pid)
            

            writer.writerow([order_id, uid, total_price, total_items, timestamp])
        print('generated orders')
    return orders

#given map<user_id, list of pids>
#33% chance the user writes a review for a pid
def gen_reviews(orders):
    with open('Review.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('product reviews...', end=' ', flush=True)
        rev_id = 0
        for uid in orders:
            for pid in orders[uid]:
                if (fake.random_int(min=1,max=2)!=1): #33% chance to write reviews
                    continue
                rating = fake.random_int(min=1, max=5)
                review = fake.sentence(nb_words=4)[:-1]
                timestamp = fake.date_time()
                imageurl = ""
                writer.writerow([rev_id, uid, pid, timestamp, review, rating, imageurl])
                rev_id+=1
        print('generated reviews')
    return 

#generates fake carts (items that a user has not yet purchased).
#extrapolated from the generated orders<user_id, list pids>
def gen_carts(orders):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('carts...', end=' ', flush=True)
        id = 0
        for uid, pids in orders.items():
            for pid in pids:
                quantity = fake.random_int(min=1, max=10)
                timestamp = fake.date_time()
                writer.writerow([id, uid, pid, quantity, timestamp])
                id += 1
        print('generated carts')
    return 

#generates saved carts
def gen_save(orders):
    with open('Save.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('save...', end=' ', flush=True)
        for uid, pids in orders.items():
            for pid in pids:
                timestamp = fake.date_time()
                writer.writerow([uid, pid, timestamp])
        print('generated carts')
    return 

if __name__ == "__main__":
    sellers = gen_users()

    available_pids = gen_products(sellers)

    purchases = gen_purchases(available_pids)
    orders = gen_orders(purchases,available_pids)
    gen_reviews(orders)
    gen_carts(orders)
    gen_save(orders)