import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from wordcloud import WordCloud, STOPWORDS
import pymongo
import folium
import math

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
        sns.heatmap(correlation_matrix, annot=True, cmap="YlGnBu")
        plt.title(f'Correlation Heatmap for Zip Code {zipcode}')
        #self.SavePlot(zipcode, "heatmap.png", plt, "plt")
        plt.show()
    
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
        #self.SavePlot(zipcode, "timevprice.png", plt, "plt")
        plt.show()

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
        #self.SavePlot(zipcode, "wordcloud.png", plt, "plt")
        plt.show()

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

            box_data.append(df[feature])

        ax.boxplot(box_data, vert=True, labels=zip_codes)
        
        plt.xlabel('Zip Codes')
        plt.ylabel(feature.capitalize())
        plt.title(f'Box Plot of {feature.capitalize()} for Zip Codes')
        plt.show()
    

    def CorrelationHeatMaps(self, zipcodes):
        num_maps = len(zipcodes)

        # Ensure that there are no more than six heat maps
        if num_maps > 6:
            print("Too many zip codes. Displaying up to six heat maps.")
            zipcodes = zipcodes[:6]
            num_maps = 6

        # Calculate the number of rows and columns for subplots
        num_rows = math.ceil(num_maps / 2)
        num_cols = min(2, num_maps)

        # Adjust for odd number of subplots
        if num_maps % 2 != 0:
            num_cols = 1

        # Create subplots with gridspec_kw
        fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(12, 8), gridspec_kw={'width_ratios': [2] * num_cols})

        for i, zipcode in enumerate(zipcodes):
            row_idx = i // num_cols
            col_idx = i % num_cols

            if num_maps > 1:
                ax = axes[row_idx, col_idx]
            else:
                ax = axes  # When there is only one heatmap

            if not self.CheckCollectionExistence(zipcode):
                print(f"{zipcode} not a collection")
                continue

            collection = self.db[zipcode]
            cursor = collection.find({'zipCode': zipcode}, {'_id': 0, 'price': 1, 'numBeds': 1, 'numBaths': 1, 'area': 1})

            df = pd.DataFrame(list(cursor))
            correlation_matrix = df.corr()

            # Format the correlation matrix values as percentages
            correlation_matrix_percentage = correlation_matrix.applymap(lambda x: f'{x:.2%}')

            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=.5, ax=ax)
            ax.set_title(f'Correlation Heatmap - {zipcode}')

        # Adjust layout and show the plot
        plt.tight_layout()
        plt.show()
