
from plugins.menu_components.menu_logic import get_options, select_option


def render_menu(event_bus, state_manager):
    while True:
        menu_title = state_manager.get("active_menu")
        options = get_options(state_manager)

        if not menu_title or not options:
            return
        
        counter = 1
        print(f"{menu_title}\n")
        for option in options:
            print(f"\n{counter} .{option['label']}")
            counter = counter + 1

        try:
            chosen_option = int(input("\n\nChoose an option: ")) - 1
            selected_option = options[chosen_option]['id']
            select_option(event_bus, state_manager, selected_option)
        except Exception as e:
            print("Invalid input.")
