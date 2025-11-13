from nicegui import ui, app
import asyncio
import os

# Global vars
FIRST_RUN_FILE = "setup_done.txt"

# Setup
app.add_static_files('/assets', 'assets')

# General helpers
def is_first_run():
    return not os.path.exists(FIRST_RUN_FILE)

# -----------------------------
# HOME PAGE (after setup)
# -----------------------------
@ui.page('/home')
def home_page():

    with ui.header().classes('justify-between items-center p-2'):

        # High z-index wrapper so menu is above dialog overlays
        with ui.element('div').classes('relative z-50'):

            # Hamburger button
            menu_button = ui.button('☰').classes('text-2xl')

            # The menu MUST come immediately after the button so it attaches to it
            with ui.menu().classes('z-[3000]'):   # ensure above dialogs
                ui.menu_item('Option 1')
                ui.menu_item('Option 2')
                ui.menu_item('Option 3')

        # Profile + dialog (unchanged)
        login_dialog = ui.dialog()
        with login_dialog:
            with ui.card().classes('p-4'):
                ui.label("Profile Login").classes('text-lg font-semibold mb-2')
                login_user = ui.input('Username')
                login_pass = ui.input('Password', password=True)
                ui.button('Login', on_click=login_dialog.close)

        ui.button('Profile', on_click=login_dialog.open)

    # Centered Skeleton Placeholder
    with ui.element('div').classes('w-full h-full flex justify-center items-center p-10'):
        ui.skeleton().classes('w-[80vw] h-[80vh] rounded-xl')


# -----------------------------
# SETUP PAGE (your original)
# -----------------------------
@ui.page('/')
def setup_page():
    # If setup is already complete → skip intro and go to home
    if not is_first_run():
        ui.navigate.to('/home')
        return

    # CSS for intro animations
    ui.add_head_html('<link rel="stylesheet" href="/assets/intro.css">')

    # FULLSCREEN INTRO
    intro_root = ui.element('div').classes('intro-root')

    with intro_root:
        ui.label("Hey there, it seems this is your first time!").classes('intro-text text1')
        ui.label("Let's get you set up.").classes('intro-text text2')

    # Activate CSS animations after DOM is ready
    ui.timer(0.1, lambda: intro_root.classes(add='ready'), once=True)

    # HIDDEN SETUP CARD
    with ui.element('div').classes('fixed inset-0 flex justify-center items-center') as card_wrapper:
        card_wrapper.set_visibility(False)

        with ui.card().classes('p-8 w-[400px]'):
            ui.label("Initial Setup").classes('text-xl font-bold mb-4 text-center')

            with ui.stepper().classes('w-full') as stepper:

                # STEP 1
                with ui.step('Inference Server'):
                    inf_ip = ui.input('Inference Server IP')
                    inf_port = ui.input('Inference Server Port')
                    ui.button('Next', on_click=stepper.next)

                # STEP 2
                with ui.step('Database Server'):
                    db_ip = ui.input('Database Server IP')
                    db_port = ui.input('Database Server Port')
                    ui.button('Next', on_click=stepper.next)

                # STEP 3
                with ui.step('Secret'):
                    secret = ui.input('Secret', password=True)

                    # Loading dialog (initially hidden)
                    loading_dialog = ui.dialog()
                    with loading_dialog:
                        with ui.card().classes('p-6 items-center flex flex-col'):
                            ui.spinner(size='lg')
                            ui.label("Connecting to servers...").classes('mt-3 text-lg')

                    # Redirect to /home AFTER delay
                    def finish():
                        # Show loading animation
                        loading_dialog.open()

                        # Simulate "connecting" for 2.5 seconds
                        def complete():
                            # Save the file marking setup complete
                            with open(FIRST_RUN_FILE, "w") as f:
                                f.write("setup=true")

                            ui.notify(
                                f"Saved:\n"
                                f"Inf={inf_ip.value}:{inf_port.value}\n"
                                f"DB={db_ip.value}:{db_port.value}"
                            )

                            ui.navigate.to('/home')

                        ui.timer(2.5, complete, once=True)

                    ui.button('Finish', on_click=finish)


    # AFTER 6 SECONDS → REMOVE INTRO & SHOW CARD
    def fade_and_remove():
        intro_root.classes(add='intro-fade')
        ui.timer(1, lambda: intro_root.delete(), once=True)
        card_wrapper.set_visibility(True)

    ui.timer(6, fade_and_remove, once=True)


ui.run(title="Setup Demo", reload=False, port=1600)

