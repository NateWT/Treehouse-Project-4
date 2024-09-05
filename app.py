from models import (Base, session,
                    Product, engine,)
from sqlalchemy import select
import csv
from datetime import datetime
import time



def fetch_data():
    stmt = select(Product)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        data = result.fetchall()
        return data


def save_to_csv(data, filename):
    columns = ['product_id', 'Product Name', 'Product Price', 'Product Quantity', 'Date Updated']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for product in data:
            product_name = product[1] 
            product_price = f"${int(product[2]) / 100:.2f}" 
            product_quantity = product[3]
            date_updated = product[4].strftime('%m/%d/%Y') 
            writer.writerow([product_name, product_price, product_quantity, date_updated])
        print('A new backup has been created.')
        time.sleep(1.5)


def clean_price(price_string):
    try:
        price_float = float(price_string.replace('$', ''))
        return int(price_float * 100)
    except ValueError:
        raise ValueError('''
                         \n***** Price Error *****
                         \rThe Price should be a number with the currency symbol 
                         \rEX:  $10.99
                         \rPress enter to try again
                         \r**********************''' )


def product_lookup():
    while True:
        try:
            product_id = int(input('Enter the Product ID you want to view: '))
            product = session.query(Product).filter(Product.product_id == product_id).one_or_none()
            if product:
                print(f'''
                      \nPRODUCT DETAILS
                      \rID: {product.product_id}
                      \rName: {product.product_name}
                      \rPrice: ${int(product.product_price) / 100:.2f} 
                      \rQuantity: {product.product_quantity}
                      \rLast Updated: {product.date_updated.strftime('%m/%d/%Y')}
                      ''')
                time.sleep(1.5)
                break
            else:
                input('''
                      \nProduct not found.
                      \rThat Id does not fall in a valid range
                      \rPress Enter to try agian.''')
        except ValueError:
            print('Invalid Product ID. Please enter a valid number.')



def menu():
    while True:
        print('''
              \nINVENTORY MANAGEMENT
              \rV) View Product Details
              \rA) Add a New Product
              \rB) Create a Backup
              \rE) Exit''')
        choice = input('What would you like to do? ').upper()
        if choice in ['V', 'A', 'B', 'E']:
            return choice
        else:
            input('''
                  \nPlease choose one of the options below
                  \r**** V **** A **** B **** E ****
                  \rPress enter to try again...''')


def clean_date(date_str):
    try:
        date_updated = datetime.strptime(date_str, '%m/%d/%Y')
        return date_updated
    except ValueError:
        print('''
              \nPlease enter a date in the proper format
              \rMonth/Day/Year
              \r1/31/2024''')



def add_csv():
    with open('inventory.csv', newline='', encoding='utf-8') as csvfile:
        data = csv.reader(csvfile)
        next(data) 
        for row in data:
            product_name = row[0]
            product_price = row[1]  
            product_quantity = row[2]
            date_updated = row[3]

            product_price = clean_price(product_price) 
            product_quantity = int(product_quantity)  
            date_updated = clean_date(date_updated)  

            product_in_db = session.query(Product).filter(Product.product_name == product_name).one_or_none()
            if product_in_db is None:
                new_product = Product(
                    product_name=product_name,
                    product_price=product_price,
                    product_quantity=product_quantity,
                    date_updated=date_updated)
                session.add(new_product)
            else:
                product_in_db.product_price = product_price
                product_in_db.product_quantity = product_quantity
                product_in_db.date_updated = date_updated
        session.commit()

def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'V':
            # Seach for product by ID
            product_lookup()
        elif choice == 'A':
            # Add new product
            product_name = input('Product Name: ')
            product_price = clean_price(input('Product Price: (ex.$10.99)'))
            product_quantity = int(input('Product Quantity: '))
            date_updated = datetime.today().date()
            product_in_db = session.query(Product).filter(Product.product_name == product_name).one_or_none()
            if product_in_db is None:
                new_product = Product(
                    product_name=product_name,
                    product_price=product_price,
                    product_quantity=product_quantity,
                    date_updated=date_updated)
                session.add(new_product)
            else:
                product_in_db.product_price = product_price
                product_in_db.product_quantity = product_quantity
                product_in_db.date_updated = date_updated
            session.commit()
        elif choice == 'B':
            # Backup
            data = fetch_data()
            save_to_csv(data, 'products_backup.csv')
        else:
            print('GOODBYE')
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()