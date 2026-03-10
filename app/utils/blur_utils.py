import cv2
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
import os

def check_blur_with_histogram(image_path, histogram_path, threshold=100.0):
    """
    Detect blur using Laplacian variance and save ONLY histogram image.
    Returns variance, threshold, and histogram filename.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or cannot be opened.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()

    # Plot histogram only
    plt.figure(figsize=(8, 6))
    plt.hist(laplacian.ravel(), bins=50, range=(-100, 100), color='blue', alpha=0.7)
    plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
    plt.axvline(x=variance, color='red', linestyle='-', linewidth=2, label=f"Variance={variance:.2f}")
    plt.title("Laplacian Histogram")
    plt.xlabel("Laplacian Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.tight_layout()
    plt.savefig(histogram_path)
    plt.close()

    return variance, threshold, os.path.basename(image_path), os.path.basename(histogram_path)
