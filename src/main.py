import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Smart room controller"
    page.bgcolor = ft.colors.LIGHT_BLUE_ACCENT_100

    welcome_message = ft.Text(
        value="Welcome to Smart IoT House Control System",
        weight=ft.FontWeight.BOLD,
        size=20,
    )

    # Fetch sensor data
    try:
        temperature_data = requests.get('http://127.0.0.1:5000/api/temperature').json()
        light_data = requests.get('http://127.0.0.1:5000/api/light_intensity').json()
        presence_data = requests.get('http://127.0.0.1:5000/api/presence').json()
    except Exception as e:
        temperature_data = {"temperature": 0}
        light_data = {"light_intensity": 100}
        presence_data = {"presence": False}

    temp = temperature_data.get("temperature", 0)
    light = light_data.get("light_intensity", 100)
    presence = presence_data.get("presence", False)

    # Texts for sensor values
    temperature_text = ft.Text(f"Temperature: {temp} °C")
    light_text = ft.Text(f"Light Level: {light} %")
    presence_text = ft.Text(
        f"Presence: {'Detected' if presence else 'Not detected'}",
        color=ft.colors.GREEN if presence else ft.colors.RED
    )

    # --- LED Controls ---
    light_status = ft.Text()
    light_toggle_button = ft.Switch(label="LED", tooltip="Click to change LED state")

    # Auto LED control based on light
    if isinstance(light, (int, float)) and light < 5:
        light_status.value = "LED is ON"
        light_status.color = ft.colors.GREEN
        light_toggle_button.value = True
    else:
        light_status.value = "LED is OFF"
        light_status.color = ft.colors.RED
        light_toggle_button.value = False

    def toggle_led(e):
        state = light_toggle_button.value
        try:
            res = requests.post("http://127.0.0.1:5000/api/led", json={"state": state})
            if res.status_code == 200:
                light_status.value = "LED is ON" if state else "LED is OFF"
                light_status.color = ft.colors.GREEN if state else ft.colors.RED
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to update LED state."), bgcolor=ft.colors.RED)
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
        page.update()

    light_toggle_button.on_change = toggle_led
    light_controls = ft.Column([
        ft.Text("Light Information:", size=16, weight=ft.FontWeight.W_600),
        ft.Row([light_toggle_button]),
        light_text,
        light_status
    ])

    # --- Fan Controls ---
    fan_status = ft.Text()
    temp_toggle = ft.Switch(label="Fan", tooltip="Click to change fan state")

    if isinstance(temp, (int, float)) and temp >= 25:
        fan_status.value = "Fan is ON"
        fan_status.color = ft.colors.GREEN
        temp_toggle.value = True
    else:
        fan_status.value = "Fan is OFF"
        fan_status.color = ft.colors.RED
        temp_toggle.value = False

    def toggle_fan(e):
        state = temp_toggle.value
        try:
            res = requests.post("http://127.0.0.1:5000/api/fan", json={"state": state})
            if res.status_code == 200:
                fan_status.value = "Fan is ON" if state else "Fan is OFF"
                fan_status.color = ft.colors.GREEN if state else ft.colors.RED
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to update Fan state."), bgcolor=ft.colors.RED)
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
        page.update()

    temp_toggle.on_change = toggle_fan
    temp_controls = ft.Column([
        ft.Text("Temperature Information:", size=16, weight=ft.FontWeight.W_600),
        ft.Row([temp_toggle]),
        temperature_text,
        fan_status
    ])

    # --- Presence Info ---
    presence_controls = ft.Column([
        ft.Text("Presence Information:", size=16, weight=ft.FontWeight.W_600),
        presence_text
    ])

    # --- Refresh Button ---
    def refresh_data(e):
        page.controls.clear()
        main(page)

    refresh_button = ft.ElevatedButton("Refresh Data", on_click=refresh_data)

    # --- Add everything to the page ---
    page.add(
        welcome_message,
        refresh_button,
        light_controls,
        temp_controls,
        presence_controls
    )

ft.app(target=main)
