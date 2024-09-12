import pandas as pd

# 加载Parquet文件
data = pd.read_parquet('parquet_example.parquet')

# 将Parquet文件转换为CSV
data.to_csv('converted_data.csv', index=False)

# 打印转换后的CSV数据
print(pd.read_csv('converted_data.csv').head())
