import open3d as o3d
import numpy as np
from PIL import Image 
import cv2
import os
import sys
from tkinter import Tk, filedialog

class Create_mp4:
    def __init__(self, stl_file, colour=[0.192,0.212,0.248], scale_ratio=0.5): 
        # Loading in STL Object 
        self.stl_file = stl_file 
        
        # Create the visualization object
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name='STL Viewer', width=900, height=900)
        self.render = self.vis.get_render_option()
        self.render.background_color = [1,1,1]
        self.render.light_on = True
        self.render.mesh_show_back_face = True
        
        # Creating Mesh 
        self.mesh = o3d.io.read_triangle_mesh(stl_file)
        self.mesh.compute_vertex_normals()
        self.mesh.paint_uniform_color(colour)

        self.geometry = o3d.geometry.TriangleMesh(self.mesh)  
        # Don't want object to close to the screen 
        self.geometry.scale(scale_ratio, center=self.mesh.get_center())
        # Just gotta keep things certain for simplicity 
        self.center = np.array(self.mesh.get_center())
        # Note that x and z can be change however you like and y is used to rotate things 
        # x = -80 -> has a slight tilt upwards to see the top part of the object
        # y -> Be used to rotate the image 
        R = self.mesh.get_rotation_matrix_from_xyz((np.radians(-80),np.radians(0),np.radians(0)))
        self.geometry.rotate(R, self.center)
        
        self.vis.add_geometry(self.geometry)
        self.images = []

    def produce_images(self): 
        print("Production of images. Starting...")
        for i in range(360): 
            # Clear the visualizer and add the mesh at the current rotation
            self.vis.clear_geometries()
            # The rotation addeds on to each other so you don't want to set your x to -80 degrees or anything. 
            R = self.mesh.get_rotation_matrix_from_xyz((0,np.radians(1),0))
            self.geometry = self.geometry.rotate(R, self.center)
            self.vis.add_geometry(self.geometry)
            
            # Render the scene to an image
            self.vis.poll_events()
            self.vis.update_renderer()
            self.images.append(self.vis.capture_screen_float_buffer(False))

        print("Finished!!!")

    def convert_to_mp4(self,output_path, speed):
        try:
            print("Converting Images to MP4")
            height, width = 900, 900
            num_frames = 360
            frame_duration = num_frames / speed
            fps =  num_frames/frame_duration 
            
            # Create the video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Write each image to the video
            for image in self.images:
                img_np = np.asarray(image)
                img = Image.fromarray((img_np * 255).astype(np.uint8))
                out.write(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
            
            out.release()
            print(f"Images converted to MP4 and saved to: {output_path}")
        except Exception as e:
            print(f"Error converting images: {e}")
    
    def destroy(self): 
        # Release the visualizer
        self.vis.destroy_window() 

if __name__ == "__main__": 
    # 1st. Grab a STL File 
    # Create a Tkinter window (hidden)
    root = Tk()
    root.withdraw()
    # Prompt the user to select an STL file
    selected_file = filedialog.askopenfilename(
        title="Select an STL file",
        filetypes=[("STL files", "*.stl")]
    )

    # Check if a file was selected
    if selected_file:
        print(f"You selected: {selected_file}")
        # Prompt the user to select an output directory
        output_dir = filedialog.askdirectory(title="Select output directory", initialdir=os.path.dirname(selected_file))

        # Prompt the user to enter an output file name
        output_file = filedialog.asksaveasfilename(
            initialdir=output_dir,
            title="Save MP4 file",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")]
        )

        if output_file:
            create_mp4 = Create_mp4(selected_file)
            create_mp4.produce_images()
            # Speed can be fiddle with 
            # Higher value will make it go quicker 
            create_mp4.convert_to_mp4(output_file, speed=30)
            create_mp4.destroy()
    else:
        print("No file selected.")     
    