from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            print(productLink)
            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.content, "html.parser")
            prod = prod_html.find('div', {'class': '_29OxBi'}).h1.span.get_text()
            data = prod_html.find('div', {'class': 'swINJg _3nrCtb'})
            parent = data.find_parent()
            url = parent.get('href')
            url = 'https://www.flipkart.com' + url
            req_data = requests.get(url)
            all_reviews = bs(req_data.content, 'html.parser')
            pages = all_reviews.find_all('div', {'class': '_2zg3yZ _3KSYCY'})  # extracts all the pages url info
            page = int(pages[0].span.get_text().split()[-1])
            if page > 3:
                page = 3
            reviews = []
            for i in range(0, page):  # we iterate through all the pages
                commentboxes = all_reviews.find_all('div', {'class': "_1PBCrt"})
                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ", e)

                    mydict = {"Product": prod, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}
                    reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
