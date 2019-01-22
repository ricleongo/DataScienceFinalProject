export SPARK_HOME=~/Applications/spark-2.4.0-bin-hadoop2.6
export SPARK_PATH=~/Applications/spark-2.4.0-bin-hadoop2.6
export PYSPARK_DRIVER_PYTHON="jupyter"
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"

#For python 3, You have to add the line below or you will get an error
export PYSPARK_PYTHON=python3
export PYTHONPATH=$PYTHONPATH:./python:$SPARK_PATH/bin/pyspark

alias snotebook='$SPARK_PATH/bin/pyspark --master local[2]'