### Import our SparkSession so we can use it
from pyspark.sql import SparkSession, SQLContext, functions as F
from pyspark.sql.functions import col, udf, regexp_replace
from pyspark.sql.types import *

### Import machine learning libraries.
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
from pyspark.ml.tuning import TrainValidationSplit, ParamGridBuilder
from pyspark.ml import Pipeline

def get_als_model():
    ### Create our SparkSession, this can take a couple minutes locally
    spark = SparkSession.builder.appName("Review_data_JSON2").config('spark.sql.broadcastTimeout','34000').getOrCreate()

    ### Open the data from review.json
    df_reviews = spark.read.json("data_source/review.json")
    
    ### Take only 192.000 rows from the original review.json.
    ratingsRDD = df_reviews.select("user_id", "business_id", "stars").take(192000)

    df_reviews = spark.createDataFrame(ratingsRDD)

    columns_indexing = ["user_id", "business_id"]

    ### Using StringIndexer to create a category feature for user_id and business_id.
    indexers = [StringIndexer(inputCol=column, outputCol=column+"_index").fit(df_reviews) for column in columns_indexing]

    ### Creating a Pipeline to index two columns from the current dataset.
    pipeline = Pipeline(stages=indexers)

    ### Creating the new DataFrame after encoding user and business Id's.
    df_reviews_prepro = pipeline.fit(df_reviews).transform(df_reviews)

    ### Spliting in training, validation and test datasets.
    (training_review, test_review) = df_reviews_prepro.select("user_id_index","business_id_index","stars").randomSplit([0.8, 0.2])

    ### Creating our ALS prediction model.
    als_model = ALS(userCol="user_id_index", 
                    itemCol="business_id_index", 
                    ratingCol="stars",
                    coldStartStrategy="drop",
                    nonnegative = True
                )

    ### Tuning model
    param_grid = ParamGridBuilder()\
            .addGrid(als_model.rank, [12, 13, 14])\
            .addGrid(als_model.maxIter, [18, 19, 20])\
            .addGrid(als_model.regParam, [.17, .18, .19])\
            .build()

    ### Evaluate as Root Mean Squared Error
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="stars", predictionCol="prediction")

    ### 
    tvs = TrainValidationSplit(
                estimator=als_model,
                estimatorParamMaps=param_grid,
                evaluator=evaluator)


    ### Training the model.
    model = tvs.fit(training_review)

    best_model = model.bestModel

    return best_model

def predict_als_model(model, user_id, business_id):
    review_factor = Row(user_id, business_id)

    predictions = model.transform(review_factor)

    return predictions

