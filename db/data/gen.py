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
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
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

def gen_reviews(orders):
    with open('Review.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('product reviews...', end=' ', flush=True)
        rev_id = 0
        for uid in orders:
            for pid in orders[uid]:
                if (fake.random_int(min=1,max=3)!=1): #33% chance to write reviews
                    continue
                rating = fake.random_int(min=1, max=5)
                review = fake.sentence(nb_words=4)[:-1]
                timestamp = fake.date_time()
                writer.writerow([rev_id, uid, pid, timestamp, review, rating])
                rev_id+=1
        print('generated reviews')
    return 

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