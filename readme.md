# Georgia Tech Bootcamp Data Science Final Project


### Team Members
* Karem Olavarry
* Ruth Holliday
* Carlos Aizpurua
* Juan León


# Yelp Recomendations Voice bot
![alt text](images/yelp.png)

From [Yelp public datasets academy webpage](https://www.yelp.com/dataset) we stared to make some analysis about how we can make this information more available to everybody without the need to open a computer or even stop to open a browser from a smart phone.

The purpose of this final project is to present the characteristics of Machine Learning and how could be implemented in the day by day of a current user. 


# The architecture of the application is design as:
![alt text](images/IBM_WATSON.jpg)



# Machine Learning Implemented

### Spark Collaborative Filtering (ALS)

ALS is a model we are using to create predictions of restaurants, hotels or rent a cars based on the ratings from other users.

This image shows an example of predicting of the user's rating using collaborative filtering. At first, people rate different items (like videos, images, games). After that, the system is making predictions about user's rating for an item, which the user hasn't rated yet. These predictions are built upon the existing ratings of other users, who have similar ratings with the active user. For instance, in our case the system has made a prediction, that the active user won't like the video.

![alt text](images/Collaborative_filtering.gif)



```python
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


### Create our SparkSession, this can take a couple minutes locally
spark = SparkSession.builder.appName("Review_data_JSON1").config('spark.sql.broadcastTimeout','34000').getOrCreate()

```


```python
### Open the data from review.json
df_reviews = spark.read.json("../data_source/review.json")
df_reviews.printSchema()
```

    root
     |-- business_id: string (nullable = true)
     |-- cool: long (nullable = true)
     |-- date: string (nullable = true)
     |-- funny: long (nullable = true)
     |-- review_id: string (nullable = true)
     |-- stars: double (nullable = true)
     |-- text: string (nullable = true)
     |-- useful: long (nullable = true)
     |-- user_id: string (nullable = true)
    



```python
### Take only 192.000 rows from the original review.json.
ratingsRDD = df_reviews.select("user_id", "business_id", "stars").take(192000)

df_reviews = spark.createDataFrame(ratingsRDD)
```


```python
### Check the schema of the DtaFrame.
df_reviews.printSchema()

```

    root
     |-- user_id: string (nullable = true)
     |-- business_id: string (nullable = true)
     |-- stars: double (nullable = true)
    



```python
### Shows the definition of the table.
df_reviews.describe().show()

```

    +-------+--------------------+--------------------+------------------+
    |summary|             user_id|         business_id|             stars|
    +-------+--------------------+--------------------+------------------+
    |  count|              192000|              192000|            192000|
    |   mean|                null|                null|3.7318854166666666|
    | stddev|                null|                null|1.4569912639557216|
    |    min|---1lKK3aKOuomHnw...|--Gc998IMjLn8yr-H...|               1.0|
    |    max|zzrwygYbYs-NgFEe-...|zzwhN7x37nyjP0ZM8...|               5.0|
    +-------+--------------------+--------------------+------------------+
    



```python
columns_indexing = ["user_id", "business_id"]

### Using StringIndexer to create a category feature for user_id and business_id.
indexers = [StringIndexer(inputCol=column, outputCol=column+"_index").fit(df_reviews) for column in columns_indexing]

### Creating a Pipeline to index two columns from the current dataset.
pipeline = Pipeline(stages=indexers)

### Creating the new DataFrame after encoding user and business Id's.
df_reviews_prepro = pipeline.fit(df_reviews).transform(df_reviews)

### Show results.
df_reviews_prepro.show()

```

    +--------------------+--------------------+-----+-------------+-----------------+
    |             user_id|         business_id|stars|user_id_index|business_id_index|
    +--------------------+--------------------+-----+-------------+-----------------+
    |hG7b0MtEbXx5QzbzE...|ujmEBvifdJM6h6RLv...|  1.0|      21237.0|            448.0|
    |yXQM5uF2jS6es16SJ...|NZnhc2sEQy3RmzKTZ...|  5.0|     131602.0|           1828.0|
    |n6-Gk65cPZL6Uz8qR...|WTqjgwHlXbSFevF32...|  5.0|      82215.0|           2691.0|
    |dacAIZ6fTM6mqwW5u...|ikCg8xy5JIg_NGPx-...|  5.0|      88932.0|           6871.0|
    |ssoyf2_x0EQMed6fg...|b1b1eb3uo-w561D0Z...|  1.0|      66574.0|           1725.0|
    |w31MKYsNFMrjhWxxA...|eU_713ec6fTGNO4Be...|  4.0|      33069.0|            859.0|
    |jlu4CztcSxrKx56ba...|3fw2X5bZYeW9xCz_z...|  3.0|       1079.0|           1344.0|
    |d6xvYpyzcfbF_AZ8v...|zvO-PJCpNk4fgAVUn...|  1.0|      21864.0|           4911.0|
    |sG_h0dIzTKWa3Q6fm...|b2jN2mm9Wf3RcrZCg...|  2.0|     113518.0|           2310.0|
    |nMeCE5-xsdleyxYuN...|oxwGyA17NL6c5t1Et...|  3.0|       5090.0|             92.0|
    |FIk4lQQu1eTe2EpzQ...|8mIrX_LrOnAqWsB5J...|  4.0|        128.0|             20.0|
    |-mA3-1mN4JIEkqOtd...|mRUVMJkUGxrByzMQ2...|  1.0|      99832.0|           2002.0|
    |GYNnVehQeXjty0xH7...|FxLfqxdYPA6Z85PFK...|  4.0|      81998.0|           3318.0|
    |bAhqAPoWaZYcyYi7b...|LUN6swQYa4xJKaM_U...|  4.0|      70503.0|            685.0|
    |TpyOT5E16YASd7EWj...|AakkkTuGZA2KBodKi...|  1.0|       4721.0|           2406.0|
    |NJlxGtouq06hhC7sS...|YvrylyuWgbP90RgMq...|  5.0|     122920.0|           1631.0|
    |86J5DwcFk4f4In1Vx...|NyLYY8q1-H3hfsTwu...|  4.0|     112106.0|             94.0|
    |JSrP-dUmLlwZiI7Dp...|cHdJXLlKNWixBXpDw...|  3.0|       3226.0|             15.0|
    |6Fz_nus_OG4gar721...|6lj2BJ4tJeu7db5as...|  5.0|      56548.0|           1172.0|
    |_N7Ndn29bpll_961o...|y-Iw6dZflNix4BdwI...|  3.0|      17085.0|            383.0|
    +--------------------+--------------------+-----+-------------+-----------------+
    only showing top 20 rows
    



```python
### Spliting in training, validation and test datasets.
(training_review, test_review) = df_reviews_prepro.select("user_id_index","business_id_index","stars").randomSplit([0.8, 0.2])


```


```python
### Validation and Test datasets should have 80% of the data each one.
training_review.printSchema()

```

    root
     |-- user_id_index: double (nullable = false)
     |-- business_id_index: double (nullable = false)
     |-- stars: double (nullable = true)
    



```python
### Training data is expected as 20% of the total of records.
test_review.show()

```


```python
### Creating our ALS prediction model.
als_model = ALS(userCol="user_id_index", 
                itemCol="business_id_index", 
                ratingCol="stars",
                coldStartStrategy="drop",
                nonnegative = True
               )

```


```python
### Tuning model
param_grid = ParamGridBuilder()\
            .addGrid(als_model.rank, [12, 13, 14])\
            .addGrid(als_model.maxIter, [18, 19, 20])\
            .addGrid(als_model.regParam, [.17, .18, .19])\
            .build()

```


```python
### Evaluate as Root Mean Squared Error
evaluator = RegressionEvaluator(metricName="rmse", labelCol="stars", predictionCol="prediction")

```


```python
### Training Validation Split.
tvs = TrainValidationSplit(
            estimator=als_model,
            estimatorParamMaps=param_grid,
            evaluator=evaluator)

```


```python
### Training the model.
model = tvs.fit(training_review)

```


```python
### Get the best model based on the ranks trained previously with TrainingValidationSplit
best_model = model.bestModel
best_model
```




    ALS_fb94b9294a15




```python
### From the best model predict the test_review dataset 20% of data from review.json
predictions = best_model.transform(test_review)
predictions
```




    DataFrame[user_id_index: double, business_id_index: double, stars: double, prediction: float]




```python
### Root mean error squeare validates the margin error.
rmes = evaluator.evaluate(predictions)
rmes
```




    1.720059351756456




```python
### Print all the results.
print("RMSE: {}".format(str(rmes)))
print("Rank: {}".format(best_model.rank))
print("MaxInter: {}".format(best_model._java_obj.parent().getMaxIter() ))
print("RMSE: {}".format(best_model._java_obj.parent().getRegParam() ))
```

    RMSE: 1.720059351756456
    Rank: 14
    MaxInter: 20
    RMSE: 0.19



```python
### Show the dataset predicted and contrast the current stars with the predicted stars.
predictions.show()
```

    +-------------+-----------------+-----+----------+
    |user_id_index|business_id_index|stars|prediction|
    +-------------+-----------------+-----+----------+
    |       3744.0|            148.0|  4.0| 2.7375278|
    |        665.0|            148.0|  4.0|  4.125117|
    |        163.0|            148.0|  4.0| 3.1874242|
    |      15204.0|            148.0|  1.0| 1.4403815|
    |      19899.0|            148.0|  4.0| 3.0769997|
    |      13816.0|            148.0|  1.0| 3.8332148|
    |       1187.0|            148.0|  5.0| 3.8611677|
    |       7943.0|            148.0|  5.0| 3.7071636|
    |       1522.0|            463.0|  2.0| 3.1605837|
    |       3056.0|            463.0|  5.0| 2.7985938|
    |      19341.0|            463.0|  1.0| 1.8810831|
    |       1203.0|            463.0|  4.0| 2.2243347|
    |       9017.0|            463.0|  5.0| 1.1739373|
    |        950.0|            471.0|  5.0| 3.8654156|
    |      12442.0|            471.0|  5.0| 3.3523858|
    |       2741.0|            471.0|  5.0| 4.1526866|
    |       3066.0|            471.0|  4.0| 4.3686895|
    |       1239.0|            471.0|  5.0| 3.0525534|
    |      19386.0|            471.0|  5.0| 2.6479685|
    |       8132.0|            496.0|  5.0|  1.788928|
    +-------------+-----------------+-----+----------+
    only showing top 20 rows
    



```python

```
