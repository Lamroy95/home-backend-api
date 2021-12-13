from app.models import Place, Room, Sensor


all_places = [
    Place(
        name="home",
        rooms=[Room(name="room1", sensors=[
            Sensor(id="temp_dec", name="Temperature", unit="°C"),
            Sensor(id="humidity", name="Humidity", unit="%", min=0, max=100),
            Sensor(id="aqi", name="Air quality", unit="pm2.5", min=0, max=500),
        ])]
    )
]


def get_all_places():
    return all_places


def get_rooms(place_name):
    for place in all_places:
        if place.name == place_name:
            return place.rooms
    else:
        raise ValueError(f"Place \"{place_name}\" not found")


def get_sensors(place_name, room_name):
    rooms = get_rooms(place_name)
    for room in rooms:
        if room.name == room_name:
            return room.sensors
    else:
        raise ValueError(f"Room \"{room_name}\" in place \"{place_name}\" not found")
