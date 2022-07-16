import os
from PIL import Image
from PIL.ExifTags import TAGS
from PIL import UnidentifiedImageError
import imagehash
import datetime
import sys
import hashlib
import sqlite3
import os
import pathlib
os.add_dll_directory("F:\\Organizer\\vcpkg\\installed\\x64-windows\\bin")
import pyheif
from tqdm import tqdm

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

def get_md5(file):
	md5 = hashlib.md5()

	with open(file, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)

	return md5


def main():
	
	filesProcessed = 0
	filesFound = 0
	imagesFound = 0
	moviesFound = 0
	heicFound = 0
	duplicatesFound = 0

	dirName = "F:\\Google Photos\\Takeout\\Takeout\\Google Photos\\Photos from 2019"
	
	# Get the list of all files in directory tree at given path
	listOfFiles = list()

	for (dirpath, dirnames, filenames) in os.walk(dirName):
		listOfFiles += [os.path.join(dirpath, file) for file in filenames]
		
	filesFound = len(listOfFiles)
	con = sqlite3.connect('./pictures.db')
	# Print the files    
	for elem in tqdm(listOfFiles):
		#print(elem)
		'''
		Logic flow:
		0) Is it a filetype we want to track? 
		1) Do we have a record of this file?
		2) Is it an image?
		3) If so, let's process
		'''
		fileExtension = pathlib.Path(elem).suffix
		if fileExtension in [".MOV", ".JPG", ".JPEG", ".PNG", ".HEIC",".MP4"]:
			isImage = True
			image = None
			try: 
				#Try to open file as an image to trigger excpetion for non-images
				image = Image.open(elem)
				imagesFound = imagesFound+1
				is_image = True
			except UnidentifiedImageError:
				is_image = False
				
				if fileExtension == '.MOV':
					moviesFound = moviesFound+1
				if fileExtension == '.HEIC':
					heif_file = pyheif.read(elem)
					print(heif_file.metadata)
					image = Image.frombytes(
						heif_file.mode, 
						heif_file.size, 
						heif_file.data,
						"raw",
						heif_file.mode,
						heif_file.stride,
						)
					heicFound = heicFound+1
					is_image = True
				pass
			
			#Compute md5 hash of file
			md5_hash = get_md5(elem)
			cur = con.cursor()
			cur.execute("SELECT * from pictures WHERE path = ? AND file_hash = ?", (elem, md5_hash.hexdigest()))

			rows = cur.fetchall()

			#print(len(rows))
			if len(rows)==0:
				filesProcessed = filesProcessed+1
				fileExtension = pathlib.Path(elem).suffix
				creationDate = datetime.datetime.fromtimestamp(os.path.getctime(elem))
				modifyDate = datetime.datetime.fromtimestamp(os.path.getmtime(elem))
				#No matching path and/or file hash, let's do the expensive stuff
				if is_image:
					exifData = image.getexif()

					
					if(exifData.get(306) is not None):
						exifDate = datetime.datetime.strptime(exifData.get(306),'%Y:%m:%d %H:%M:%S')
					else:
						exifDate = ''

					image_hash = imagehash.dhash(image)
					cur.execute("INSERT INTO pictures(path, file_hash, perceptual_hash, exif_date, create_date, mod_date, ext) VALUES (?, ?, ?, ?, ?, ?, ?)", (elem, md5_hash.hexdigest(), str(image_hash), exifDate, creationDate, modifyDate, fileExtension))
				else:
					cur.execute("INSERT INTO pictures(path, file_hash, create_date, mod_date, ext) VALUES (?, ?, ?, ?, ?)", (elem, md5_hash.hexdigest(), creationDate, modifyDate, fileExtension))

			else:
				duplicatesFound = duplicatesFound+1
			con.commit()

		
		
	print(f'Files found: {filesFound}')		
	print(f'Images found: {imagesFound}')
	print(f'Images processed: {filesProcessed}')
	print(f'Already processed: {duplicatesFound}')
	print(f'Movies found: {moviesFound}')
	print(f'HEIC found: {heicFound}')

		
		
		
if __name__ == '__main__':
	main()