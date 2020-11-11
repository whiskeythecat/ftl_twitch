import sys
import json
import os
import os.path
import filecmp
from time import sleep
import time

def read_int(fin):
    return int.from_bytes(fin.read(4), byteorder="little")

def read_string(fin):
    length = int.from_bytes(fin.read(4), byteorder="little")
    string = fin.read(length)
    return string.decode("utf-8")

def read_bool(fin):
    boolean = int.from_bytes(fin.read(4), byteorder="little")
    return boolean != 0

def read_animation(fin):
    read_bool(fin)
    read_bool(fin)
    read_int(fin)
    read_int(fin)
    read_int(fin)
    read_int(fin)
    read_int(fin)

def read_crew(fin):
    crew = {}
    crew["name"] = read_string(fin)
    crew["race"] = read_string(fin)
    crew["boarding_drone"] = read_bool(fin)
    crew["health"] = read_int(fin)
    #Sprite locations
    read_int(fin)
    read_int(fin)
    crew["room_id"] = read_int(fin)
    crew["room_square"] = read_int(fin)
    crew["player"] = read_bool(fin)

    crew["clone_ready"] = read_int(fin)
    crew["death_order"] = read_int(fin)

    tint_count = read_int(fin)
    for i in range(tint_count):
        read_int(fin)

    crew["mind_controlled"] = read_bool(fin)
    crew["saved_room_square"] = read_int(fin)
    crew["saved_room_id"] = read_int(fin)

    crew["skill_pilot"] = read_int(fin)
    crew["skill_engine"] = read_int(fin)
    crew["skill_shield"] = read_int(fin)
    crew["skill_weapon"] = read_int(fin)
    crew["skill_repair"] = read_int(fin)
    crew["skill_combat"] = read_int(fin)

    crew["male"] = read_bool(fin)

    crew["repairs"] = read_int(fin)
    crew["combat_kills"] = read_int(fin)
    crew["pilot_evasions"] = read_int(fin)
    crew["jumps_survived"] = read_int(fin)
    crew["masteries_earned"] = read_int(fin)

    crew["stun_ticks"] = read_int(fin)
    crew["health_boost"] = read_int(fin)
    crew["clonebay_priority"] = read_int(fin)
    crew["damage_boost"] = read_int(fin)
    crew["unknown_lambda"] = read_int(fin)
    crew["universal_death_count"] = read_int(fin)

    #masteries skip
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    read_bool(fin)
    
    #unknown 
    read_int(fin)

    read_animation(fin)

    #unknown 
    read_int(fin)

    if crew["race"] == "crystal":
        crew["lockdown_recharge_ticks"] = read_int(fin) 
        crew["lockdown_recharge_ticks_goal"] = read_int(fin) 
        #unkown 
        read_int(fin)

    return crew

def read_ship(fin):
    ship = {}
    ship["blueprint_name"] = read_string(fin)
    ship["ship_name"] = read_string(fin)
    ship["gfx_name"] = read_string(fin)

    ship["starting_crew"] = []
    starting_crew = read_int(fin)
    for i in range(starting_crew):
        crew = {}
        crew["race"] = read_string(fin)
        crew["name"] = read_string(fin)
        ship["starting_crew"].append(crew)

    ship["hostile" ] = read_bool(fin)
    ship["jump_charge_ticks"] = read_int(fin)
    ship["jumping"] = read_bool(fin)
    ship["jump_animation_ticks"] = read_int(fin)

    ship["hull"] = read_int(fin)
    ship["fuel"] = read_int(fin)
    ship["drone_parts"] = read_int(fin)
    ship["missiles"] = read_int(fin)
    ship["scrap"] = read_int(fin)

    crew = read_int(fin)
    ship["crew"] = []
    for i in range(crew):
        ship["crew"].append(read_crew(fin))

    return ship

def parse_ftl(filename):

    fin = open(filename, "rb")

    save = {}

    save["file_format"] = read_int(fin)
    if save["file_format"] == 11:
        save["random_native"] = read_bool(fin)
    else:
        save["random_native"] = True

    if save["file_format"] == 2:
        save["advanced"] = False
    else:
        save["advanced"] = read_bool(fin)

    difficulty = read_int(fin)
    if difficulty == 0:
        save["difficulty"] = "easy"
    elif difficulty == 1:
        save["difficulty"] = "normal"
    else:
        save["difficulty"] = "hard"

    save["total_ships_defeated"] = read_int(fin)
    save["total_beacons_explored"] = read_int(fin)
    save["total_scrap_collected"] = read_int(fin)
    save["total_crew_hired"] = read_int(fin)

    save["ship_name"] = read_string(fin)
    save["blueprint_name"] = read_string(fin)

    #one based sector number
    save["sector"] = read_int(fin)

    #unknown value
    fin.read(4)

    statevars = read_int(fin)

    save["state_vars"] = {}
    for i in range(statevars):
        var_name = read_string(fin)
        var_value = read_int(fin)
        save["state_vars"][var_name] = var_value

    save["player_ship"] = read_ship(fin)
        
    return save

if __name__ == "__main__":
    beacons = 0
    hull = 0
    hull_total = 0
    fuel = 0
    fuel_total = 0
    sector = 0
    session = []
    cur_game = None

    while True:
        if os.path.exists("C:/Users/me/Documents/My Games/FasterThanLight/continue.sav"):
            os.system("copy \"C:\\Users\\me\\Documents\\My Games\\FasterThanLight\\continue.sav\" save.dat")
            
        if os.path.exists("save.dat") and (os.path.exists("prev.dat") == False or filecmp.cmp("save.dat", "prev.dat") == False):
            os.system("copy save.dat prev.dat")
            os.system("echo \"var data = \" > data.json")
            save = parse_ftl("save.dat")
            fout = open("data.json", "w")
            fout.write("var data = ")
            fout.write(json.dumps(save))
            print("Updated data.json")
            data = save

            if cur_game == None or data["total_beacons_explored"]  < beacons:
                cur_game = {}
                cur_game["ship"] = data["player_ship"]["ship_name"]
                cur_game["jumps"] = []
                hull = data["player_ship"]["hull"]
                fuel = data["player_ship"]["fuel"]
                hull_total = 0
                fuel_total = 0
                session.append(cur_game)
                beacons = -1
                sector = -1

                print("New game")


            if data["total_beacons_explored"] > beacons:
                print("New jump")
                beacons = data["total_beacons_explored"]
                jump = {}
                jump["total_beacons_explored"] = data["total_beacons_explored"];
                jump["sector"] = data["sector"];
                jump["total_ships_defeated"] = data["total_ships_defeated"];
                jump["total_scrap_collected"] = data["total_scrap_collected"];

                new_hull = data["player_ship"]["hull"]
                new_fuel = data["player_ship"]["fuel"]
                if new_hull < hull:
                    hull_total += (hull - new_hull)
                if new_fuel < fuel:
                    fuel_total += (fuel - new_fuel)
                fuel = new_fuel
                hull = new_hull
                jump["hull"] = hull_total
                jump["fuel"] = fuel_total

                if "state_vars" in data and "store_repair" in data["state_vars"]:
                    jump["repair"] = data["state_vars"]["store_repair"];
                else:
                    jump["repair"] = 0;
                jump["time"] = time.time()
                cur_game["jumps"].append(jump)

                with open("session.json", "w") as json_file:
                    json_file.write("var session = ")
                    json_file.write(json.dumps(session))
        sleep(1.0)
