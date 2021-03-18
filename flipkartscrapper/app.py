# doing necessary imports

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
from multiprocessing import Pool
import threading
import os



app = Flask(__name__)  # initialising the flask app with the name 'app'
_pool = None


@app.route('/', methods=['GET'])
@cross_origin()
def homePage():

    #USR = 'Sriram'
    #PWD = '5121'
    DB_NAME = 'Scapper'
    #CONNECTION_URL = f"mongodb+srv://{USR}:{PWD}@cluster0.ovptx.mongodb.net/{DB_NAME}?retryWrites=true&w=majority"
    # dbConn = pymongo.MongoClient(CONNECTION_URL)

    dbConn = pymongo.MongoClient(os.getenv("MONGODB_URI", 'mongodb://127.0.0.1:27017/Scapper'))

    #user_collection = pymongo.collection.Collection(dbConn, 'user_collection')
    db = dbConn[DB_NAME] # connecting to the database called crawlerDB
    databaseList = db.list_collection_names()
    DocCount = [db[collection].count() for collection in databaseList]
    return render_template("index.html", databases = databaseList, counts=DocCount)

@app.route('/reviews', methods=['POST', 'GET'])  # route with allowed methods as POST and GET
@cross_origin()
def index():
    if request.method == 'POST':

        try:
            searchString = request.form['content'].replace(" ", "") # obtaining the search string entered in the form
            USR = 'Sriram'
            PWD = '5121'
            DB_NAME = 'Scapper'
            CONNECTION_URL = f"mongodb+srv://{USR}:{PWD}@cluster0.ovptx.mongodb.net/{DB_NAME}?retryWrites=true&w=majority"
            dbConn = pymongo.MongoClient(CONNECTION_URL)
            # user_collection = pymongo.collection.Collection(dbConn, 'user_collection')
            db = dbConn[DB_NAME]  # connecting to the database called crawlerDB
            collection = db[searchString]

            test_data = collection.find()
            reviews = []
            for idx, record in enumerate(test_data):
                reviews.append(record)

            #reviews = collection[searchString].find({})  # searching the collection with the name same as the keywor
            if len(reviews) > 500:  # if there is a collection with searched keyword and it has records in it
                return render_template('results.html', reviews=reviews)  # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
                print(flipkart_url)
                uClient = uReq(flipkart_url)  # requesting the webpage from the internet
                flipkartPage = uClient.read()  # reading the webpage
                uClient.close()  # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
                prod_boxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})  # seacrhing for appropriate tag to redirect to the product link
                "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="
                product_pages_link = flipkart_url + "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="
                print(product_pages_link)

                prod_string = flipkart_html.find("span", {"class": "_10Ermr"}).text.split()
                prod_count = int(prod_string[3])
                total_prod_count = int(prod_string[5].replace(',',''))
                print(prod_count)
                #table = db[searchString]  # creating a collection with the same name as search string. Tables and Collections are analogous.
                # filename = searchString+".csv" #  filename to save the details
                # fw = open(filename, "w") # creating a local file to save the details
                # headers = "Product, Customer Name, Rating, Heading, Comment \n" # providing the heading of the columns
                # fw.write(headers) # writing first the headers to file
                #reviews = []  # initializing an empty list for reviews
                #  iterating over the comment section to get the details of customer and their comments
                # finding the HTML section containing the customer comments

                multiple_page_links = [product_pages_link+str(i) for i in range(1,(total_prod_count // prod_count) + 1)]
                for pageLink in multiple_page_links:

                    if len(reviews) > 550:
                        break
                    print(pageLink)
                    client = uReq(pageLink)
                    page = client.read()
                    client.close()
                    page_html = bs(page, 'html.parser')
                    product_boxes = page_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                    print(len(product_boxes))
                    del product_boxes[0:3]
                    del product_boxes[-4:]
                    print(len(product_boxes))

                    for prod_box in product_boxes:
                        productLink = "https://www.flipkart.com" + prod_box.div.div.div.a['href']  # extracting the actual product link
                        print(productLink)
                        prodRes = requests.get(productLink)  # getting the product page from server
                        prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
                        main_box = prod_html.find('div', {'class': '_1YokD2 _3Mn1Gg col-8-12'})

                        offer_box = main_box.find('div', {'class': 'XUp0WS'})
                        desc_box = main_box.find('div', {'class': '_3nkT-2'})

                        prod_spects = [item.text for item in main_box.find_all('td', {'class': '_1hKmbr colcol - 3 - 12'})]
                        prod_spects_content = [item.text for item in main_box.find_all('td', {'class': 'URwL2wcol col-9-12'})]
                        try:
                            product_name = main_box.find('h1', {'class': 'yhB1nd'}).text

                        except:
                            product_name = 'No Name'

                        try:
                            product_rating = main_box.find('div', {'class': '_3LWZlK'}).text

                        except:
                            product_rating = 'No Rating'

                        try:
                            product_price = main_box.find('div', {'class': "_30jeq3 _16Jk6d"}).text
                        except:
                            product_price = "No Price Available"
                        try:
                            discount = main_box.find('div', {'class': '_3Ay6Sb _31Dcoz'}).span.text
                        except:
                            discount = "No Discount"
                        try:
                            description = desc_box.find('p').text
                        except:
                            description = "No description available"
                        try:
                            available_offers = [offer.text for offer in offer_box.find_all('span', {'class': ''})]
                        except:
                            available_offers = "No offers available"
                        try:
                            highlights = [item.text for item in main_box.find_all('li', {'class': '_21Ahn-'})]
                        except:
                            highlights = "No highlights"
                        try:
                            specifications = dict(zip(prod_spects, prod_spects_content))
                        except:
                            specifications = "No specifications available"
                        try:
                            payment_options = [item.text for item in main_box.find_all('li', {'class': '_1Ma4bX'})]
                            #payment_options = [item.text for item in main_box.dev.ul]
                        except:
                            payment_options = "Cash on Delivery"

                        # fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                        mydict = {"Product Name": product_name,
                                  "Product Rating": product_rating,
                                  "Product Price": product_price,
                                  "Discount": discount,
                                  "Description": description,
                                  "Available Offers": available_offers,
                                  "Highlights": highlights,
                                  "Specifications": specifications,
                                  "Payment Options": payment_options
                                  }
                        x = collection.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                        reviews.append(mydict)
                        # reviews.append(mydict)  # appending the comments to the review list
                return render_template('results.html', reviews=reviews)  # showing the review to the user
        except:
            #return 'something is wrong'
            searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form

            USR = 'Sriram'
            PWD = '5121'
            DB_NAME = 'Scapper'
            CONNECTION_URL = f"mongodb+srv://{USR}:{PWD}@cluster0.ovptx.mongodb.net/{DB_NAME}?retryWrites=true&w=majority"
            dbConn = pymongo.MongoClient(CONNECTION_URL)
            # user_collection = pymongo.collection.Collection(dbConn, 'user_collection')
            db = dbConn[DB_NAME]  # connecting to the database called crawlerDB
            collection = db[searchString]

            test_data = collection.find()
            reviews = []
            for idx, record in enumerate(test_data):
                reviews.append(record)
            return render_template('results.html', reviews=reviews)
    else:
        return render_template('index.html')


if __name__ == "__main__":

    threading.Thread(targer=app.run(port=8000, debug=True)).start() # running the app on the local machine on port 8000
