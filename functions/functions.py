# Import our SparkSession so we can use it
from pyspark.sql import SparkSession, SQLContext, functions as F
from pyspark.sql.functions import col

# Create our SparkSession, this can take a couple minutes locally
spark = SparkSession.builder.appName("BusinessJSON").config('spark.sql.broadcastTimeout',-1).getOrCreate()
# df_business = spark.read.json("../data_source/business_review/part-00000-a6c5280a-4adf-4f1d-b37f-cbfd7dc9a6c6-c000.json").orderBy(df_business.state.desc())
# df_users = spark.read.json("data_source/user.json")
df_business = spark.read.json("data_source/business.json")


def login(phoneNumber):
    print(phoneNumber)

    names = [
        {'phone': '+16783603191', 'name': 'Karem', 'email': 'karemolav1215@gmail.com'},
        {'phone': '+16789861827', 'name': 'Juan', 'email': 'ricleongo@gmail.com'},
        {'phone': '+19123323875', 'name': 'Ruth', 'email': 'rutholliday@gmail.com'},
        {'phone': '+19199462157', 'name': 'Carlos', 'email': 'carlos.aizpurua@gapac.com'}
    ]

    userItem = [item for item in names if item["phone"] == phoneNumber]

    if len(userItem) > 0:
        username = userItem[0]["name"]
        email = userItem[0]["email"]
    else:
        username = "Sir"
        email = ""

    return "Email is {} and User is {}".format(username, email)

def getRestaurantList(watson_values):

    if len(watson_values.split(",")) > 1:
        category = watson_values.split(",")[0].strip()
        review = watson_values.split(",")[1].strip()
        city = watson_values.split(",")[2].strip()
    else:
        category = "rent a car"
        review = ""
        city = "Atlanta"

    cat_filter = f"%{category}%"

    restaurants = df_business.filter((col("stars") >= 4) & (col("categories").like(cat_filter)) &(col("state") == 'NV') & (col("city") == 'North Las Vegas')).groupBy("categories", "name", "stars", "hours").count().take(3)

    top_rest = ', '.join([restaurant.name for restaurant in restaurants])
    response_ = f"Most recomended restaurants, in the city of {city} are {top_rest}"

    print(response_)

    return response_
