import os

try:
    from PIL import Image
except ImportError:
    print("Pillow library is not installed. Please install it by running: pip install Pillow")
    exit(1)

def remove_white_bg(img_path):
    print(f"Processing {img_path}...")
    try:
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            # Check if pixel is white or very light gray
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                # Make transparent
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        img.save(img_path, "PNG")
        print(f"Successfully removed white background from {img_path}!")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

if __name__ == "__main__":
    # Get absolute path to the logo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "components", "logo.png")
    
    if os.path.exists(logo_path):
        remove_white_bg(logo_path)
    else:
        print(f"Logo not found at {logo_path}")
