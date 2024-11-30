from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from plyer import filechooser
import os


class MultiCarouselApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation="vertical")

        # Title
        self.main_layout.add_widget(Button(text="Add Images", size_hint=(1, 0.1), on_press=self.open_gallery))

        # Main Image Carousel
        self.carousel = Carousel(direction="right", size_hint=(1, 0.7))
        self.main_layout.add_widget(self.carousel)

        # Horizontal Scroll Bar for Thumbnails
        self.scrollview = ScrollView(size_hint=(1, 0.2), do_scroll_x=True, do_scroll_y=False)
        self.thumbnail_layout = GridLayout(cols=10, size_hint=(None, 1), height=150, spacing=10, padding=10)
        self.thumbnail_layout.bind(minimum_width=self.thumbnail_layout.setter("width"))
        self.scrollview.add_widget(self.thumbnail_layout)
        self.main_layout.add_widget(self.scrollview)

        # Store all image paths for reference
        self.image_paths = []

        return self.main_layout

    def open_gallery(self, instance):
        """
        Opens a file chooser for image selection.
        """
        filechooser.open_file(
            filters=[("Images", ".png;.jpg;*.jpeg;*.JPG")],
            multiple=True,
            on_selection=self.add_images
        )

    def add_images(self, selection):
        """
        Adds selected images to the carousel and thumbnails.
        """
        if not selection:
            print("No images selected or invalid paths.")
            return

        for image_path in selection:
            if os.path.exists(image_path) and os.path.isfile(image_path):
                self.image_paths.append(image_path)  # Store the path for reference
                print(f"Adding image: {image_path}")
                self.add_image_to_carousel(image_path)
                self.add_image_to_thumbnails(image_path)
            else:
                print(f"Invalid image path: {image_path}")

    def add_image_to_carousel(self, image_path):
        """
        Adds the image to the main carousel.
        """
        img = Image(source=image_path, allow_stretch=True)
        img.bind(on_touch_down=lambda instance, touch: self.on_image_click(instance, touch, image_path))
        self.carousel.add_widget(img)

    def add_image_to_thumbnails(self, image_path):
        """
        Adds the image as a thumbnail in the horizontal scroll view.
        """
        thumbnail = Image(source=image_path, size_hint=(None, 1), width=150, allow_stretch=True)
        thumbnail.bind(on_touch_down=lambda instance, touch: self.on_thumbnail_click(instance, touch, image_path))
        self.thumbnail_layout.add_widget(thumbnail)

    def on_image_click(self, instance, touch, image_path):
        """
        Displays the clicked image in full-screen modal view.
        """
        if instance.collide_point(*touch.pos):
            self.show_full_screen(image_path)

    def on_thumbnail_click(self, instance, touch, image_path):
        """
        Loads the corresponding image into the main carousel when its thumbnail is clicked.
        """
        if instance.collide_point(*touch.pos):
            for widget in self.carousel.slides:
                if widget.source == image_path:
                    self.carousel.load_slide(widget)
                    break

    def show_full_screen(self, image_path):
        """
        Displays the image in a full-screen modal view.
        """
        modal = ModalView(size_hint=(1, 1), background_color=(0, 0, 0, 0.8))
        image = Image(source=image_path, allow_stretch=True)
        modal.add_widget(image)
        modal.bind(on_touch_down=lambda *args: modal.dismiss())
        modal.open()


if __name__ == "__main__":
    MultiCarouselApp().run()






