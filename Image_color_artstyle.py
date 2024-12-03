from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from plyer import filechooser
import os
from PIL import Image as PILImage, ImageEnhance, ImageFilter


class ImageEditorApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        # Add Images Button
        add_images_button = Button(text="Add Images", size_hint=(1, 0.1))
        add_images_button.bind(on_press=self.open_gallery)
        self.main_layout.add_widget(add_images_button)

        # Main Image Carousel
        self.carousel = Carousel(direction="right", size_hint=(1, 0.5))
        self.main_layout.add_widget(self.carousel)

        # Thumbnails Scroll View
        self.scrollview = ScrollView(size_hint=(1, 0.15), do_scroll_x=True, do_scroll_y=False)
        self.thumbnail_layout = GridLayout(cols=10, size_hint=(None, 1), height=150, spacing=10, padding=10)
        self.thumbnail_layout.bind(minimum_width=self.thumbnail_layout.setter("width"))
        self.scrollview.add_widget(self.thumbnail_layout)
        self.main_layout.add_widget(self.scrollview)

        # Color Adjustment Sliders
        self.color_controls = BoxLayout(orientation="horizontal", size_hint=(1, 0.15))
        self.add_color_sliders()
        self.main_layout.add_widget(self.color_controls)

        # Art Styles Scroll View
        self.style_scroll = ScrollView(size_hint=(1, 0.1), do_scroll_x=True, do_scroll_y=False)
        self.style_layout = GridLayout(cols=8, size_hint=(None, 1), spacing=10, padding=10)
        self.style_layout.bind(minimum_width=self.style_layout.setter("width"))
        self.style_scroll.add_widget(self.style_layout)
        self.main_layout.add_widget(self.style_scroll)

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
                self.image_paths.append(image_path)
                self.add_image_to_carousel(image_path)
                self.add_image_to_thumbnails(image_path)

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

    def add_color_sliders(self):
        self.brightness_slider = Slider(min=0.5, max=2.0, value=1.0, size_hint=(0.3, 1))
        self.brightness_slider.bind(value=self.update_image)
        self.color_controls.add_widget(Label(text="Brightness", size_hint=(0.2, 1)))
        self.color_controls.add_widget(self.brightness_slider)

        self.contrast_slider = Slider(min=0.5, max=2.0, value=1.0, size_hint=(0.3, 1))
        self.contrast_slider.bind(value=self.update_image)
        self.color_controls.add_widget(Label(text="Contrast", size_hint=(0.2, 1)))
        self.color_controls.add_widget(self.contrast_slider)

    def update_image(self, instance, value):
        current_image = self.carousel.current_slide
        if not current_image or not current_image.source:
            return

        original_path = next((k for k, v in self.modified_images.items() if v == current_image.source), None)
        if not original_path:
            return

        pil_image = PILImage.open(original_path)

        enhancer = ImageEnhance.Brightness(pil_image)
        bright_image = enhancer.enhance(self.brightness_slider.value)

        enhancer = ImageEnhance.Contrast(bright_image)
        final_image = enhancer.enhance(self.contrast_slider.value)

        updated_image_path = f"temp_adjusted_{os.path.basename(original_path)}"
        final_image.save(updated_image_path)

        current_image.source = updated_image_path
        current_image.reload()
        self.modified_images[original_path] = updated_image_path

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

        pil_image = PILImage.open(original_path)

        if style == "Original":
            styled_image = pil_image
        elif style == "Van Gogh":
            styled_image = pil_image.filter(ImageFilter.EMBOSS)
        elif style == "Pop Art":
            styled_image = pil_image.filter(ImageFilter.CONTOUR)
        elif style == "Sketch":
            styled_image = pil_image.convert("L").filter(ImageFilter.EDGE_ENHANCE)
        elif style == "Painting":
            styled_image = pil_image.filter(ImageFilter.SMOOTH_MORE)
        elif style == "Pointillism":
            styled_image = pil_image.filter(ImageFilter.DETAIL)
        elif style == "Surreal":
            styled_image = pil_image.filter(ImageFilter.GaussianBlur(5))
        elif style == "Cubism":
            styled_image = pil_image.filter(ImageFilter.FIND_EDGES)
        else:
            styled_image = pil_image

        styled_image_path = f"temp_styled_{style}_{os.path.basename(original_path)}"
        styled_image.save(styled_image_path)

        current_image.source = styled_image_path
        current_image.reload()
        self.modified_images[original_path] = styled_image_path


if __name__ == "__main__":
    ImageEditorApp().run()
