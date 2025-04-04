import pyautogui
import pytesseract
import time
from PIL import Image, ImageEnhance, ImageOps
import re

# Configuration - Adjust these based on your screen
BLUE_GEM_POS = (885, 700)  # Replace with blue gem button coordinates
CLICK_TO_SKIP_POS = (800, 450)  # Safe spot to skip animation
SCREENSHOT_REGION = (840, 520, 290, 140)  # Extended to capture 4 stat slots

# Gold loot thresholds
MIN_TOTAL_GOLD_LOOT = 80  # Stop when total Gold Loot is 60% or higher
GOLD_LOOT_VALUES = {20, 40, 50}  # Allowed gold loot values

# Initialize
pyautogui.PAUSE = 0.1  # Small delay between actions
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path

def preprocess_image(image):
    """Enhance image for better OCR."""
    gray = image.convert('L')
    enhanced = ImageEnhance.Contrast(gray).enhance(3.0)
    inverted = ImageOps.invert(enhanced)
    bw = ImageOps.autocontrast(inverted)
    return bw

def extract_stats():
    """Capture screen and extract gold loot percentages."""
    screenshot = pyautogui.screenshot(region=SCREENSHOT_REGION)
    processed = preprocess_image(screenshot)

    # OCR recognition with improved config
    text = pytesseract.image_to_string(processed, config='--psm 6 --oem 3')
    print(f"\U0001F4DD OCR Raw Output: {text}")  # Debugging: Print raw text

    # Show screenshot for debug (uncomment to use debugger)
    # processed.show(title="OCR Debug Image") 

    # Clean up and extract values
    cleaned_text = text.replace('4', '+')

    # Extract gold loot values
    gold_matches = re.findall(r'\+?(\d{2,3})%?\s*Gold\s*loot', cleaned_text, re.IGNORECASE)
    current_roll_values = [int(match) for match in gold_matches if int(match) in GOLD_LOOT_VALUES]
    return current_roll_values

def should_stop(gold_values):
    """Check if the current roll meets the gold loot threshold."""
    total_gold = sum(gold_values)

    if total_gold >= MIN_TOTAL_GOLD_LOOT:
        print(f"✅ Found desired stats: {gold_values} (Total: {total_gold}%)")
        return True
    return False

def reroll():
    """Perform one reroll cycle."""
    pyautogui.click(BLUE_GEM_POS)  # Click blue gem
    time.sleep(0.3)  # Wait for animation
    pyautogui.click(CLICK_TO_SKIP_POS)  # Skip animation
    time.sleep(0.2)  # Brief pause

def main():
    print("Starting auto-reroller... (Press Ctrl+C to stop)")
    time.sleep(3)  # 3-second delay before script starts
    try:
        while True:
            reroll()
            time.sleep(0.5)  # Small delay to avoid spam clicking

            gold_values = extract_stats()  # Fresh OCR per roll
            print(f"\U0001F50D Current gold loot stats: {gold_values}")

            if should_stop(gold_values):
                break  # Stop only if the current roll meets the threshold

    except KeyboardInterrupt:
        print("\n⏹ Stopped by user.")

if __name__ == "__main__":
    main()
