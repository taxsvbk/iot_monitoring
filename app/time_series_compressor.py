import pandas as pd
import numpy as np
from sklearn.decomposition import DictionaryLearning
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.metrics import mean_squared_error
import sqlite3

class TimeSeriesCompressor:

    # Initialization
    def __init__(self, csv_file_path, segment_length=20, n_atoms=10, n_nonzero_coefs=5, db_path='iot_data.db'):
        self.csv_file_path = csv_file_path
        self.segment_length = segment_length
        self.n_atoms = n_atoms
        self.n_nonzero_coefs = n_nonzero_coefs
        self.db_path = db_path
        self.time_series_data = None
        self.dictionary = None
        self.sparse_codes = None
        self.compressed_data = None

    # Load data from .csv file
    def load_data(self):
        data = pd.read_csv(self.csv_file_path)
        temperature_data = data['T2M'].values
        humidity_data = data['QV2M'].values
        self.time_series_data = np.vstack((temperature_data, humidity_data))

    # Segment the data
    def segment_data(self):
        num_series, num_points = self.time_series_data.shape
        segments = []
        for i in range(num_series):
            for j in range(0, num_points, self.segment_length):
                segment = self.time_series_data[i, j:j + self.segment_length]
                if len(segment) == self.segment_length:  # Only include full-length segments
                    segments.append(segment)
        return np.array(segments)

    # Learn the dictionary based on segmented data
    def learn_dictionary(self, segments):
        dict_learn = DictionaryLearning(n_components=self.n_atoms, fit_algorithm='lars', transform_algorithm='omp')
        self.dictionary = dict_learn.fit(segments).components_

    # Perform sparse coding
    def perform_sparse_coding(self, segments):
        omp = OrthogonalMatchingPursuit(n_nonzero_coefs=self.n_nonzero_coefs)
        sparse_codes = []
        for segment in segments:
            sparse_code = omp.fit(self.dictionary.T, segment).coef_
            sparse_codes.append(sparse_code)
        self.sparse_codes = np.array(sparse_codes)

    # Compute the Correlation Matrix
    def compute_correlation_matrix(self):
        return np.corrcoef(self.time_series_data)

    # Perform compression
    def compress(self, threshold=0.8):
        corr_matrix = self.compute_correlation_matrix()
        compressed_data = []
        for i in range(self.time_series_data.shape[0]):
            max_corr = np.max(corr_matrix[i][i+1:]) if i + 1 < corr_matrix.shape[0] else 0

            if max_corr < threshold:
                reconstructed_segment = np.sum(self.sparse_codes[i][:, np.newaxis] * self.dictionary, axis=0)
                compressed_data.append(reconstructed_segment)
            else:
                correlated_series_idx = np.argmax(corr_matrix[i][i+1:]) + (i+1)
                scale_factor = np.dot(self.time_series_data[i], self.time_series_data[correlated_series_idx]) / np.dot(self.time_series_data[correlated_series_idx], self.time_series_data[correlated_series_idx])
                compressed_data.append(scale_factor * self.time_series_data[correlated_series_idx])
        self.compressed_data = np.array(compressed_data)
        return self.compressed_data

    # Decompress the data
    def decompress(self):
        decompressed_data = []
        for series in self.compressed_data:
            if isinstance(series, np.ndarray):
                decompressed_data.append(np.dot(self.dictionary, series))
            else:
                decompressed_data.append(series)
        return np.array(decompressed_data)

    # Reassemble the segmented data
    def reassemble_segments(self, segments, num_series, num_points):
        reassembled_data = np.zeros((num_series, num_points))
        seg_idx = 0
        for i in range(num_series):
            for j in range(0, num_points, self.segment_length):
                if seg_idx < len(segments):
                    reassembled_data[i, j:j+self.segment_length] = segments[seg_idx]
                    seg_idx += 1
        return reassembled_data

    # Evaluate compression performance
    def evaluate_compression(self, original_data, decompressed_segments):
        num_series, num_points = original_data.shape
        decompressed_data = self.reassemble_segments(decompressed_segments, num_series, num_points)
        mse = mean_squared_error(original_data.flatten(), decompressed_data.flatten())
        compression_ratio = original_data.size / decompressed_segments.size
        return mse, compression_ratio

    # Store results in database
    def store_results(self, mse, compression_ratio):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS compressed_data
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      original BLOB,
                      compressed BLOB,
                      mse REAL,
                      compression_ratio REAL)''')

        # Insert data into temporary table (for demonstration purposes)
        original_data_blob = self.time_series_data.tobytes()
        compressed_data_blob = self.compressed_data.tobytes()

        c.execute('''INSERT INTO compressed_data (original, compressed, mse, compression_ratio)
                     VALUES (?, ?, ?, ?)''',
                  (original_data_blob, compressed_data_blob, mse, compression_ratio))

        # Commit and close the connection to the database
        conn.commit()
        conn.close()

    # Run the compression process
    def run_compression(self):
        self.load_data()
        segments = self.segment_data()
        self.learn_dictionary(segments)
        self.perform_sparse_coding(segments)
        compressed_data = self.compress()
        mse, compression_ratio = self.evaluate_compression(self.time_series_data, compressed_data)
        self.store_results(mse, compression_ratio)
        return mse, compression_ratio

    # Run the decompression process
    def run_decompression(self):
        decompressed_data = self.decompress()
        return decompressed_data