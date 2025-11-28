import numpy as np

# Example vectors
x = np.array([2,4,4,5,5,6,6,8,6])
y = np.array([2,4,4,5,5,6,3,5,5])

# Compute correlation matrix
corr_matrix = np.corrcoef(x, y)

# Extract correlation coefficient
corr_xy = corr_matrix[0, 1]

print(f"Correlation coefficient between x and y: {corr_xy}")