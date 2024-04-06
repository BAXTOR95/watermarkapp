import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, colorchooser, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from matplotlib.font_manager import findSystemFonts


class WatermarkApp:
    """
    A desktop application for adding text or logo watermarks to images, built with Tkinter.

    Attributes:
        root (tk.Tk): The root window for the Tkinter application.
        original_image (PIL.Image.Image): The original image loaded by the user.
        preview_image (ImageTk.PhotoImage): The resized image for display in the Tkinter canvas.
        watermarked_image (PIL.Image.Image): The image with the applied watermark.
        scale_x (float): The scale factor for the x-axis to adjust from preview to original size.
        scale_y (float): The scale factor for the y-axis to adjust from preview to original size.
        last_click_x (int): The x-coordinate of the last click on the canvas.
        last_click_y (int): The y-coordinate of the last click on the canvas.
        default_margin_x (int): Default margin from the right edge for watermark placement.
        default_margin_y (int): Default margin from the bottom edge for watermark placement.
        text_color (str): Default color for text watermark.
    """

    ###############################################################################
    #                           Initialization and Setup                          #
    ###############################################################################

    def __init__(self, root):
        """
        Initializes the WatermarkApp application with a given Tkinter root window.

        :param root: The main Tkinter root window.
        """
        self.root = root
        self.setup_ui()

        self.original_image = None
        self.preview_image = None
        self.watermarked_image = None
        self.scale_x = 1  # Initialize scale factors
        self.scale_y = 1
        self.last_click_x = 0
        self.last_click_y = 0
        self.default_margin_x = 30  # Margin from the right edge
        self.default_margin_y = 30  # Margin from the bottom edge
        self.text_color = "#000000"  # Default text color

    def setup_ui(self):
        """
        Sets up the user interface, including buttons, a canvas for image preview, and other widgets.
        """
        self.root.title('Watermark App')
        self.root.geometry('800x600')

        # This frame will hold all the buttons and the canvas, making it easier to center everything together
        self.content_frame = tk.Frame(self.root)
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Configure the root to expand the content_frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Buttons
        self.upload_btn = tk.Button(
            self.content_frame, text='Upload Image', command=self.upload_image
        )
        self.upload_btn.grid(row=0, column=0, padx=10, pady=10)

        self.text_watermark_btn = tk.Button(
            self.content_frame,
            text='Add Text Watermark',
            command=self.open_text_editor,
            state='disabled',
        )
        self.text_watermark_btn.grid(row=0, column=1, padx=10)

        self.logo_watermark_btn = tk.Button(
            self.content_frame,
            text='Add Logo Watermark',
            command=self.add_logo_watermark,
            state='disabled',
        )
        self.logo_watermark_btn.grid(row=0, column=2, padx=10)

        self.save_btn = tk.Button(
            self.content_frame,
            text='Save Image',
            command=self.save_image,
            state='disabled',
        )
        self.save_btn.grid(row=0, column=3, padx=10)

        self.exit_btn = tk.Button(
            self.content_frame, text='Exit App', command=self.exit_app
        )
        self.exit_btn.grid(row=0, column=4, padx=10)

        # Canvas for image preview
        self.canvas = tk.Canvas(
            self.content_frame, width=600, height=400, cursor="cross"
        )
        self.canvas.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        self.canvas.bind(
            '<Button-1>', self.on_canvas_click
        )  # Binding click event to the canvas

        # Adjusting content_frame grid to center its contents
        self.content_frame.grid_rowconfigure(1, weight=1)
        for col in range(
            5
        ):  # Ensuring all columns in content_frame can expand uniformly
            self.content_frame.grid_columnconfigure(col, weight=1)

    ###############################################################################
    #                        Event Handlers and UI Updates                        #
    ###############################################################################

    def on_canvas_click(self, event):
        """
        Handles canvas click events, recording the click position and drawing a marker on the canvas.

        :param event: The event object containing details about the mouse click.
        """
        # Record the click coordinates
        self.last_click_x = event.x
        self.last_click_y = event.y

        # Clear previous markers if any
        self.canvas.delete("click_marker")

        # Draw a small circle as a marker for the click
        radius = 5  # Radius of the circle
        self.canvas.create_oval(
            self.last_click_x - radius,
            self.last_click_y - radius,
            self.last_click_x + radius,
            self.last_click_y + radius,
            outline='red',
            fill='red',
            tags="click_marker",
        )

    def update_text_preview(self, event=None):
        """
        Updates the text preview in the text editor dialog based on user inputs.

        :param event: Optional event parameter for handling events that trigger a preview update.
        """
        # Fetch current values
        current_text = self.watermark_text.get()
        font_family = self.font_family.get()
        font_size = self.font_size.get()
        text_color = (
            self.text_color
        )  # Assuming this gets updated in your color picker method

        # Validate and apply font size
        try:
            font_size = int(font_size)
        except ValueError:
            font_size = 12  # Default to 12 if conversion fails

        # Update preview label
        self.preview_label.config(
            text=current_text if current_text else "Preview Text",
            font=(font_family, font_size),
            fg=text_color,
        )

    def update_preview(self):
        """
        Updates the preview canvas with the watermarked image.
        """
        if self.watermarked_image:
            self.preview_image = self.get_resized_image_for_preview(
                self.watermarked_image
            )
            self.canvas.create_image(300, 200, image=self.preview_image)

    ###############################################################################
    #                 User Actions: Image Upload and Watermarking                 #
    ###############################################################################

    def upload_image(self):
        """
        Opens a file dialog for the user to select an image, then attempts to load and display the image.
        Includes error handling and user feedback for a better user experience.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.preview_image = self.get_resized_image_for_preview(
                    self.original_image
                )
                self.canvas.create_image(
                    300, 200, anchor=tk.CENTER, image=self.preview_image
                )
                self.enable_buttons()
                tk.messagebox.showinfo(
                    "Image Uploaded",
                    "Click on the preview image to select the watermark position.",
                )
            except Exception as e:
                tk.messagebox.showerror(
                    "Image Upload Error",
                    f"Failed to load the image: {e}\nPlease ensure the file is a valid image format.",
                )
        else:
            tk.messagebox.showinfo(
                "No Image Selected",
                "No image was selected. Please choose an image file to upload.",
            )

    def add_logo_watermark(self):
        """
        Initiates the process for adding a logo watermark by opening a file dialog to select an image.
        """
        logo_path = filedialog.askopenfilename()
        if logo_path and self.original_image:
            logo_image = Image.open(logo_path)
            self.apply_logo_watermark(logo_image)

    def apply_text_watermark(self):
        """
        Applies the text watermark to the image at the position specified by the last canvas click or a default position.

        :param use_last_click: Determines whether to use the last click position for placing the watermark.
        """
        if self.original_image:
            # Retrieve the entered text, font size, and selected font family from the text editor
            text = self.watermark_text.get()
            font_family = self.font_family.get()
            font_path = self.get_font_path(font_family)  # Get the full path of the font

            try:
                font_size = int(self.font_size.get())
            except ValueError:
                font_size = 36  # Fallback to a default size if conversion fails

            # Proceed only if there's text to apply
            if text.strip():
                watermark_image = self.original_image.copy()
                draw = ImageDraw.Draw(watermark_image)

                try:
                    font = ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    font = ImageFont.load_default()
                    print(f"Failed to load font {font_family} at path {font_path}: {e}")

                ## Using getbbox() to get text dimensions
                text_bbox = font.getbbox(text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                if self.last_click_x > 0 and self.last_click_y > 0:
                    # Adjust coordinates based on scale factors
                    adjusted_click_x = (
                        self.last_click_x - 125
                    )  # Adjusting for x padding
                    adjusted_click_y = self.last_click_y  # Y doesn't need adjustment
                    # Apply scale factors
                    original_x = int(adjusted_click_x * self.scale_x)
                    original_y = int(adjusted_click_y * self.scale_y)
                    # Adjust for text dimensions to ensure visibility within the image
                    position = (
                        max(original_x - text_width, 0),
                        max(original_y - text_height, 0),
                    )
                else:
                    # Use a default position, adjusted for scale and text size
                    position = (
                        watermark_image.width - text_width - self.default_margin_x,
                        watermark_image.height - text_height - self.default_margin_y,
                    )

                # Apply the watermark text with the chosen font size and color
                draw.text(position, text, fill=self.text_color, font=font)

                # Clear previous markers if any
                self.canvas.delete("click_marker")

                # Update the image preview
                self.watermarked_image = watermark_image
                self.update_preview()

                # Optionally, close the text editor window if it's open
                if self.text_editor.winfo_exists():
                    self.text_editor.destroy()

    def apply_logo_watermark(self, logo_image):
        """
        Applies the logo watermark to the image, using the last click position or a default position.

        :param logo_image: The PIL image object of the logo to be used as a watermark.
        :param use_last_click: Determines whether to use the last click position for placing the watermark.
        """
        if self.original_image:
            # Copy the original image
            watermark_image = self.original_image.copy()

            # Resize logo to be a fixed proportion of the original image's width
            base_width = int(watermark_image.width * 0.1)
            wpercent = base_width / float(logo_image.size[0])
            hsize = int((float(logo_image.size[1]) * float(wpercent)))
            logo_image = logo_image.resize(
                (base_width, hsize), Image.Resampling.LANCZOS
            )

            if self.last_click_x > 0 and self.last_click_y > 0:
                # Adjusting for the padding due to centering the preview image
                adjusted_click_x = (
                    self.last_click_x - 125
                )  # Account for left padding in x
                adjusted_click_y = self.last_click_y  # No adjustment needed for y

                # Apply scale factors to adjust coordinates
                original_x = int(adjusted_click_x * self.scale_x)
                original_y = int(adjusted_click_y * self.scale_y)

                # Adjust logo position to be centered on the click
                position = (
                    original_x - logo_image.width // 2,
                    original_y - logo_image.height // 2,
                )
            else:
                # Default position calculation for a logo might consider the logo's dimensions to avoid clipping
                logo_width, logo_height = logo_image.size
                position = (
                    watermark_image.width - logo_width - self.default_margin_x,
                    watermark_image.height - logo_height - self.default_margin_y,
                )

            # Apply logo watermark
            watermark_image.paste(logo_image, position, logo_image)

            # Clear previous markers if any
            self.canvas.delete("click_marker")

            # Update the watermarked image and the preview
            self.watermarked_image = watermark_image
            self.update_preview()

    def save_image(self):
        """
        Saves the watermarked image to a file, opening a save dialog for the user to choose the file location and name.
        Enhancements include error handling and user feedback.
        """
        if self.watermarked_image:
            save_path = filedialog.asksaveasfilename(defaultextension='.png')
            if save_path:
                try:
                    self.watermarked_image.save(save_path)
                    tk.messagebox.showinfo(
                        "Save Successful", "The image has been saved successfully."
                    )
                except Exception as e:
                    tk.messagebox.showerror(
                        "Save Error", f"Failed to save the image: {e}"
                    )
            else:
                tk.messagebox.showwarning(
                    "Save Cancelled", "Image save operation was cancelled."
                )
        else:
            tk.messagebox.showwarning(
                "No Image", "There is no image to save. Please add a watermark first."
            )

    ###############################################################################
    #               Text Watermark Customization and Color Selection              #
    ###############################################################################

    def open_text_editor(self):
        """
        Opens a text editor dialog where the user can enter text for the watermark and customize its appearance.
        """
        self.text_editor = tk.Toplevel(self.root)
        self.text_editor.title("Text Watermark Editor")

        # Get available font families
        fonts = list(tkFont.families())
        fonts.sort()  # Sort the font list alphabetically

        # Frame for text and font size inputs
        input_frame = tk.Frame(self.text_editor)
        input_frame.pack(fill='x', padx=5, pady=5)

        # Configuring the text entry
        tk.Label(input_frame, text="Text:").pack(side='left', padx=5)
        self.watermark_text = tk.Entry(input_frame)
        self.watermark_text.pack(side='left', expand=True, fill='x', padx=5)
        self.watermark_text.bind(
            "<KeyRelease>", self.update_text_preview
        )  # Update on text change

        # Configuring the font size input
        tk.Label(input_frame, text="Font Size:").pack(side='left', padx=5)
        self.font_size = tk.Spinbox(input_frame, from_=10, to_=72, width=5)
        self.font_size.pack(side='left', padx=5)
        self.font_size.bind(
            "<KeyRelease>", self.update_text_preview
        )  # Update on size change

        # Font selection
        tk.Label(input_frame, text="Font:").pack(side='left', padx=5)
        self.font_family = ttk.Combobox(input_frame, values=fonts, state="readonly")
        self.font_family.pack(side='left', padx=5)
        self.font_family.set("Arial")  # Set a default font
        self.font_family.bind("<<ComboboxSelected>>", self.update_text_preview)

        # Preview label
        self.preview_label = tk.Label(
            self.text_editor, text="Preview Text", font=("Arial", 12)
        )
        self.preview_label.pack(pady=5)

        # Frame for buttons
        button_frame = tk.Frame(self.text_editor)
        button_frame.pack(fill='x', padx=5, pady=5)

        self.color_button = tk.Button(
            button_frame, text="Choose Color", command=self.choose_text_color
        )
        self.color_button.pack(side='left', fill='x', expand=True, padx=5)

        self.apply_button = tk.Button(
            button_frame,
            text="Apply Text",
            command=lambda: self.apply_text_watermark(True),
        )
        self.apply_button.pack(side='left', fill='x', expand=True, padx=5)

        self.text_editor.transient(self.root)  # Make the window modal
        self.text_editor.grab_set()
        self.root.wait_window(self.text_editor)

    def choose_text_color(self):
        """
        Opens a color chooser dialog for selecting the color of the text watermark.
        """
        # Open color chooser dialog and update text_color
        color_code = colorchooser.askcolor(
            title="Choose color", initialcolor=self.text_color
        )
        if color_code[1]:
            self.text_color = color_code[1]
            self.update_text_preview()

    ###############################################################################
    #                               Utility Functions                             #
    ###############################################################################

    def get_font_path(self, font_name):
        """
        Attempts to find the full path of a given font name installed on the system.

        :param font_name: The name of the font to find.
        :return: The path to the font file or None if not found.
        """
        # List all system fonts
        fonts_list = findSystemFonts()
        # Filter out fonts that match the selected font_name
        for font_path in fonts_list:
            if font_name.lower() in os.path.basename(font_path).lower():
                return font_path
        # Fallback if no matching font found
        return None

    def get_resized_image_for_preview(self, img):
        """
        Resizes the given image to fit within the preview canvas, maintaining aspect ratio.

        :param img: The PIL.Image.Image object to resize.
        :return: A resized ImageTk.PhotoImage object for Tkinter display.
        """
        # Create a copy to avoid modifying the original image
        img_copy = img.copy()

        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate the resize factor to fit the image in the canvas
        max_size = (canvas_width, canvas_height)
        img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Store scale factors
        self.scale_x = img.width / img_copy.width
        self.scale_y = img.height / img_copy.height

        # Convert to PhotoImage for Tkinter compatibility
        return ImageTk.PhotoImage(img_copy)

    def enable_buttons(self):
        """
        Enables the buttons for adding watermarks and saving the image after an image is uploaded.
        """
        self.text_watermark_btn['state'] = 'normal'
        self.logo_watermark_btn['state'] = 'normal'
        self.save_btn['state'] = 'normal'

    ###############################################################################
    #                                Application Exit                             #
    ###############################################################################

    def exit_app(self):
        """
        Closes the application window and exits the app.
        """
        self.root.quit()  # This stops the tkinter loop
        self.root.destroy()  # This ensures the app window is closed


if __name__ == '__main__':
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
