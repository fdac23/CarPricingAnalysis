# RentPricingAnalysis

## Install Instructions 
#### Setup virtual env
Need to create a .env file and add MongoDB token to when one is obtained. This allows access to the database to pull down scraped housing data.
```bash
MONGO_URI = 'mongodb+srv://username:token@cluster0.iwkiwxt.mongodb.net/?retryWrites=true&w=majority'
```
```bash
conda create -n githubwrapped python-3.6 anaconda 
conda activate githubwrapped
```
#### Install requirments
```bash 
pip install -r requirments.txt
```
#### Install GCP 
Go through steps here for your OS / container
- https://cloud.google.com/sdk/docs/install
#### Setup GCP
```bash 
gcloud auth application-default login
gcloud services enable bigquery.googleapis.com
gcloud services list
```

## Project Goals

- Collect current rent prices from Zillow
- Analyze data and see what trends are found
- Develop an ML model to predict rent pricing

## Presentation

<object data="./rentpriceanalysis.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="./rentpriceanalysis.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="./rentpriceanalysis.pdf">Download PDF</a>.</p>
    </embed>
</object>

## Resources
- https://Zillow.com
- https://mongodb.com