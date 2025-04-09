import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from config import get_db_connection

df = pd.read_sql_query('select * from products',con=get_db_connection())


# df1 = pd.read_sql_query('select * ')

print(df)