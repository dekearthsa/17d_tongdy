
demo_data_exhaust = {
    "sensor_id": "after_exhaust", ## "after_exhaust", "before_exhaust", "interlock_4c" 
    "sensor_type": "tongdy", ## "tongdy", "interlock"
    "payload": {
        "temperature": 11.0, ## float
        "humid": 45, ## int
        "co2": 333, ## int
        
    }
}


demo_data_interlock = {
    "sensor_id": "interlock_4c", ## "after_exhaust", "before_exhaust", "interlock_4c" 
    "sensor_type": "interlock", ## "tongdy", "interlock"
    "payload": {
            "temperature": 11.0, ## float
            "humid": 45, ## int
            "co2": 333, ## int
            "operation_mode": 1, ## int
            "temp_before_filter": 10.0, ## float 
            "fan_speed": 10, ## int
            "voc": 333 ## int
        },
    }


## db hlr_db.db 
## table -> sensor_data_exhaust (id int,  timestamp (ms) int, sensor_type string, temp float, humid int, co2 int )
## table -> sensor_data_interlock(id int,  timestamp (ms) int, sensor_type string, temp float, humid int, co2 int, operation_mode int, fan_speed int, voc int )