from pathlib import Path

import customtkinter as ctk
from PIL import Image


IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "SIGMA.png"

# REMINDER: delete comment string below later, restructuring app pages below it
""""
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
"""


#Front/first page of the applications
class frontPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text="This is the front Page")
        self.label.grid(row = 0, column = 0, padx = 20)

        #Goes to second (REPLACE WITH FUTURE PAGE IT WILL GO TO)
        self.btn = ctk.CTkButton(
            self,
            text = "Go to Next Page",
            command = lambda: controller.show_page(secondPage) #REPLACE secondPage WITH NEW PAGE NAME
        )
        self.btn.grid(row=1, column=0, padx=20, pady=10)

# template for page to be switched into and from
class secondPage(ctk.CTkFrame): #REMINDER: CHANGE PAGE NAME 
    def __init__(self, parent, controller):
        super().__init__(parent) # always has parent argument if not root page
        self.label = ctk.CTkLabel(self, text="This is the Second Page!")
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Button to go back to the front page
        self.btn = ctk.CTkButton(
            self, 
            text="Go Back Home", 
            command=lambda: controller.show_page(frontPage)
        )
        self.btn.grid(row=1, column=0, padx=20, pady=10)


class App(ctk.CTk): #will hold rest of the CTkFrames (pages), functionally like main
    
    #self will function as the "root" window
    def __init__(self):
        super().__init__() #always goes at the beggining of a page's code

        #screen width and height for page/widget size use later
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        #screen_width = root_tk.winfo_screenwidth()
        #screen_height = root_tk.winfo_screenheight()
        
        width = int(screen_width * 0.6)
        height = int(screen_height * 0.6)

        # Note: other pages cannot be larger than root window size
        #Root size
        self.geometry(f"{width}x{height}")

        self.title("SigmaMusic main page")

        # Container frame that that holds pages
        container = ctk.CTkFrame(self) 

        # tells container to fill entire root window
        container.pack(side="top", fill="both", expand=True)


        # using a grid to organize pages, tells row and columns to grow
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # dictionary for all of the pages
        self.pages = {}

        # placing all pages onto grid 
        # IMPORTANT: WHEN ADDING NEW PAGES, ADD THEM TO THIS LIST BELOW
        for PageClass in (frontPage, secondPage):
            page_instance = PageClass(parent=container, controller=self)
            self.pages[PageClass] = page_instance

            # put them all in row 0, column 0
            # when placing page, tells it to stretch all corners (nsew)
            page_instance.grid(row=0, column=0, sticky="nsew")

        self.show_page(frontPage)

    #command for changing/showing a page onto the front of the grid
    def show_page(self, page_class):
        page = self.pages[page_class] # finding the page using it's class name
        page.tkraise() #lifts that frame (page) into the top layer




        

if __name__ == "__main__":  # only not true important if this file is imported into another
    app = App()
    app.mainloop()