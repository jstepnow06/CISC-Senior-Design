from pathlib import Path
import json
import os
import subprocess
import sys #for running the pipeline scripts
import customtkinter as ctk
from PIL import Image
import threading 
from tkinter import filedialog #for working with files on system
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from audio_player import AudioPlayer
from styles import BUTTON_STYLE, LABEL_STYLE

#Defines parameters for displaying the logo
IMAGE_PATH = Path(__file__).resolve().parent.parent / "assets" / "sigma_logo.png"
WORKFLOW = Path(__file__).resolve().parent.parent / "workflow" # point to workflow folder for running pipeline
FFMPEG_BIN = Path(__file__).resolve().parent.parent / "ffmpeg" / "bin" # torchcodec needs these DLLs to read audio
BACKGROUND_SCALE = 0.7

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

        #Configures styling of page
        self.configure(fg_color="gray20")

        #Defines image to be displayed as background
        image = Image.open(IMAGE_PATH)
        self.image_ratio = image.width / image.height
        self.sigma_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(1, 1)
        )
        self.label = ctk.CTkLabel(self, image=self.sigma_image, text="")
        self.label.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.7, anchor="center")
        self.bind("<Configure>", self._resize_image)

        #Generates heading of main page
        self.welcome_label = ctk.CTkLabel(self,
            text="Welcome to Sigma Music",
            **LABEL_STYLE
        )
        self.welcome_label.place(relx=0.5, rely=0.25, anchor="center")

        #Button to move on to second page
        self.btn = ctk.CTkButton(self,
            text = "Get Started",
            command = lambda: controller.show_page(secondPage), #REPLACE secondPage WITH NEW PAGE NAME
            **BUTTON_STYLE
        )
        self.btn.grid(row=1, column=0, padx=20, pady=15)
        self.btn.place(relx=0.5, rely=0.75, anchor="center")

    #Modifies the size of the background image based on previously defined scale
    def _resize_image(self, event) -> None:
        width = int(event.width * BACKGROUND_SCALE)
        height = int(event.height * BACKGROUND_SCALE)

        if width / height > self.image_ratio:
            width = int(height * self.image_ratio)
        else:
            height = int(width / self.image_ratio)

        self.sigma_image.configure(
            size=(max(1, width), max(1, height))
        )

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
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

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

        self.process_btn = ctk.CTkButton(
            self,
            text="Process Audio",
            command=self.process_audio,
            state="disabled",
            **BUTTON_STYLE
        )
        self.process_btn.grid(row=3, column=0, padx=20, pady=10, sticky="")

        self.player_frame = AudioPlayer(self)
        self.player_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.selected_file = None
        self.result = None
        self.controller = controller

    def upload_file(self): #helper function for uploading audio files
        file_path = filedialog.askopenfilename(
            title = "Select an Audio File (mp3 or wav)",
            filetypes=[("Audio Files", "*.mp3 *.wav"), ("All Files","*.*")],
        )

        if file_path:
            if self.player_frame.load_audio(Path(file_path)):
                self.selected_file = Path(file_path)
                self.upload_btn.configure(state="disabled")
                self.process_btn.configure(state="normal")
                self.label.configure(text="Audio ready to process")

    def process_audio(self):
        if self.selected_file is None:
            return

        self.process_btn.configure(state="disabled")
        self.label.configure(text="Processing audio...")
        self.result = None
        threading.Thread(
            target=self.run_pipeline,
            args=(self.selected_file,),
            daemon=True,
        ).start()
        self.after(200, self.check)

    def run_pipeline(self, file_path):
            # runs each step with the same python as the GUI (.venv), outputs land next to the song
            # song.wav -> song_ymt3.mid, song_beats.json
            for script in ("MIDIscribe.py", "beats.py"):
                result = subprocess.run(
                    [sys.executable, str(WORKFLOW / script), str(file_path)],
                    cwd=file_path.parent,
                    env={**os.environ, "PATH": f"{FFMPEG_BIN};{os.environ['PATH']}"},
                )
                # error handling if scripts fail
                if result.returncode != 0:
                    self.result = f"{script} failed (see terminal)"
                    return

            try:
                self.result = self.create_pdf(file_path)
            except (OSError, ValueError, KeyError) as exc:
                self.result = f"Could not create PDF: {exc}"

    @staticmethod
    def create_pdf(file_path):
        output_stem = file_path.with_suffix("")
        beats_path = output_stem.parent / f"{output_stem.name}_beats.json"
        midi_path = output_stem.parent / f"{output_stem.name}_ymt3.mid"
        pdf_path = output_stem.parent / f"{output_stem.name}_output.pdf"

        with beats_path.open(encoding="utf-8") as beats_file:
            beats = json.load(beats_file)

        pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
        pdf.setTitle(f"Sigma Music output for {file_path.name}")
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(72, 720, "Sigma Music Processing Output")
        pdf.setFont("Helvetica", 12)
        lines = (
            f"Audio file: {file_path.name}",
            f"MIDI output: {midi_path.name}",
            f"Estimated tempo: {beats['bpm']:.1f} BPM",
            f"Beats per bar: {beats['beats_per_bar']}",
            f"Total beats: {len(beats['beats'])}",
            f"Total downbeats: {len(beats['downbeats'])}",
        )
        for index, line in enumerate(lines):
            pdf.drawString(72, 680 - index * 24, line)
        pdf.save()
        return pdf_path

    def check(self):
        # Keep checking if pipeline is finished
        if self.result is None:
            self.after(200, self.check)
            return
        if isinstance(self.result, Path):
            self.controller.show_pdf(self.result)
        else:
            self.label.configure(text=self.result)
            self.process_btn.configure(state="normal")


class pdfPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.document = None
        self.page_index = 0
        self.image = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title = ctk.CTkLabel(self, text="Processing Output", **LABEL_STYLE)
        self.title.grid(row=0, column=0, padx=20, pady=15)
        self.viewer = ctk.CTkLabel(self, text="No PDF loaded")
        self.viewer.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.back_btn = ctk.CTkButton(
            self,
            text="Process Another Audio File",
            command=lambda: controller.show_page(secondPage),
            **BUTTON_STYLE
        )
        self.back_btn.grid(row=2, column=0, padx=20, pady=15)

    def load_pdf(self, pdf_path):
        if self.document is not None:
            self.document.close()
        self.document = fitz.open(str(pdf_path))
        self.page_index = 0
        self.title.configure(text=f"Processing Output: {pdf_path.name}")
        self.display_page()

    def display_page(self):
        if self.document is None or not self.document.page_count:
            return
        page = self.document.load_page(self.page_index)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        self.image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
        self.viewer.configure(image=self.image, text="")



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
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        # Container frame that that holds pages
        container = ctk.CTkFrame(self) 

        # tells container to fill entire root window
        container.pack(side="top", fill="both", expand=True)
        self.page_container = container


        # using a grid to organize pages, tells row and columns to grow
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # The drawer and its in-menu button stay above the current page.
        self.menu = ctk.CTkFrame(
            container,
            width=240,
            corner_radius=0,
            fg_color=("gray94", "gray12"),
            border_width=1,
            border_color=("gray75", "gray30"),
        )
        self.menu.grid_columnconfigure(0, weight=1)
        self.menu.grid_columnconfigure(1, weight=0)
        self.menu.grid_rowconfigure(3, weight=1)
        self.menu_open = False
        self.menu_animating = False
        self.menu_animation_steps = 15
        self.menu_animation_interval = 12

        self.menu_button = ctk.CTkButton(
            self.menu,
            text="☰",
            width=44,
            height=44,
            font=("Arial", 26, "bold"),
            text_color="gold",
            fg_color="transparent",
            hover_color="gray25",
            command=self.toggle_menu,
        )
        # Anchor to the drawer's top-right so this follows its width.
        self.menu_button.grid(row=0, column=1, padx=12, pady=(12, 8), sticky="e")

        # Keep a separate trigger visible while the drawer is closed.
        self.menu_trigger_button = ctk.CTkButton(
            container,
            text="☰",
            width=44,
            height=44,
            font=("Arial", 26, "bold"),
            text_color="gold",
            fg_color="transparent",
            hover_color="gray25",
            command=self.toggle_menu,
        )
        self.menu_trigger_button.place(x=12, y=12)

        self.new_project_button = ctk.CTkButton(
            self.menu,
            text="New project",
            command=self.create_project,
            **BUTTON_STYLE,
        )
        self.new_project_button.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=8
        )

        self.home_button = ctk.CTkButton(
            self.menu,
            text="Home",
            command=lambda: self.show_page(frontPage),
            **BUTTON_STYLE,
        )
        self.home_button.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8)
        )

        self.project_list = ctk.CTkScrollableFrame(
            self.menu,
            fg_color="transparent",
            corner_radius=0,
        )
        self.project_list.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8)
        )

        self.project_pages = {}
        self.project_buttons = {}
        self.project_count = 0

        # dictionary for all of the pages
        self.pages = {}

        # placing all pages onto grid 
        # IMPORTANT: WHEN ADDING NEW PAGES, ADD THEM TO THIS LIST BELOW
        for PageClass in (frontPage, secondPage, pdfPage):
            #when creating the pages, parent is the container CTkFrame they are contained in
            #In controller = self, the controller is reffering to the App class itself (root)
            page_instance = PageClass(parent=container, controller=self)
            self.pages[PageClass] = page_instance

            # put them all in row 0, column 0
            # when placing page, tells it to stretch all corners (nsew)
            page_instance.grid(row=0, column=0, sticky="nsew")

        self.show_page(frontPage)

    def close_app(self):
        second_page = self.pages.get(secondPage)
        if second_page is not None:
            second_page.player_frame.close()
        pdf_page = self.pages.get(pdfPage)
        if pdf_page is not None and pdf_page.document is not None:
            pdf_page.document.close()
        self.destroy()

    #command for changing/showing a page onto the front of the grid
    def show_page(self, page_class):
        page = self.pages[page_class] if page_class in self.pages else page_class
        page.tkraise() #lifts that frame (page) into the top layer
        if self.menu_open or self.menu_animating:
            self.menu.lift()
            self.menu_button.lift()
        else:
            self.menu_trigger_button.lift()

    def create_project(self):
        self.project_count += 1
        project_name = f"Project {self.project_count}"
        project_page = ctk.CTkFrame(self.page_container)
        project_page.grid(row=0, column=0, sticky="nsew")
        self.project_pages[project_name] = project_page

        project_button = ctk.CTkButton(
            self.project_list,
            text=project_name,
            command=lambda page=project_page: self.show_page(page),
            **BUTTON_STYLE,
        )
        project_button.pack(fill="x", pady=4)
        self.project_buttons[project_name] = project_button

        self.show_page(project_page)

    def show_pdf(self, pdf_path):
        pdf_page = self.pages[pdfPage]
        pdf_page.load_pdf(pdf_path)
        self.show_page(pdfPage)

    def toggle_menu(self):
        # Ignore clicks until the current slide animation finishes.
        if self.menu_animating:
            return

        self.menu_width = self.menu.winfo_reqwidth()
        opening = not self.menu_open
        self.menu_animating = True
        if opening:
            self.menu_trigger_button.place_forget()
            self.menu.place(x=-self.menu_width, y=0, relheight=1)
            self.menu.lift()
            self.menu_button.lift()
        else:
            self.menu_button.lift()
        self.animate_menu(opening, 0)

    def animate_menu(self, opening, step):
        # Ease the movement at both ends for a smoother slide.
        progress = step / self.menu_animation_steps
        eased_progress = progress * progress * (3 - 2 * progress)
        start_x = -self.menu_width if opening else 0
        end_x = 0 if opening else -self.menu_width
        menu_x = round(start_x + (end_x - start_x) * eased_progress)

        self.menu.place(x=menu_x, y=0, relheight=1)

        if step == self.menu_animation_steps:
            self.menu_animating = False
            self.menu_open = opening
            if not opening:
                self.menu.place_forget()
                self.menu_trigger_button.place(x=12, y=12)
                self.menu_trigger_button.lift()
            return

        self.after(
            self.menu_animation_interval,
            lambda: self.animate_menu(opening, step + 1),
        )




        

if __name__ == "__main__":  # only not true important if this file is imported into another
    app = App()
    app.mainloop()