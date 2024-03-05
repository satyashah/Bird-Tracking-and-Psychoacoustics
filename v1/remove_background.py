# Importing Required Modules 
from rembg import remove 
from PIL import Image 

# Store path of the image in the variable input_path 
input_path =  'test_images/bird_tube_pos.jpg'

# Store path of the output image in the variable output_path 
output_path = 'test_images/bird_tube_pos_nobg.png' 

# Processing the image 
input = Image.open(input_path) 

# Removing the background from the given Image 
output = remove(input)

# Displaying the image
output.show()

#Saving the image in the given path 
output.save(output_path) 