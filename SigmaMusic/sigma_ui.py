import customtkinter as ctk


def main() -> None: #main function to open the window
    root = ctk.CTk() #creating the application window (root of all the app)
    root.title("Sigma Music") 
    root.geometry("900x600")
    root.minsize(500, 300)
    root.configure(fg_color="#f5f5f5")
    root.mainloop() #keeps the window open; otherwise would just exit right after opening


if __name__ == "__main__": #only not true important if this file is imported into another
    main()

