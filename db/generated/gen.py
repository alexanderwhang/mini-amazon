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
            balance = uid
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
        print(f'{num_users} users generated')
    return

def gen_sellers():
    sellers = []
    with open('Sellers.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        for uid in range(num_users):
            if fake.random_element(elements=(True, False)):
                sellers.append(uid)
                writer.writerow([uid])
        print('generated sellers')
    return sellers

def gen_products():
    available_pids = {}
    categoriesFile = open('Categories.csv', 'w')
    categories_writer = get_csv_writer(categoriesFile)

    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            user_id = fake.random_int(min=0, max=num_users-1)
            name = fake.sentence(nb_words=4)[:-1]
            nameParts = name.split()
            category = fake.random_element(elements=nameParts)
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
        print(f'{num_purchases} generated')
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
    with open('ProductReviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('product reviews...', end=' ', flush=True)
        for uid, pids in orders.items()
            for pid in pids:
                rating = fake.random_int(min=1, max=5)
                review = fake.sentence(nb_words=4)[:-1]
                writer.writerow([uid, pid, rating, review])
        print('generated reviews')
    return 

def gen_carts(orders):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('carts...', end=' ', flush=True)
        for uid, pids in orders.items()
            id = 0
            for pid in pids:
                quantity = fake.random_int(min=1, max=10)
                timestamp = fake.date_time()
                writer.writerow([id, uid, pid, quantity, timestamp])
                id += 1
        print('generated carts')
    return 
    

if __name__ == "__main__":
    gen_users()
    gen_sellers()

    available_pids = gen_products()
    purchases = gen_purchases(available_pids)
    orders = gen_orders(purchases,available_pids)
    gen_reviews(orders)
    gen_carts(orders)