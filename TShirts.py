import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import io

class TshirtCustomizer:
    def __init__(self, root):
        self.root = root
        self.root.title("T-shirt Customizer")
        self.root.geometry("800x600")
        
        # Default values
        self.tshirt_color = "white"
        self.text = ""
        self.text_color = "black"
        self.text_position = (300, 200)  # Default position for text
        
        # Create canvas for displaying the t-shirt
        self.canvas = tk.Canvas(root, width=600, height=500, bg="lightgray")
        self.canvas.pack(pady=10)
        
        # Create buttons frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        # Create buttons
        tk.Button(button_frame, text="Change T-shirt Color", command=self.change_color).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Add/Change Text", command=self.add_text).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Change Text Color", command=self.change_text_color).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Move Text", command=self.move_text).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Save Design", command=self.save_design).grid(row=0, column=4, padx=5)
        
        # Draw initial t-shirt
        self.draw_tshirt()
        
    def draw_tshirt(self):
        """Draw the t-shirt with current settings on the canvas"""
        # Create a blank image with a light gray background
        img = Image.new("RGB", (600, 500), "lightgray")
        draw = ImageDraw.Draw(img)
        
        # Draw the t-shirt shape
        # Collar
        collar_points = [(250, 50), (350, 50), (330, 80), (270, 80)]
        draw.polygon(collar_points, fill=self.tshirt_color, outline="black")
        
        # Shoulders and body
        body_points = [
            (200, 80),  # Left shoulder outer
            (270, 80),  # Left collar
            (330, 80),  # Right collar
            (400, 80),  # Right shoulder outer
            (450, 200), # Right sleeve end
            (400, 200), # Right sleeve inner
            (400, 400), # Right bottom
            (200, 400), # Left bottom
            (200, 200), # Left sleeve inner
            (150, 200), # Left sleeve end
        ]
        draw.polygon(body_points, fill=self.tshirt_color, outline="black")
        
        # Add text if any
        if self.text:
            try:
                # Try to use a nice font, fall back to default if not available
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except:
                    font = ImageFont.load_default()
                
                draw.text(self.text_position, self.text, fill=self.text_color, font=font)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add text: {str(e)}")
        
        # Convert to PhotoImage and display on canvas
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
    def change_color(self):
        """Open color chooser and update t-shirt color"""
        color = colorchooser.askcolor(title="Choose T-shirt Color")
        if color[1]:  # If a color was chosen (not canceled)
            self.tshirt_color = color[1]
            self.draw_tshirt()
            
    def add_text(self):
        """Prompt for text and add it to the t-shirt"""
        text = simpledialog.askstring("Add Text", "Enter text to add to the t-shirt:", initialvalue=self.text)
        if text is not None:  # None if canceled
            self.text = text
            self.draw_tshirt()
    
    def change_text_color(self):
        """Open color chooser and update text color"""
        if not self.text:
            messagebox.showinfo("Info", "Add some text first!")
            return
            
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:  # If a color was chosen (not canceled)
            self.text_color = color[1]
            self.draw_tshirt()
    
    def move_text(self):
        """Allow user to move text position"""
        if not self.text:
            messagebox.showinfo("Info", "Add some text first!")
            return
            
        def on_click(event):
            self.text_position = (event.x, event.y)
            self.draw_tshirt()
            self.canvas.unbind("<Button-1>")
            messagebox.showinfo("Success", "Text position updated!")
        
        messagebox.showinfo("Move Text", "Click on the t-shirt where you want to position the text.")
        self.canvas.bind("<Button-1>", on_click)
    
    def save_design(self):
        """Save the current design as a PNG file"""
        try:
            # Create image to save
            img = Image.new("RGB", (600, 500), "lightgray")
            draw = ImageDraw.Draw(img)
            
            # Draw the t-shirt shape
            # Collar
            collar_points = [(250, 50), (350, 50), (330, 80), (270, 80)]
            draw.polygon(collar_points, fill=self.tshirt_color, outline="black")
            
            # Shoulders and body
            body_points = [
                (200, 80),  # Left shoulder outer
                (270, 80),  # Left collar
                (330, 80),  # Right collar
                (400, 80),  # Right shoulder outer
                (450, 200), # Right sleeve end
                (400, 200), # Right sleeve inner
                (400, 400), # Right bottom
                (200, 400), # Left bottom
                (200, 200), # Left sleeve inner
                (150, 200), # Left sleeve end
            ]
            draw.polygon(body_points, fill=self.tshirt_color, outline="black")
            
            # Add text if any
            if self.text:
                try:
                    # Try to use a nice font, fall back to default if not available
                    try:
                        font = ImageFont.truetype("arial.ttf", 30)
                    except:
                        font = ImageFont.load_default()
                    
                    draw.text(self.text_position, self.text, fill=self.text_color, font=font)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not add text: {str(e)}")
            
            filename = simpledialog.askstring("Save Design", "Enter a filename:", initialvalue="my_tshirt_design")
            if filename:
                if not filename.endswith('.png'):
                    filename += '.png'
                img.save(filename)
                messagebox.showinfo("Success", f"Design saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save design: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TshirtCustomizer(root)
    root.mainloop()
