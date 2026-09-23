import customtkinter as ctk


def main() -> None:
    root = ctk.CTk()
    root.title("Sigma Music")
    root.geometry("900x600")
    root.minsize(500, 300)
    root.configure(fg_color="#f5f5f5")
    root.mainloop()


if __name__ == "__main__":
    main()

