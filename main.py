from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

FILL_COLOR = (203, 201, 201)


class ImgPreview(Label):
    def __init__(self, *args, **kwargs):
        Label.__init__(self, *args, **kwargs)
        self.img = None
        self.photo = None
        self.img_with_watermark = watermarked_image


class WatermarkEntry(Entry):
    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.bind("<KeyRelease>", apply_watermark)


class WaterMarkImage:
    def __init__(self, image=None, text="", watermark=None):
        self.image = image
        self.text = text
        self.watermark = None
        self.result = None


def open_image(label):
    file_path = filedialog.askopenfilename(title="Open Image File",
                                                 filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")])
    if file_path:
        label.file_path = file_path
        img = Image.open(file_path)
        if str(label).split(".")[-1] == "image":
            watermarked_image.image = img.copy()
            print("background loaded")
        elif str(label).split(".")[-1] == "watermark":
            watermarked_image.watermark = img.copy()
            print("watermark loaded")
        display_image(img, label)


def display_image(img, label):
    label.img = img.copy()
    img = resize_image(img, label)
    photo = ImageTk.PhotoImage(img)

    label.config(image=photo)
    label.photo = photo

    apply_watermark(None)


def apply_watermark(event):
    if watermarked_image.image:
        if watermarked_image.watermark:
            bg_img = watermarked_image.image
            bg_w, bg_h = bg_img.size
            watermark = watermarked_image.watermark
            watermark_w, watermark_h = watermark.size
            if watermark_w > bg_w or watermark_h > bg_h:
                watermark.thumbnail((bg_h, bg_w))
            offset = ((bg_w - watermark.size[0]) // 2, (bg_h - watermark.size[1]) // 2)
            mask_im = Image.new("L", watermark.size, 0)
            draw = ImageDraw.Draw(mask_im)
            draw.ellipse((15, 15, mask_im.width - 15, mask_im.height - 15), fill=150)
            blurred = mask_im.filter(ImageFilter.GaussianBlur(10))
            img_watermark = bg_img.copy()
            img_watermark.paste(watermark, offset, blurred)
            image_preview.img_with_watermark = img_watermark.copy()
            watermarked_image.result = img_watermark.copy()

            # watermarked_image.result.save('out.png')
        else:
            watermarked_image.result = watermarked_image.image.copy()

        watermarked_image.text = text_watermark.get()
        img_size = watermarked_image.image.size
        if watermarked_image.text != "":
            font_size = 1
            font = ImageFont.truetype("Conquest-8MxyM.ttf", font_size)
            while font.getbbox(watermarked_image.text)[3] - font.getbbox(watermarked_image.text)[1] < 0.2 * img_size[0]:
                font_size += 1
                font = ImageFont.truetype("Conquest-8MxyM.ttf", font_size)
            while font.getbbox(watermarked_image.text)[2] - font.getbbox(watermarked_image.text)[0] > img_size[1]:
                font_size -= 1
                font = ImageFont.truetype("Conquest-8MxyM.ttf", font_size)
            font_size -= 1
            font = ImageFont.truetype("Conquest-8MxyM.ttf", font_size)
        position = (int(img_size[0] / 2), int(img_size[1] / 2))
        drawing = ImageDraw.Draw(watermarked_image.result)
        drawing.text(xy=position, text=watermarked_image.text, font=font, fill=FILL_COLOR, anchor="mm")
        prev_img = watermarked_image.result.copy()
        prev_img = resize_image(prev_img, image_preview)
        photo = ImageTk.PhotoImage(prev_img)
        image_preview.config(image=photo)
        image_preview.photo = photo


def close_watermark():
    if watermark_preview.img is not None:
        watermarked_image.watermark = None
        watermark_preview.photo = None
        watermark_preview.img = None
        watermark_preview.config(image=pixel)
        apply_watermark(None)


def resize_image(img, label):
    img_w, img_h = img.size
    label_w, label_h = (label.winfo_width(), label.winfo_height())

    if img_w > label_w or img_h > label_h:
        img.thumbnail((label_w, label_h))
    return img


def save():
    if watermarked_image.result:
        watermarked_image.result.save('out.png')


App = Tk()
App.title = "Watermark"

watermarked_image = WaterMarkImage()
pixel = PhotoImage(height=1, width=1)

container = Frame(App, height=580, width=1080)
container.pack(side="top", fill="both", expand=True)
container.pack_propagate(False)

image_preview = ImgPreview(container, name="image", image=pixel, height=400, width=600, borderwidth=2, relief="ridge")
image_preview.grid(row=0, column=0, rowspan=4, padx=20, pady=20)

open_file = Button(container, text='Open image', command=lambda: open_image(image_preview))
open_file.grid(row=4, column=0, sticky='S', padx=10, pady=10)

label_text_watermark = Label(container, text="Text for watermark:")
label_text_watermark.grid(row=0, column=1, columnspan=2, sticky="WS", padx=20, pady=10)
text_frame = Frame(container, borderwidth=2, relief=RIDGE)
text_frame.grid(row=1, column=1, columnspan=2, sticky="N", padx=20)
text_watermark = WatermarkEntry(text_frame, borderwidth=10, relief=FLAT, width=52)
text_watermark.pack()


open_watermark = Button(container, text='Open watermark', command=lambda: open_image(watermark_preview))
open_watermark.grid(row=2, column=1, sticky="WS", padx=20)
remove_watermark = Button(container, text='Remove watermark', command=close_watermark)
remove_watermark.grid(row=2, column=2, sticky="ES", padx=20)
watermark_preview = ImgPreview(container, name="watermark", image=pixel, height=100, borderwidth=2, relief="ridge")
watermark_preview.grid(row=3, column=1, columnspan=2, sticky="NSEW", padx=20, pady=20)

save_photo = Button(container, text='Save', command=save)
save_photo.grid(row=4, column=1, columnspan=2, sticky="NSEW", padx=20, pady=20)


App.mainloop()
