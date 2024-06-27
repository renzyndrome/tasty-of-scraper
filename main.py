import ofscraper.utils.paths.common as common_paths
import ofscraper.utils.auth.helpers as helpers
import tkinter as tk
from tkinter import ttk
import ofscraper.api.statistics as stats
from ofscraper.utils.me import get_username
import ofscraper.utils.auth.schema as auth_schema
import ofscraper.utils.auth.make as make
import json
import logging
import re

log = logging.getLogger("shared")


def make_auth(auth=None):
    # helpers.authwarning(common_paths.get_auth_file())

    auth = auth_schema.auth_schema(auth or helpers.get_empty())

    for key, item in auth.items():
        newitem = item.strip()
        newitem = re.sub("^ +", "", newitem)
        newitem = re.sub(" +$", "", newitem)
        newitem = re.sub("\n+", "", newitem)
        auth[key] = newitem

    authFile = common_paths.get_auth_file()
    log.info(f"{auth}\nWriting to {authFile}", style="yellow")
    auth = auth_schema.auth_schema(auth)

    with open(authFile, "w") as f:
        f.write(json.dumps(auth, indent=4))

    return True


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tasty OF Scraper")
        self.geometry("400x300")
        self.configure(bg="lightblue")  # Set the background color

        # Configure style for rounded, embossed buttons
        style = ttk.Style(self)
        style.configure("RoundedButton.TButton",
                        background="white",
                        foreground="black",
                        relief="raised",
                        padding=6)
        style.map("RoundedButton.TButton",
                  relief=[("active", "groove"), ("pressed", "sunken")])

        # Centered Start scraping button
        self.start_button = ttk.Button(
            self, text="Start scraping", command=self.start_scraping, style="RoundedButton.TButton")
        self.start_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Loading progress bar below the button
        self.progress_bar = ttk.Progressbar(
            self, mode="indeterminate", length=200)
        self.progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.progress_bar.place_forget()  # Ensure it's initially hidden

        # Small Edit configuration button top right
        self.edit_button = ttk.Button(
            self, text="Edit configuration", command=self.edit_configuration, style="RoundedButton.TButton")
        self.edit_button.place(relx=0.9, rely=0.1, anchor=tk.NE)

        # Hidden textbox for entering cookie details
        self.cookie_frame = tk.Frame(self, bg="lightblue")
        self.cookie_label = tk.Label(
            self.cookie_frame, text="Enter Cookie Details", bg="lightblue")
        self.cookie_label.pack()

        self.cookie_text = tk.Text(self.cookie_frame, height=4, width=30)
        self.cookie_text.pack()

        self.save_button = ttk.Button(
            self.cookie_frame, text="Save", command=self.save_configuration, style="RoundedButton.TButton")
        self.save_button.pack()

        self.cookie_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        self.cookie_frame.place_forget()  # Ensure it's initially hidden

    # def make_auth(auth=None):

    def start_scraping(self):
        # Change button text and start progress bar
        self.start_button.config(text="Scraping...")
        username = get_username()
        stats.get_earnings_all(username)
        stats.get_earnings_all(username)
        stats.get_earnings_tips(username)
        stats.get_reach_user(username)
        stats.get_reach_guest(username)
        stats.get_subs_fans_count_new(username)
        # stats.get_subs_fans_all(username)
        stats.get_subs_fans_earnings_new(username)
        stats.get_subs_fans_count_all(username)
        stats.get_subs_fans_earnings_all(username)
        stats.get_subs_fans_count_renew(username)
        stats.get_earnings_chargebacks(username)
        self.progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.progress_bar.start()

        # Placeholder for scraping logic
        # Simulate scraping duration with after method
        self.after(5000, self.scraping_complete)

    def scraping_complete(self):
        # Stop the progress bar and reset button text
        self.progress_bar.stop()
        self.progress_bar.place_forget()
        self.start_button.config(text="Start scraping")

    def edit_configuration(self):
        # Hide start button and show cookie frame
        self.start_button.place_forget()
        self.cookie_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def save_configuration(self):
        # Save the cookie details (placeholder)
        cookie_details = self.cookie_text.get("1.0", tk.END).strip()
        # auth_file.edit_auth()
        if isinstance(cookie_details, str):
            try:
                # Convert string to dictionary
                dict_cookie_details = json.loads(cookie_details)
            except json.JSONDecodeError as e:
                log.error(f"Error decoding auth JSON: {e}")
                return None
        auth = auth_schema.auth_schema(dict_cookie_details)
        # make.make_auth(auth)
        make_auth(auth)
        print(f"Cookie Details Saved: {cookie_details}")
        # print(make_auth)

        # Hide cookie frame and show start button
        self.cookie_frame.place_forget()
        self.start_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)


if __name__ == "__main__":
    app = App()
    app.mainloop()
