from pathlib import Path

import customtkinter as ctk
from PIL import Image


IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "SIGMA.png"


def load_sigma_image(size: tuple[int, int]) -> ctk.CTkImage | None:
    try:
        image = Image.open(IMAGE_PATH).convert("RGBA")
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except FileNotFoundError:
        print(f"Image not found: {IMAGE_PATH}")
        return None
    except Exception as exc:
        print(f"Could not load image: {exc}")
        return None


def on_button_click(image_label: ctk.CTkLabel) -> None:
    print("SIGMA OVERWATCH")
    sigma_image = load_sigma_image((300, 300))
    if sigma_image is not None:
        image_label.configure(image=sigma_image, text="")
        image_label.pack(pady=10)


def main() -> None:  # main function to open the window
    root = ctk.CTk()  # creating the application window (root of all the app)
    root.title("Sigma Music")
    root.geometry("900x600")
    root.minsize(500, 300)
    root.configure(fg_color="#f5f5f5")


    ex_text_label = ctk.CTkLabel(
        master = root, #Where text goes
        text = "THIS IS A TEST", # What it says
        font = ("arial", 20), # How it looks
        text_color = "black" #color of text
    )

    ex_text_label.pack(pady=40) #placing the text somewhere

    text = ctk.CTkLabel(root, text="Welcome to Sigma Music", fg_color="#f5f5f5")
    text.pack(pady=10)

    image_label = ctk.CTkLabel(root, text="", width=0, height=0)
    image_label.pack_forget()

    button = ctk.CTkButton(root, text="What is that melody?", command=lambda: on_button_click(image_label))
    button.pack(pady=10)

    #KEEP THIS LINE AT THE END OF THE FUNCTION
    root.mainloop()  # keeps the window open; otherwise would just exit right after opening


if __name__ == "__main__":  # only not true important if this file is imported into another
    main()