import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from wordcloud import WordCloud, STOPWORDS
import pymongo
import folium
import math
from IPython.display import display

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

    #Takes a single zipcode string as an argument. Produces one heatmap
    def CorrelationHeatMap(self, zipcode: str):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({'zipCode': zipcode}, {'_id': 0, 'price': 1, 'numBeds': 1, 'numBaths': 1, 'area': 1})

        df = pd.DataFrame(list(cursor))
        correlation_matrix = df.corr()

        plt.figure(figsize=(8, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap="YlGnBu")
        plt.title(f'Correlation Heatmap for Zip Code {zipcode}')
        #self.SavePlot(zipcode, "heatmap.png", plt, "plt")
        plt.show()
    

    #Takes a single zipcode string as an argument
    #Can take a feature argument to show ScatterVFeature, but other features not so interesting
    def ScatterTimeVPrice(self, zipcode, feature="price"):
        my_dict = {"area": "SqFt", "price": "($)", "numBeds": "", "numBaths": ""}
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'timeOnZillow': 1, feature: 1})

        data = pd.DataFrame(list(cursor))
        data['timeOnZillow_days'] = data['timeOnZillow'] / (24 * 60 * 60 * 1000)

        plt.figure(figsize=(10, 6))
        plt.scatter(data['timeOnZillow_days'], data[feature], alpha=0.5)
        plt.title(f'Time on Zillow vs {feature.capitalize()} for Zip Code {zipcode}')
        plt.xlabel('Time on Zillow (days)')
        plt.ylabel(f'{feature.capitalize()} {my_dict[feature]}')
        plt.grid(True)
        #self.SavePlot(zipcode, "timevprice.png", plt, "plt")
        plt.show()


    #Shows a word cloud of street names, takes a single string zipcode as an argument.
    #Optional price thresholds variables. Default will show most expensive addresses
    def AddressWordCloud(self, zipcode, price_threshold_lb=2000, price_threshold_ub=10000):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'address': 1, 'price': 1})

        df = pd.DataFrame(list(cursor))
        filtered_df = df[df['price'] > price_threshold_lb]
        filtered_df = filtered_df[filtered_df['price'] < price_threshold_ub]

        text = ' '.join(filtered_df['address']).lower()

        stop_words = set(['cir', 'knoxville', 'tn', 'seymour', 'louisville', 'ln', 'ave', 'pike', 'rd', 'apt', 'dr', 'hwy', 'w', 'st', 'se', 'ave'])
        stop_words = stop_words.union(set(STOPWORDS))

        wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words).generate(text)

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud of Apartment Addresses for Zip Code {zipcode}')
        #self.SavePlot(zipcode, "wordcloud.png", plt, "plt")
        plt.show()

    #Takes a list as an argument. List must have at least 1 zip code string
    #Takes a feature as an argument
    def FeatureBoxPlot(self, zip_codes, feature):
        numerical_columns = ['price', 'numBeds', 'numBaths', 'area']

        if feature not in numerical_columns:
            raise ValueError("Invalid feature. Please choose from 'price', 'numBeds', 'numBaths', or 'area'.")

        fig, ax = plt.subplots(figsize=(10, 8))

        box_data = []
        for i, zip_code in enumerate(zip_codes):
            if not self.CheckCollectionExistence(zip_code):
                print(f"{zip_code} not a collection")
                return
            
            collection = self.db[zip_code]

            cursor = collection.find({}, {'_id': 0, feature: 1})

            df = pd.DataFrame(list(cursor))
            df = df.dropna(subset=[feature])

            box_data.append(df[feature])

        ax.boxplot(box_data, vert=True, labels=zip_codes)
        
        plt.xlabel('Zip Codes')
        plt.ylabel(feature.capitalize())
        plt.title(f'Box Plot of {feature.capitalize()} for Zip Codes')
        plt.show()
    
    #Takes a list with two zipcode strings as an argument.
    #Displays heatmaps side by side
    def CorrelationHeatMaps(self, zipcodes):
        if len(zipcodes) > 2:
            print("Please no more than 2 zip codes.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        for i, zipcode in enumerate(zipcodes):
            if not self.CheckCollectionExistence(zipcode):
                print(f"{zipcode} not a collection")
                continue

            collection = self.db[zipcode]
            cursor = collection.find({"zipCode": zipcode}, {"_id": 0, "price": 1, "numBeds": 1, "numBaths": 1, "area": 1})

            df = pd.DataFrame(list(cursor))
            correlation_matrix = df.corr()

            sns.heatmap(correlation_matrix, annot=True, cmap="YlGnBu", linewidths=.5, ax=axes[i])
            axes[i].set_title(f"Correlation Heatmap - {zipcode}")

        plt.tight_layout()
        plt.show()


    #Takes a single zip code string as an argument
    def GeoSpatialMap(self, zipcode):
        if not self.CheckCollectionExistence(zipcode):
            print(f"{zipcode} not a collection")
            return
        
        collection = self.db[zipcode]
        cursor = collection.find({}, {'_id': 0, 'latitude': 1, 'longitude': 1, 'price': 1, 'numBeds': 1, 'numBaths': 1})

        data = pd.DataFrame(list(cursor))

        # Define price ranges and corresponding colors
        price_ranges = [(0, 999), (1000, 1499), (1500, 1999), (2000, 2499), (2500, 2999), (3000, float('inf'))]
        colors = ['gray', 'blue', 'green', 'orange', 'red', 'purple']

        m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

        for _, row in data.iterrows():
            color = 'gray'
            for i, (lower, upper) in enumerate(price_ranges):
                if lower <= row['price'] <= upper:
                    color = colors[i]
                    break

            folium.Marker([row['latitude'], row['longitude']],
                        popup=f"Price: ${row['price']} | Beds: {row['numBeds']} | Baths: {row['numBaths']}",
                        icon=folium.Icon(color=color)).add_to(m)
            
        legend_html = """
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: 190px; 
                        background-color: white; border: 2px solid black; z-index:9999;
                        font-size:14px;">
            <p style="margin: 5px;"><b>Legend</b></p>
            <p style="margin: 5px; color: #333333;">$0 - $999</p>
            <p style="margin: 5px; color: blue;">$1000 - $1499</p>
            <p style="margin: 5px; color: green;">$1500 - $1999</p>
            <p style="margin: 5px; color: orange;">$2000 - $2499</p>
            <p style="margin: 5px; color: red;">$2500 - $2999</p>
            <p style="margin: 5px; color: purple;">$3000+</p>
            </div>
        """

        m.get_root().html.add_child(folium.Element(legend_html))
        display(m)


    
