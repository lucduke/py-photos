import piexif

def get_exif_data(file_path):
    try:
        exif_dict = piexif.load(file_path)
        return str(exif_dict)
    except Exception as e:
        return str(e)
