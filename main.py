import ofscraper.utils.auth.helpers as helpers
import tkinter as tk
from tkinter import ttk
import ofscraper.api.statistics as stats
from ofscraper.utils.me import get_username
import ofscraper.utils.auth.schema as auth_schema
import ofscraper.utils.args.read as read_args
import ofscraper.utils.profiles.data as profile_data
import ofscraper.utils.auth.make as make
import ofscraper.const.constants as constants
import ofscraper.utils.args.read as read_args
import ofscraper.utils.config.data as data
import ofscraper.utils.config.file as config_file
import ofscraper.utils.constants as constants_attr
import ofscraper.utils.dates as dates_manager
import ofscraper.utils.profiles.data as profile_data
import ofscraper.utils.me as me_util
import threading
import json
import logging
import re
import os
import pathlib

log = logging.getLogger("shared")


def get_config_home():
    return get_config_path().parent


def get_profile_path(name=None):
    if name:
        return get_config_home() / name
    elif not read_args.retriveArgs().profile:
        return get_config_home() / profile_data.get_current_config_profile()
    return get_config_home() / read_args.retriveArgs().profile


def get_config_path():
    configPath = read_args.retriveArgs().config
    defaultPath = pathlib.Path.home() / constants.configPath / constants.configFile
    ofscraperHome = pathlib.Path.home() / constants.configPath

    if configPath is None or configPath == "":
        return defaultPath
    configPath = pathlib.Path(configPath)

    if configPath.is_file():
        return configPath
    elif configPath.is_dir():
        return configPath / constants.configFile
    elif configPath.suffix == "":
        return configPath / constants.configFile
    elif str(configPath.parent) == ".":
        return ofscraperHome / configPath
    return configPath


def get_auth_file(profile_name=None):
    return get_profile_path(profile_name) / constants_attr.getattr("authFile")


def print_auth():
    print("inside print_auth()")
    auth_file = get_auth_file()
    print(auth_file)
    return auth_file


# def get_all_profiles():
#     config_home = get_config_home()
#     profiles = []
#     for item in os.listdir(config_home):
#         item_path = config_home / item
#         if item_path.is_dir() and (item_path / constants.authFile).exists():
#             profiles.append(item)
#     return profiles


# def get_username_from_profile(profile):
#     try:
#         auth_data = helpers.get_auth_dict(profile)
#         # Extract and return the username from auth_data
#         # The exact implementation depends on how the username is stored in your auth file
#         return auth_data.get('username', 'default_username')
#     except json.JSONDecodeError:
#         log.error(f"Error reading auth file for profile '{
#                   profile}'. The file may be empty or contain invalid JSON.")
#         return None
#     except Exception as e:
#         log.error(f"Error processing profile '{profile}': {str(e)}")
#         return None


# def run_statistics_for_all_profiles():
#     profiles = get_all_profiles()
#     print(f"Here are the profiles: {profiles}")
#     for profile in profiles:
#         username = get_username_from_profile(profile)
#         print(f"Username is {username}")
#         stats.get_earnings_all(username, profile)
#         stats.get_earnings_tips(username, profile)
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
        self.start_button.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        # Loading progress bar below the button
        self.progress_bar = ttk.Progressbar(
            self, mode="indeterminate", length=200)
        self.progress_bar.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        self.progress_bar.place_forget()  # Ensure it's initially hidden

        # Small Edit configuration button top right
        self.edit_button = ttk.Button(
            self, text="Edit configuration", command=self.edit_configuration, style="RoundedButton.TButton")
        self.edit_button.place(relx=0.9, rely=0.1, anchor=tk.NE)

        # Hidden textbox for entering cookie details
        self.cookie_frame = tk.Frame(self, bg="lightblue")
        self.cookie_label = tk.Label(
            self.cookie_frame, text="Enter Cookie Details", bg="lightblue")
        self.cookie_label.pack(pady=(0, 5))  # Add some padding below the label

        self.cookie_text = tk.Text(self.cookie_frame, height=4, width=30)
        self.cookie_text.pack(pady=(0, 10))  # Add padding below the text box

        # Create a frame for buttons
        self.button_frame = tk.Frame(self.cookie_frame, bg="lightblue")
        self.button_frame.pack(pady=(10, 0))  # Add padding above the buttons

        self.save_button = ttk.Button(
            self.button_frame, text="Save", command=self.save_configuration, style="RoundedButton.TButton")
        # Add some space between buttons
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))

        self.cancel_button = ttk.Button(
            self.button_frame, text="Cancel", command=self.cancel_configuration, style="RoundedButton.TButton")
        self.cancel_button.pack(side=tk.LEFT)

        self.isEditingConfiguration = False
        self.cookie_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        self.cookie_frame.place_forget()  # Ensure it's initially hidden
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # def make_auth(auth=None):
        self.profiles = self.get_all_profiles()
        self.current_profile = None
        self.current_profile = read_args.retriveArgs(
        ).profile or profile_data.get_current_config_profile()
        self.view_profiles_button = ttk.Button(
            self, text="View all profiles", command=self.view_all_profiles, style="RoundedButton.TButton")
        self.view_profiles_button.place(relx=0.9, rely=0.2, anchor=tk.NE)
        self.edit_cookies_button = ttk.Button(
            self, text="Edit Cookies", command=self.edit_cookies, style="RoundedButton.TButton")
        self.edit_cookies_button.place(relx=0.9, rely=0.3, anchor=tk.NE)

    def start_scraping_thread(self):
        # Create and start a new thread for the scraping tasks
        scraping_thread = threading.Thread(target=self.run_scraping)
        scraping_thread.start()

    def run_scraping(self):
        name, username = me_util.parse_user()
        me_util.print_user(name, username)
        username = name
        tasks = [
            lambda: stats.get_earnings_all(username),
            lambda: stats.get_earnings_tips(username),
            lambda: stats.get_reach_user(username),
            lambda: stats.get_reach_guest(username),
            lambda: stats.get_subs_fans_count_new(username),
            lambda: stats.get_subs_fans_earnings_new(username),
            lambda: stats.get_subs_fans_count_all(username),
            lambda: stats.get_subs_fans_earnings_all(username),
            lambda: stats.get_subs_fans_count_renew(username),
            lambda: stats.get_earnings_chargebacks(username),
        ]

        self.progress_bar["maximum"] = len(tasks)  # Set the maximum value
        self.progress_bar["value"] = 0  # Start with the progress bar empty

        for i, task in enumerate(tasks, start=1):
            task()  # Execute the task
            if not self.isEditingConfiguration:
                self.update_progress_bar(i)

        self.reset_to_main_menu()

    def update_progress_bar(self, value):
        def _update():
            if not self.isEditingConfiguration:  # Check if not in editing mode before updating
                self.progress_bar['value'] = value
                self.progress_bar.update_idletasks()

        self.after(0, _update)

    def enter_editing_configuration(self):
        self.isEditingConfiguration = True
        self.progress_bar.place_forget()  # Hide the progress bar

    def exit_editing_configuration(self):
        self.isEditingConfiguration = False
        self.progress_bar.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

    def reset_to_main_menu(self):
        self.progress_bar['value'] = 0
        self.progress_bar.place_forget()
        self.start_button.config(text="Start Scraping")
        self.start_button.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        self.isEditingConfiguration = False

    def get_all_profiles(self):
        config_home = get_config_home()
        profiles = []
        for item in os.listdir(config_home):
            item_path = config_home / item
            if item_path.is_dir() and (item_path / "auth.json").exists():
                profiles.append(item)
        return profiles

    def view_all_profiles(self):
        profiles = self.get_all_profiles()
        profile_window = tk.Toplevel(self)
        profile_window.title("All Profiles")
        profile_window.geometry("300x200")

        listbox = tk.Listbox(profile_window)
        listbox.pack(expand=True, fill=tk.BOTH)

        for profile in profiles:
            listbox.insert(tk.END, profile)

    def edit_cookies(self):
        profiles = self.get_all_profiles()

        profile_window = tk.Toplevel(self)
        profile_window.title("Select Profile")
        profile_window.geometry("300x200")

        listbox = tk.Listbox(profile_window)
        listbox.pack(expand=True, fill=tk.BOTH)

        for profile in profiles:
            listbox.insert(tk.END, profile)

        def on_profile_select(event):
            selected_profile = listbox.get(listbox.curselection())
            profile_window.destroy()
            self.edit_profile_configuration(selected_profile)

        listbox.bind('<<ListboxSelect>>', on_profile_select)

    def edit_profile_configuration(self, profile):
        self.enter_editing_configuration()
        self.start_button.place_forget()
        self.progress_bar.place_forget()
        self.cookie_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        auth_file = get_auth_file(profile)
        with open(auth_file, 'r') as f:
            auth_data = json.load(f)

        self.cookie_text.delete('1.0', tk.END)
        self.cookie_text.insert(tk.END, json.dumps(auth_data, indent=4))

        def save_profile_configuration():
            cookie_details = self.cookie_text.get("1.0", tk.END).strip()
            try:
                auth_data = json.loads(cookie_details)
                with open(auth_file, 'w') as f:
                    json.dump(auth_data, f, indent=4)
                self.cookie_frame.place_forget()
                self.start_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
                self.exit_editing_configuration()
                tk.messagebox.showinfo("Success", f"Cookies for {
                                       profile} updated successfully!")
            except json.JSONDecodeError:
                tk.messagebox.showerror("Error", "Invalid JSON format")

        self.save_button.config(command=save_profile_configuration)


    def run_statistics_for_all_profiles(self):
        for profile in self.profiles:
            self.update_current_profile(profile)
            username = self.get_username_from_profile(profile)
            if username:
                print(f"Scraping now for {username}")
                self.run_statistics_for_profile(username, profile)
            else:
                log.warning(f"Skipping statistics for profile '{
                            profile}' due to error.")

    def run_statistics_for_profile(self, username, profile):
        try:

            stats.get_earnings_all(username)
            stats.get_earnings_tips(username)
            # ... (other statistics functions) ...
            print(f"Scraping for {profile} completed.")
        except Exception as e:
            log.error(f"Error running statistics for profile '{
                      profile}': {str(e)}")

    def get_username_from_profile(self, profile):
        try:
            # auth_data = helpers.get_auth_dict(profile)
            # return auth_data.get('username', 'default_username')
            import ofscraper.api.me as me

            # currentProfile = get_active_profile()
            currentData = me.scrape_user()
            # print(currentData)
            return currentData['name']
        except json.JSONDecodeError:
            log.error(f"Error reading auth file for profile '{
                      profile}'. The file may be empty or contain invalid JSON.")
            return None
        except Exception as e:
            log.error(f"Error processing profile '{profile}': {str(e)}")
            return None

    def update_current_profile(self, profile_name):
        import ofscraper.utils.config.config as config_
        import ofscraper.utils.constants as constants
        self.current_profile = profile_name
        config_.update_config(constants.getattr("mainProfile"), profile_name)

    def start_scraping(self):
        # Change button text and prepare progress bar
        self.start_button.config(text="Scraping...")
        self.progress_bar.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        # No need to call self.progress_bar.start() since we're manually updating the progress
        # print(get_username_from_profile())
        # Start the scraping in a new thread to keep the UI responsive
        # threading.Thread(target=self.run_scraping).start()
        threading.Thread(target=self.run_statistics_for_all_profiles).start()

    def start_scraping_silent(self):
        threading.Thread(target=self.run_statistics_for_all_profiles).start()


    def scraping_complete(self):
        # Stop the progress bar and reset button text
        self.progress_bar.stop()
        self.progress_bar.place_forget()
        self.start_button.config(text="Start scraping")

    def edit_configuration(self):
        self.enter_editing_configuration()
        self.start_button.place_forget()
        self.progress_bar.place_forget()  # Ensure progress bar is hidden
        # Centered vertically
        self.cookie_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def cancel_configuration(self):
        self.cookie_text.delete('1.0', tk.END)  # Clear the text box
        self.cookie_frame.place_forget()
        self.start_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.exit_editing_configuration()

    def save_configuration(self):
        # Save the cookie details (placeholder)
        cookie_details = self.cookie_text.get("1.0", tk.END).strip()

        try:
            # Convert the provided JSON string to a Python dictionary
            auth_data = json.loads(cookie_details)

            # Extract the cookie string and split into key-value pairs
            cookie_string = auth_data["auth"]["cookie"]
            cookie_pairs = cookie_string.split(';')

            # Initialize variables for storing extracted values
            sess_value = None
            auth_id_value = None
            auth_uid_value = None
            user_agent_value = None
            x_bc_value = None

            # Extract values from cookie pairs
            for pair in cookie_pairs:
                key_value = pair.strip().split('=')
                key = key_value[0].strip()
                if key == 'sess':
                    sess_value = key_value[1].strip()
                elif key == 'auth_id':
                    auth_id_value = key_value[1].strip()
                elif key == 'auth_uid':
                    auth_uid_value = key_value[1].strip()

            # Extract other values from auth_data
            user_agent_value = auth_data["auth"]["user_agent"]
            x_bc_value = auth_data["auth"]["x_bc"]

            # Construct the extracted data dictionary
            extracted_data = {
                "sess": sess_value,
                "auth_id": auth_id_value,
                "auth_uid": auth_uid_value,
                "user_agent": user_agent_value,
                "x-bc": x_bc_value
            }

            # Convert extracted data back to JSON format
            extracted_json = json.dumps(extracted_data, indent=4)

            # Print the extracted JSON to terminal (optional)
            print(f"Extracted JSON:\n{extracted_json}")

            # Get the path to the JSON file from print_auth() function
            json_file_path = print_auth()

            # Write extracted JSON to the existing JSON file
            with open(json_file_path, 'w') as outfile:
                json.dump(extracted_data, outfile, indent=4)

            print(f"Extracted data saved to {json_file_path}")

        except json.JSONDecodeError as e:
            log.error(f"Error decoding auth JSON: {e}")
            return None
        except KeyError as e:
            log.error(f"KeyError: {e}. Check JSON structure.")
            return None

        # Hide cookie frame and show start button (assuming your GUI logic here)
        self.cookie_frame.place_forget()
        self.start_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.exit_editing_configuration()


if __name__ == "__main__":
    app = App()
    app.mainloop()
