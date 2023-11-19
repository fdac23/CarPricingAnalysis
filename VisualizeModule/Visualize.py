import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from wordcloud import WordCloud, STOPWORDS
import pymongo
import folium

class Visualize:
    def __init__(self):
        visuals_folder_path = os.path.join(os.path.dirname(__file__), "Visuals")

        if not os.path.exists(visuals_folder_path):
            os.makedirs(visuals_folder_path)
        
        load_dotenv()
        MONGO_URI = os.getenv('MONGO_URI')
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client['zipCodes']

    def SavePlot(self, zipcode, name, plot, p_type="plt"):
        subdirectory_path = os.path.join(os.path.dirname(__file__), "Visuals", str(zipcode))

        if not os.path.exists(subdirectory_path):
            os.makedirs(subdirectory_path)

        if p_type == "plt":
            plot.savefig(os.path.join(subdirectory_path, name))
        elif p_type == "folio":
            plot.save(os.path.join(subdirectory_path, name))

    def CheckCollectionExistence(self, zipcode):
        coll_list = self.db.list_collection_names()
        for z in coll_list:
            if z == zipcode: return True
        return False

    def CorrelationHeatMap(self, zipcode: str):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({'zipCode': zipcode}, {'_id': 0, 'price': 1, 'numBeds': 1, 'numBaths': 1, 'area': 1})

        df = pd.DataFrame(list(cursor))
        correlation_matrix = df.corr()

        plt.figure(figsize=(8, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title(f'Correlation Heatmap for Zip Code {zipcode}')
        self.SavePlot(zipcode, "heatmap.png", plt, "plt")
    
    def GeoSpatialMap(self, zipcode):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'latitude': 1, 'longitude': 1, 'price': 1, 'numBeds': 1, 'numBaths': 1})

        data = pd.DataFrame(list(cursor))
        m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

        for _, row in data.iterrows():
            folium.Marker([row['latitude'], row['longitude']],
                        popup=f"Price: ${row['price']} | Beds: {row['numBeds']} | Baths: {row['numBaths']}",
                        icon=folium.Icon(color='blue')).add_to(m)

        html_filename = f'geospatial_map_{zipcode}.html'
        self.SavePlot(zipcode, html_filename, m, "folio")
    
    def ScatterTimeVPrice(self, zipcode):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'timeOnZillow': 1, 'price': 1})

        data = pd.DataFrame(list(cursor))

        plt.figure(figsize=(10, 6))
        plt.scatter(data['timeOnZillow'], data['price'], alpha=0.5)
        plt.title(f'Time on Zillow vs Price for Zip Code {zipcode}')
        plt.xlabel('Time on Zillow (days)')
        plt.ylabel('Price ($)')
        plt.grid(True)
        self.SavePlot(zipcode, "heatmap.png", plt, "plt")

    def AddressWordCloud(self, zipcode, price_threshold=2000):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'address': 1, 'price': 1})

        df = pd.DataFrame(list(cursor))
        filtered_df = df[df['price'] > price_threshold]

        text = ' '.join(filtered_df['address']).lower()

        stop_words = set(['knoxville', 'tn', 'seymour', 'louisville', 'ln', 'ave', 'pike', 'rd', 'apt', 'dr', 'hwy'])
        stop_words = stop_words.union(set(STOPWORDS))

        wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words).generate(text)

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud of Apartment Addresses for Zip Code {zipcode}')
        self.SavePlot(zipcode, "wordcloud.png", plt, "plt")


vis = Visualize()
zipcode = "37920"

#Creates word cloud of address names. Only includes listings of price_threshold and up
vis.AddressWordCloud(zipcode, price_threshold=2000)
#Creates a heatmap based on price, numBedRooms, etc..
vis.CorrelationHeatMap(zipcode)
#Creates a scatter plot showing correlation between time on Zillow and price
vis.ScatterTimeVPrice(zipcode)
#Creates a map with a pin for each address. Pins show price, beds, and baths.
vis.GeoSpatialMap(zipcode)