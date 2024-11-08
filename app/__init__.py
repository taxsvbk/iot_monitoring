from time_series_compressor import TimeSeriesCompressor

# Remember to change path to data21.csv directory
# Remember to change path to data21.csv directory
# Remember to change path to data21.csv directory
csv_file_path = 'C:/Users/LAPTOP/Downloads/data21.csv'
compressor = TimeSeriesCompressor(csv_file_path)

mse, compression_ratio = compressor.run_compression()
print(f"Compression Ratio: {compression_ratio}")
print(f"Mean Squared Error: {mse}")

decompressed_data = compressor.run_decompression()
print("Decompressed data:", decompressed_data)
