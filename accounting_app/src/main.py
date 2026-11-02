import customtkinter as ctk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.login import LoginView
from src.ui.business_select import BusinessSelectView
from src.ui.dashboard import DashboardView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Parigantavya Accounting")
        self.geometry("1000x700")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.current_frame = None
        self.current_user = None
        self.current_business = None

        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = LoginView(self, on_login_success=self.on_login_success)
        self.current_frame.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.show_business_select()

    def show_business_select(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = BusinessSelectView(self, current_user=self.current_user, on_business_selected=self.on_business_selected)
        self.current_frame.pack(fill="both", expand=True)

    def on_business_selected(self, business):
        self.current_business = business
        self.show_dashboard()

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = DashboardView(self, current_user=self.current_user, current_business=self.current_business)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
