from flask import Flask, jsonify, render_template, request, send_from_directory
import json

### Import our SparkSession so we can use it
from pyspark.sql import SparkSession, SQLContext, functions as F
from pyspark.sql.functions import col, udf, regexp_replace
from pyspark.sql.types import *
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.ml import Pipeline

app = Flask(__name__, static_url_path = "")

@app.route("/api/user")
def user():
    return send_from_directory('data_source', 'user.json')

@app.route("/api/business")
def business():
    return send_from_directory('data_source', 'business.json')

@app.route("/api/checkin")
def checkin():
    return send_from_directory('data_source', 'checkin.json')

@app.route("/api/photo")
def photo():
    return send_from_directory('data_source', 'photo.json')

@app.route("/api/review")
def review():
    return send_from_directory('data_source', 'review.json')

@app.route("/api/tip")
def tip():
    return send_from_directory('data_source', 'tip.json')

@app.route("/api/als")
def als():

    ### Create our SparkSession, this can take a couple minutes locally
    spark = SparkSession.builder.appName("Review_Data_JSON").config('spark.sql.broadcastTimeout','34000').getOrCreate()
    
    ### Open the data from review.json
    df_reviews = spark.read.json("data_source/review.json")
    
    ### Select the feaatures we will use for our model
    df_reviews_model = df_reviews.select("user_id", "business_id", "stars")

    columns_indexing = ["user_id", "business_id"]

    ### Using StringIndexer to create a category feature for user_id and business_id.
    indexers = [StringIndexer(inputCol=column, outputCol=column+"_index").fit(df_reviews_model) for column in columns_indexing]

    ### Creating a Pipeline to index two columns from the current dataset.
    pipeline = Pipeline(stages=indexers)

    ### Creating the new DataFrame after encoding user and business Id's.
    df_reviews_prepro = pipeline.fit(df_reviews_model).transform(df_reviews_model)

    ### Spliting in training, validation and test datasets.
    (training_review, test_review) = df_reviews_prepro.randomSplit([0.4, 0.1])

    ### Creating our ALS prediction model.
    als_model = ALS(maxIter=5, regParam=0.1, 
                    userCol="user_id_index", 
                    itemCol="business_id_index", 
                    ratingCol="stars",
                    coldStartStrategy="drop")

    ### Training the model.
    # als_trained = als_model.fit(training_review)

    # als_trained.show()

    return ""


if __name__ == '__main__':
    app.run(debug=True)