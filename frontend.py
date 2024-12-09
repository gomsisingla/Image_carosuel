import os
import shutil
import tempfile
import atexit
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from plyer import filechooser
import cv2
import numpy as np
from PIL import Image as PILImage

BACKEND_URL = "http://127.0.0.1:5000"

class ImageEditorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Temporary directory for intermediate files
        self.temp_dir = tempfile.mkdtemp()
        atexit.register(self.cleanup_temp_files)  # Ensure cleanup on exit
        



    def cleanup_temp_files(self):
        """Clean up temporary files when the app exits."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        self.message_label = Label(text="", size_hint=(1, 0.03), color=(1, 1, 1, 1), halign="center", valign="middle")
        self.main_layout.add_widget(self.message_label)

        # Add Images Button
        add_images_button = Button(text="Add Images", size_hint=(1, 0.1))
        add_images_button.bind(on_press=self.open_gallery)
        self.main_layout.add_widget(add_images_button)

        # Main Image Carousel
        self.carousel = Carousel(direction="right", size_hint=(1, 0.4))
        self.main_layout.add_widget(self.carousel)

        # Thumbnails Scroll View
        self.scrollview = ScrollView(size_hint=(1, 0.15), do_scroll_x=True, do_scroll_y=False)
        self.thumbnail_layout = GridLayout(cols=10, size_hint=(None, 1), height=150, spacing=10, padding=10)
        self.thumbnail_layout.bind(minimum_width=self.thumbnail_layout.setter("width"))
        self.scrollview.add_widget(self.thumbnail_layout)
        self.main_layout.add_widget(self.scrollview)

        # Art Styles Scroll View
        self.style_scroll = ScrollView(size_hint=(1, 0.1), do_scroll_x=True, do_scroll_y=False)
        self.style_layout = GridLayout(cols=8, size_hint=(None, 1), spacing=10, padding=10)
        self.style_layout.bind(minimum_width=self.style_layout.setter("width"))
        self.style_scroll.add_widget(self.style_layout)
        self.main_layout.add_widget(self.style_scroll)

        # Color Adjustment Sliders
        self.color_controls = BoxLayout(orientation="horizontal", size_hint=(1, 0.15))
        self.add_color_sliders()
        self.main_layout.add_widget(self.color_controls)

        # Save Image Button
        save_image_button = Button(text="Save Image", size_hint=(1, 0.1))
        save_image_button.bind(on_press=self.save_image)
        self.main_layout.add_widget(save_image_button)

        # Track images
        self.image_paths = []  # Original image paths
        self.modified_images = {}  # Map: original path -> modified path

        # Predefined Art Styles
        self.art_styles = ["Original", "Van Gogh", "Pop Art", "Sketch", "Painting", "Pointillism", "Surreal", "Cubism"]
        self.add_art_style_buttons()

        return self.main_layout

    def open_gallery(self, instance):
        filechooser.open_file(
            filters=[("Images", "*.png;*.jpg;*.jpeg")],
            multiple=True,
            on_selection=self.add_images
        )

    def add_images(self, selection):
        if not selection:
            return

        for image_path in selection:
            if os.path.exists(image_path) and os.path.isfile(image_path):
                # Upload image to backend
                self.upload_image_to_backend(image_path)
                self.image_paths.append(image_path)
                self.add_image_to_carousel(image_path)
                self.add_image_to_thumbnails(image_path)

    def upload_image_to_backend(self, image_path):
        """Send the selected image to the backend for upload."""
        url = BACKEND_URL + "/upload"
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f)}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            print("Image uploaded successfully:", response.json())
        else:
            print("Error uploading image:", response.text)

    def add_image_to_carousel(self, image_path):
        img = Image(source=image_path, allow_stretch=True)
        self.carousel.add_widget(img)
        self.modified_images[image_path] = image_path  # Initialize modified image path as the original path

    def add_image_to_thumbnails(self, image_path):
        thumbnail = Image(source=image_path, size_hint=(None, 1), width=150, allow_stretch=True)
        thumbnail.bind(on_touch_down=lambda instance, touch: self.on_thumbnail_click(instance, touch, image_path))
        self.thumbnail_layout.add_widget(thumbnail)

    def on_thumbnail_click(self, instance, touch, image_path):
        if instance.collide_point(*touch.pos):
            for widget in self.carousel.slides:
                if self.modified_images[image_path] == widget.source:
                    self.carousel.load_slide(widget)
                    break

    def add_art_style_buttons(self):
        for style in self.art_styles:
            button = Button(text=style, size_hint=(None, 1), width=150)
            button.bind(on_press=lambda instance, s=style: self.apply_art_style(s))
            self.style_layout.add_widget(button)

    def apply_art_style(self, style):
        current_image = self.carousel.current_slide
        if not current_image or not current_image.source:
            return

        original_path = next((k for k, v in self.modified_images.items() if v == current_image.source), None)
        if not original_path:
            return

        img = cv2.imread(original_path)
        if img is None:
            return

        # Apply style effects
        if style == "Original":
            styled_image = img
        elif style == "Van Gogh":
            styled_image = self.apply_van_gogh_effect(img)
        elif style == "Pop Art":
            styled_image = self.apply_pop_art_effect(img)
        elif style == "Sketch":
            styled_image = self.apply_sketch_effect(img)
        elif style == "Painting":
            styled_image = self.apply_painting_effect(img)
        elif style == "Pointillism":
            styled_image = self.apply_pointillism_effect(img)
        elif style == "Surreal":
            styled_image = self.apply_surreal_effect(img)
        elif style == "Cubism":
            styled_image = self.apply_cubism_effect(img)

        # Save the styled image to the temporary directory
        styled_image_path = os.path.join(self.temp_dir, f"styled_{style}_{os.path.basename(original_path)}")
        cv2.imwrite(styled_image_path, styled_image)

        # Update the carousel and tracking
        current_image.source = styled_image_path
        current_image.reload()
        self.modified_images[original_path] = styled_image_path

    # Filter effects (apply respective transformations to the image)
    def apply_van_gogh_effect(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_img[..., 0] = (hsv_img[..., 0] + 30) % 180
        return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    def apply_pop_art_effect(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # _, binary_img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        # return cv2.applyColorMap(binary_img, cv2.COLORMAP_JET)

    def apply_sketch_effect(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted_img = cv2.bitwise_not(gray_img)
        blurred_img = cv2.GaussianBlur(inverted_img, (111, 111), 0)
        return cv2.cvtColor(cv2.divide(gray_img, 255 - blurred_img, scale=256), cv2.COLOR_GRAY2BGR)
        # gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # inverted_img = cv2.bitwise_not(gray_img)
        # blurred_img = cv2.GaussianBlur(inverted_img, (111, 111), 0)
        # return cv2.cvtColor(cv2.divide(gray_img, 255 - blurred_img), cv2.COLOR_GRAY2BGR)

    def apply_painting_effect(self, img):
        return cv2.bilateralFilter(img, 9, 75, 75)
        # return cv2.GaussianBlur(img, (21, 21), 0)

    def apply_pointillism_effect(self, img):
        output = np.zeros_like(img)
        for y in range(0, img.shape[0], 5):
            for x in range(0, img.shape[1], 5):
                cv2.circle(output, (x, y), 3, img[y, x].tolist(), -1)
        return output
        # return cv2.bilateralFilter(img, 15, 75, 75)

    def apply_surreal_effect(self, img):
        return cv2.GaussianBlur(img, (15, 15), 2)
        # lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        # lab_img[..., 1] = cv2.add(lab_img[..., 1], 50)
        # lab_img[..., 2] = cv2.add(lab_img[..., 2], 50)
        # return cv2.cvtColor(lab_img, cv2.COLOR_LAB2BGR)

    def apply_cubism_effect(self, img):
        return cv2.Canny(img, 100, 200)
        # height, width = img.shape[:2]
        # small = cv2.resize(img, (width // 8, height // 8))
        # return cv2.resize(small, (width, height))

    def add_color_sliders(self):
        self.red_slider = Slider(min=0, max=255, value=255, size_hint=(0.25, 1))
        self.red_slider.bind(value=self.update_image)
        self.color_controls.add_widget(Label(text="Red", size_hint=(0.15, 1)))
        self.color_controls.add_widget(self.red_slider)

        self.green_slider = Slider(min=0, max=255, value=255, size_hint=(0.25, 1))
        self.green_slider.bind(value=self.update_image)
        self.color_controls.add_widget(Label(text="Green", size_hint=(0.15, 1)))
        self.color_controls.add_widget(self.green_slider)

        self.blue_slider = Slider(min=0, max=255, value=255, size_hint=(0.25, 1))
        self.blue_slider.bind(value=self.update_image)
        self.color_controls.add_widget(Label(text="Blue", size_hint=(0.15, 1)))
        self.color_controls.add_widget(self.blue_slider)
        # self.red_slider = Slider(min=0, max=255, value=127)
        # self.green_slider = Slider(min=0, max=255, value=127)
        # self.blue_slider = Slider(min=0, max=255, value=127)
        #
        # self.red_slider.bind(value=self.update_image)
        # self.green_slider.bind(value=self.update_image)
        # self.blue_slider.bind(value=self.update_image)
        #
        # self.color_controls.add_widget(Label(text="Red"))
        # self.color_controls.add_widget(self.red_slider)
        # self.color_controls.add_widget(Label(text="Green"))
        # self.color_controls.add_widget(self.green_slider)
        # self.color_controls.add_widget(Label(text="Blue"))
        # self.color_controls.add_widget(self.blue_slider)

    def update_image(self, instance, value):
        """Update image based on RGB sliders."""
        current_image = self.carousel.current_slide
        if not current_image or not current_image.source:
            return

        original_path = next((k for k, v in self.modified_images.items() if v == current_image.source), None)
        if not original_path:
            return

        pil_image = PILImage.open(original_path).convert("RGB")
        r, g, b = pil_image.split()

        red_adjust = r.point(lambda p: p * self.red_slider.value / 255)
        green_adjust = g.point(lambda p: p * self.green_slider.value / 255)
        blue_adjust = b.point(lambda p: p * self.blue_slider.value / 255)

        final_image = PILImage.merge("RGB", (red_adjust, green_adjust, blue_adjust))
        styled_image_path = os.path.join(self.temp_dir, f"color_adjust_{os.path.basename(original_path)}")
        final_image.save(styled_image_path)

        current_image.source = styled_image_path
        current_image.reload()
        self.modified_images[original_path] = styled_image_path
        # if not self.carousel.current_slide:
        #     return
        #
        # current_image = self.carousel.current_slide
        # if not current_image.source:
        #     return
        #
        # img = cv2.imread(current_image.source)
        # if img is None:
        #     return
        #
        # img[:, :, 0] = np.clip(img[:, :, 0] + self.blue_slider.value, 0, 255)
        # img[:, :, 1] = np.clip(img[:, :, 1] + self.green_slider.value, 0, 255)
        # img[:, :, 2] = np.clip(img[:, :, 2] + self.red_slider.value, 0, 255)
        #
        # cv2.imwrite(current_image.source, img)
        # current_image.reload()

    # def save_image(self, instance):
    #     if not self.carousel.current_slide:
    #         return

    #     current_image = self.carousel.current_slide
    #     if not current_image.source:
    #         return

    #     # Open the image file
    #     with open(current_image.source, 'rb') as f:
    #         files = {'file': (os.path.basename(current_image.source), f)}
    #         # Send the image to the backend to be saved
    #         url = BACKEND_URL + "/save_image"
    #         response = requests.post(url, files=files)

    #     if response.status_code == 200:
    #         print("Image saved successfully:", response.json())
    #     else:
    #         print("Error saving image:", response.text)

    def clear_message(self, dt):
        self.message_label.text = ""

    def save_image(self, instance):
        if not self.carousel.current_slide:
            return

        current_image = self.carousel.current_slide
        if not current_image.source:
            return

        # Open the image file
        with open(current_image.source, 'rb') as f:
            files = {'file': (os.path.basename(current_image.source), f)}
            # Send the image to the backend to be saved
            url = BACKEND_URL + "/save_image"
            response = requests.post(url, files=files)

        # Update message label based on response
        if response.status_code == 200:
            self.message_label.text = "Image saved successfully!"
            self.message_label.color = (0, 1, 0, 1)  # Green for success
        else:
            self.message_label.text = "Error saving image."
            self.message_label.color = (1, 0, 0, 1)  # Red for error

        # Schedule to hide the message after 3 seconds
        from kivy.clock import Clock
        Clock.schedule_once(self.clear_message, 3)




if __name__ == '__main__':
    ImageEditorApp().run()
