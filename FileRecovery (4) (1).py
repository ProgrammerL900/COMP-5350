#!/usr/bin/python

import math
import os
import sys
import shutil

# Resources: 
# For the file signatures: https://www.garykessler.net/library/file_sigs.html
# For reloacting the files over to the folder RecoveredFiles: https://stackoverflow.com/questions/27545454/python-moving-files-and-directories-from-one-folder-to-another
# For importing and opening the disk image provided: https://datagy.io/python-move-file/
# For issues with getting the file to run: https://stackoverflow.com/questions/5807663/permission-denied-when-launch-python-script-via-bash
# For reference for coding with python: https://github.com/merrymitch/COMP5350/blob/main/Project2/FileRecovery.py

# CHANGE BASED ON WHERE YOU WANT THE FOUND FILES TO GO
# The path is where the disk image or file that you are analysising is.
path = ('/home/sansforensics/Desktop/')
# Below is a location where you want the files to end up. 
RecoveredFiles = ('/home/sansforensics/Desktop/RecoveredFiles/')

# Below are all of the header signatures that were pulled from https://www.garykessler.net/library/file_sigs.html
headers = {'JPG': 'ffd8ff', 'AVI': '52494646', 'MPG': '000001b3', 'PDF': '25504446', 'BMP': '424d', 'GIF87a': '474946383761',  
    'GIF89a': '474946383961', 'GIF87a': '474946383761', 'DOCX': '504b030414000600', 'PNG': '89504e470d0a1a0a'}

# Below are all of the footers that were pulled from https://www.garykessler.net/library/file_sigs.html
footers = {'JPG': 'ffd90', 'GIF': '003b0','MPEG': '000001b7', 'MPGD': '000001b9', 'PDF1': '0d2525454f460d', 'PDF2': '0d0a2525454f460d0a0',
    'PDF3': '0a2525454f460a0', 'PDF4': '0a2525454f460','DOCX': '504b0506', 'PNG': '49454e44ae426082'}

# Below opens the diak image and converts the contents to hexidecimal and returns as 'hex'
def openDiskImage(diskImage):
    diskContents = open(diskImage, 'rb')
    hex = diskContents.read().hex()
    diskContents.close()
    return hex

# Below searches through the hexidecimal from the disk image, extracts the file, and moves the file to a folder called Recovered Files
def project2(diskContents):
    # Initialize the number of files currently found starting at 0 becasue we have not found any files yet. 
    count = 0

    # Go through all of the file signatures that we want to find on the disk
    for head in headers:
        # We need to start looking for the dataArea (possible file locations) at the very beginning of the diskImage
        dataArea = 0 
        pfl = diskContents.find(headers[head])

        # Iterate through the hex as long as there are still headers that have not been found yet
        while pfl != -1:
            # Check for the types of headers. 
            if head == 'JPG':
                if (pfl % 512) == 0:
                    print()
                    count += 1

		            # Check for the footer                    
                    foot = diskContents.find(footers['JPG'], pfl)
                    foot = foot + 3 
                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.jpg', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    jpgFile = 'File' + str(count) + '.jpg'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(jpgFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(jpgFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, jpgFile)
                    try:
                        print('Moving ' + jpgFile + ' to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(jpgFile + ' moved')
                    print()
                    # Move starting search location for the next jpg file to the end of this file so we don't keep coming back to the current file
                    dataArea = foot

                else:
                    dataArea = pfl + 6

            elif head == 'AVI':
                # Check that the signature is at the beginning of a sector and the last part of the head is present 
                if (pfl % 512) == 0 and (diskContents[(pfl + 16):(pfl + 32)] == '415649204c495354'):
                    count += 1
		            # Get the file size which is the next four bytes after the signature (little endian order)
                    info = (str(diskContents[(pfl + 14):(pfl + 16)]) + str(diskContents[(pfl + 12):(pfl + 14)]) +
                        str(diskContents[(pfl + 10):(pfl + 12)]) + str(diskContents[(pfl + 8):(pfl + 10)])) 
                    info = int(info, 16) + 8 
                    # Convert the offsets to a usable format for the extraction
                    sfo = int(pfl / 2)
                    end = sfo + info
		    # Print file information
                    print('File' + str(count) + '.avi', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    aviFile = 'File' + str(count) + '.avi'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(aviFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(aviFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, aviFile)
                    try:
                        print('Moving ' + aviFile + ' to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(aviFile + ' moved')
                    print()
                    dataArea = pfl + info
                else:
                    dataArea = pfl + 32

            elif head == 'MPG':
                
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

		            # Check for one of the footers that mark the end of the file
                    foot = diskContents.find(footers['MPEG'], pfl)
                    if foot == -1:
                        foot = diskContents.find(footers['MPGD'], pfl) 
                    foot = foot + 7
                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2) 
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.mpg', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ") 
                    print('End Offset: ' + str(hex(end)))

                    # Uses the data collected above in order to extract the files using the dd command                    
                    mpgFile = 'File' + str(count) + '.mpg'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(mpgFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(mpgFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, mpgFile)
                    try:
                        print('Moving ' + mpgFile + ' to the folder RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(mpgFile + ' moved')
                    print()
                    dataArea = foot
                else:
                    dataArea = pfl + 8

            elif head == 'PDF':
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

		            # Check for one of the footers that mark the end of the file
                    foot = diskContents.find(footers['PDF1'], pfl)
                    end = 13 
                    if foot == -1: 
                        foot = diskContents.find(footers['PDF2'], pfl) 
                        end = 17 
                    if foot == -1:
                        foot = diskContents.find(footers['PDF3'], pfl) 
                        end = 13 
                    if foot == -1:
                        foot = diskContents.find(footers['PDF4'], pfl) 
                        end = 11
                    end = end + foot

                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(end / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.pdf', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

                    # Uses the data collected above in order to extract the files using the dd command                    
                    pdfFile = 'File' + str(count) + '.pdf'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(pdfFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(pdfFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)
                    
                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, pdfFile)
                    try:
                        print('Moving ' + pdfFile + ' to RecoverdFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(pdfFile + ' moved')
                    print()
                    dataArea = foot
                else:
                    dataArea = pfl + 8

            elif head == 'BMP':
                if (pfl % 512) == 0 and (diskContents[(pfl + 12):(pfl + 20)] == '00000000'):
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

                    # Convert the offsets to a usable format for the extraction and prints the found information which in this case is 
                    # little Endian
                    info = (str(diskContents[(pfl + 10):(pfl + 12)]) + str(diskContents[(pfl + 8):(pfl + 10)]) +
                        str(diskContents[(pfl + 6):(pfl + 8)]) + str(diskContents[(pfl + 4):(pfl + 6)]))
                    info = int(info, 16) # Convert the size from hex to decimal
                    sfo = int(pfl / 2)
                    end = sfo + info
                    # Print file information
                    print('File' + str(count) + '.bmp', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    bmpFile = 'File' + str(count) + '.bmp'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(bmpFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(bmpFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, bmpFile)
                    try:
                        print('Moving ' + bmpFile + ' to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(bmpFile + ' moved')
                    print()
                    dataArea = pfl + info
                else:
                    dataArea = pfl + 4

            elif head == 'DOCX':
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

		            # Check for the footer                    
                    foot = diskContents.find(footers['DOCX'], pfl)
                    foot = foot + 43 

                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.docx', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    docxFile = 'File' + str(count) +  '.docx'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(docxFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)

                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(docxFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, docxFile)
                    try:
                        print('Moving ' + docxFile + ' to Recovered Files')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(docxFile + ' moved')
                    print()
                    dataArea = foot
                else:
                    dataArea = pfl + 16

            elif head == 'GIF87a':
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

		            # Check for the footer                    
                    foot = diskContents.find(footers['GIF'], pfl)
                    foot = foot + 3 
                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.gif', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    gifFile = 'File' + str(count) + 'gif'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(gifFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(gifFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, gifFile)
                    try:
                        print('Moving ' + gifFile + ' to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(gifFile + ' moved')
                    print()
                    dataArea = foot
                else:
                    dataArea = pfl + 12

            elif head == 'GIF89a':
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

                    foot = diskContents.find(footers['GIF'], pfl)
                    foot = foot + 3                   
                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    # Print file information
                    print('File' + str(count) + '.gif', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		            # Below used the information gathered above in the extraction command that we learned 
                    gifFile = 'File' + str(count) + '.gif'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(gifFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum' + str(gifFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, gifFile)
                    try:
                        print('Moving ' + gifFile + 'to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(gifFile + ' moved')
                    print()
                    dataArea = foot
                else:
                    dataArea = pfl + 12
              


            elif head == 'PNG':
                if (pfl % 512) == 0:
                    # In order to keep track of the files we add 1 to the count started earlier.  
                    count += 1

		            # Check for the footer                    
                    foot = diskContents.find(footers['PNG'], pfl)
                    foot = foot + 15 
                    # Convert the offsets to a usable format for the extraction and prints the found information
                    sfo = int(pfl / 2)
                    end = int(math.ceil(foot / 2))
                    info = end - sfo
                    print('File' + str(count) + '.png', end = ', ')
                    print('Start Offset: ' + str(hex(sfo)), end = ", ")
                    print('End Offset: ' + str(hex(end)))

		    # Below used the information gathered above in the extraction command that we learned 
                    pngFile = 'File' + str(count) + '.png'
                    extraction = 'dd if=' + str(sys.argv[1]) + ' of=' + str(pngFile) + ' bs=1 skip=' + str(sfo) + ' count=' + str(info)
                    os.system(extraction)
                    # Below is the command to generate the SHA-256 hash specified in the project discription. 
                    hash = 'sha256sum ' + str(pngFile)
                    print('SHA-256', end = ': ')
                    sys.stdout.flush()  
                    os.system(hash)

                    # Move the recovered file above to a folder named "RecoveredFiles" for ease of viewing
                    #for fileName in os.listdir(RecoveredFiles):
                    target = os.path.join(path, pngFile)
                    try:
                        print('Moving ' + pngFile + ' to RecoveredFiles')
                    except NotADirectoryError:
                        try:
                            os.unlink(target)
                        except FileNotFoundError:
                            pass
                    shutil.move(os.path.join(target), RecoveredFiles)
                    print(pngFile + ' moved')
                    dataArea = foot
                else:
                    dataArea = pfl + 16
            pfl = diskContents.find(headers[head], dataArea)
    print('Total number of files found: ' + str(count))
    print('Recovered files are located in ~/RecoveredFiles')

# Run above methods to find, extract, and move all of the files
def main():
    inputDisk = sys.argv[1]
    diskContents = openDiskImage(inputDisk)
    project2(diskContents)
    
if __name__ == "__main__":
    main()
