import os
import pathlib
os.add_dll_directory("F:\\Organizer\\vcpkg\\installed\\x64-windows\\bin")
import pyheif
import piexif

heif_file = pyheif.read("F:\\Google Photos\\Takeout\\Takeout\\Google Photos\\Photos from 2019\\IMG_0115.HEIC")
for metadata in heif_file.metadata or []:
    if metadata['type'] == 'Exif':
        exif_dict = piexif.load(metadata['data'])
        print(exif_dict)