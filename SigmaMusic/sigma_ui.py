from pathlib import Path
import os, subprocess, sys #for running the pipeline scripts
import customtkinter as ctk
from PIL import Image
import threading 
from tkinter import filedialog #for working with files on system


IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "SIGMA.png"
WORKFLOW = Path(__file__).resolve().parent.parent / "workflow" # point to workflow folder for running pipeline
FFMPEG_BIN = Path(__file__).resolve().parent.parent / "ffmpeg" / "bin" # torchcodec needs these DLLs to read audio

BUTTON_STYLE = {
    "font": ("Centaur", 20, "bold"),
    "text_color": "gold",
    "fg_color": "gray29",
    "border_color": "black",
    "border_width": 3,
}

LABEL_STYLE = {
    "font": ("Castellar", 30), 
    "anchor": "center", 
    "justify": "center", 
    "text_color": "gold"
}

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
        self.label = ctk.CTkLabel(self, text="Welcome to Sigma Music", 
            **LABEL_STYLE
        )
        self.label.grid(row = 0, column = 0, padx = 20, pady = 20)
        self.label.place(relx=0.5, rely=0.2, anchor="center")

        #Goes to second (REPLACE WITH FUTURE PAGE IT WILL GO TO)
        self.btn = ctk.CTkButton(
            self,
            text = "Get Started",
            command = lambda: controller.show_page(secondPage), #REPLACE secondPage WITH NEW PAGE NAME
            **BUTTON_STYLE
        )
        self.btn.grid(row=1, column=0, padx=20, pady=15)
        self.btn.place(relx=0.5, rely=0.5, anchor="center")

# template for page to be switched into and from
class secondPage(ctk.CTkFrame): #REMINDER: CHANGE PAGE NAME 
    #self here just refers to itself; it's own page/class
    def __init__(self, parent, controller):
        super().__init__(parent) # always has parent argument if not root page
        
        self.grid_columnconfigure(0, weight=1) #center horizontally

        # space for row 0 and 1
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)

        # push row 2 to bottom half of page
        self.grid_rowconfigure(2, weight=2)

        self.label = ctk.CTkLabel(self, text="This is the Second Page!", **LABEL_STYLE)

        # tells this label to stick to the bottom of row 0
        self.label.grid(row=0, column=0, padx=20, pady=20, sticky="s")

        # Button to go back to the front page
        self.btn = ctk.CTkButton(
            self, 
            text="Go Back Home", 
            command=lambda: controller.show_page(frontPage),
            **BUTTON_STYLE
        )
        self.btn.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        #Uploading Audio
        self.upload_btn = ctk.CTkButton(
            self, 
            text="Upload Audio File", 
            command=self.upload_file, #calls helper function below
            **BUTTON_STYLE
            )
        self.upload_btn.grid(row=2, column=0, padx=20, pady=10, sticky="")

    def upload_file(self): #helper function for uploading audio files
        file_path = filedialog.askopenfilename(
            title = "Select an Audio File (mp3 or wav)",
            filetypes=[("Audio Files", "*.mp3 *.wav"), ("All Files","*.*")],
        )

        if file_path:
            print(f"User selected: {file_path}")
            # You save 'file_path' to a variable or pass it to your controller
            self.label.configure(text=f"Loaded: {file_path.split('/')[-1]}")
            self.upload_btn.configure(state="disabled") #Limit to one song at a time
            self.result = None
            # Start the pipeline in a separate thread to avoid freezing the GUI
            threading.Thread(target=self.run_pipeline, args=(file_path,), daemon=True).start()
            self.after(200, self.check)

    def run_pipeline(self, file_path):
            # runs each step with the same python as the GUI (.venv), outputs land next to the song
            # song.wav -> song_ymt3.mid, song_beats.json
            for script in ("MIDIscribe.py", "beats.py"):
                result = subprocess.run([sys.executable, str(WORKFLOW / script), file_path],
                                        cwd=Path(file_path).parent,
                                        env={**os.environ, "PATH": f"{FFMPEG_BIN};{os.environ['PATH']}"})
                # error handling if scripts fail
                if result.returncode != 0:
                    self.result = f"{script} failed (see terminal)"
                    return

            self.result = "Done!"

    def check(self):
        # Keep checking if pipeline is finished
        if self.result is None:
            self.after(200, self.check)
            return
        self.label.configure(text=self.result)
        self.upload_btn.configure(state="normal")



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
            #when creating the pages, parent is the container CTkFrame they are contained in
            #In controller = self, the controller is reffering to the App class itself (root)
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