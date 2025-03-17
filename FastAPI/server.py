from fastapi import FastAPI, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import utils
import random

app = FastAPI()

NOT_STARTED = 'NOT_STARTED'
FINISHED = 'FINISHED'
MOVING = 'MOVING'
ELIMINATED = 'ELIMINATED'

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

origins = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MapDimensions(BaseModel):
    row: int
    col: int

class Mine(BaseModel):
    row: int
    col: int
    serialNumber: int

map = []
mines = []
rovers = []
commands = [utils.get_rover_commands(id) for id in range(1, 11)]
id_list = random.sample(range(11, 100), 50)
valid_commands = ['L', 'R', 'M', 'D']

# --- Endpoints for Map --- #

@app.get("/map", status_code=status.HTTP_200_OK)
def get_map():
    global map, mines
    map, mines = utils.generate_new_map(10, 10)
    return {
        "row": len(map),
        "col": len(map[0]),
        "map": map
    }

@app.put("/map")
def update_map(item: MapDimensions, status_code=status.HTTP_201_CREATED):
    global map, mines
    map, mines = utils.generate_new_map(item.row, item.col)
    return {
        "row": len(map),
        "col": len(map[0]),
        "map": map,
        "statusCode" : status_code
    }

# --- Endpoints for Mines --- #

@app.get("/mines")
def get_mines():
    mines_dict = []
    for mine_info in mines:
        mine_dict = {
            "row": mine_info[0],
            "col": mine_info[1],
            "serialNumber": mine_info[2]
        }
        mines_dict.append(mine_dict)
    return mines_dict

@app.get("/mines/{id}")
def get_mine_id(id: int):
    for mine_info in mines:
        if mine_info[2] == id:
            return utils.disarm_mine(str(id))
    raise HTTPException(status_code=404, detail=f"Mine with Serial Number '{id}' Not Found")

@app.delete("/mines/{id}")
def delete_mine(id: int):
    global mines
    for mine_info in enumerate(mines):
        if mine_info[2] == id:
            row = mine_info[0]
            col = mine_info[1]
            map[row][col] = 0
            mines.remove(mine_info)
            return {
                "message": f"Mine with Serial Number '{id}' Successfully Deleted"
            }
    raise HTTPException(status_code=404, detail=f"Mine with Serial Number '{id}' Not Found")

@app.post("/mines")
def create_mine(new_mine: Mine):
    if map[new_mine.row][new_mine.col] == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Mine Already Exists at ({new_mine.row}, {new_mine.col})")
    map[new_mine.row][new_mine.col] = 1
    mines.append([new_mine.row, new_mine.col, new_mine.serialNumber])
    return {
        "row": f"{new_mine.row}",
        "col": f"{new_mine.col}",
        "serialNumber": f"{new_mine.serialNumber}"
    }

@app.put("/mines/{id}")
def update_mine(id: int, mine: Mine):
    global mines
    for i, mine_info in enumerate(mines):
        if mine_info[2] == id:
            if mine.row is not None and mine.col is None:
                raise HTTPException(status_code=400, detail="Both Row and Col Must be Provided Together")
            if mine.col is not None and mine.row is None:
                raise HTTPException(status_code=400, detail="Both Row and Col Must be Provided Together")
            
            mines[i][0] = mine.row
            mines[i][1] = mine.col
            
            if mine.serialNumber is not None:
                mines[i][2] = mine.serialNumber

            return {
                "row": mines[i][0], 
                "col": mines[i][1], 
                "serialNum": mines[i][2]
            }
    raise HTTPException(status_code=404, detail=f"Mine with Serial Number '{id}' Not Found")

# --- Endpoints for Rover --- #

@app.get("/rovers")
def get_rovers():
    return rovers

@app.get("/rovers/{id}")
def get_rover_id(id: int):
    for rover in rovers:
        if rover['id'] == id:
            return {
                "id": rover['id'],
                "commands": rover['commands'],
                "status": rover['status'],
                "position": rover['position']
            }

@app.post("/rovers")
def create_rover(incoming_command: str):
    incoming_command = incoming_command.upper()
    for command in incoming_command:
        if command not in valid_commands:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Command, Must be 'L', 'R', 'M', 'D'")
    rovers.append({"id": id_list.pop(), "commands": incoming_command, "status": NOT_STARTED, "position": (0, 0)})
    return rovers[len(rovers) - 1]['id']

@app.delete("/rovers/{id}")
def delete_rover(id: int):
    for i, rover in enumerate(rovers):
        if rover['id'] == id:
            rovers.pop(i)
            return {
                "message": f"Rover with ID '{id}' Successfully Deleted"
            }

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rover with ID '{id}' Not Found")

@app.put("/rovers/{id}")
def update_rover(id: int, commands: str):
    global rovers
    for rover in rovers:
        if rover['id'] == id:
            if rover['status'] not in ['NOT_STARTED', 'FINISHED']:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rover must be 'NOT_STARTED' or 'FINISHED' to Update Commands")
            
            for command in commands:
                if command not in valid_commands:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Command, Must be 'L', 'R', 'M', 'D'")
            
            rover['commands'] = commands
            return {
                "id": id, 
                "commands": rover['commands']
            }
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rover Not Found")

@app.post("/rovers/{id}/dispatch")
def dispatch_rover(id: int):
    global rovers
    for rover in rovers:
        if rover['id'] == id:
            if rover['status'] != 'NOT_STARTED':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rover must be 'NOT_STARTED' to dispatch")
            
            rover['status'] = 'MOVING'
            
            position = rover['position']
            for command in rover['commands']:
                if command == 'L':
                    position = (position[0] - 1, position[1])
                elif command == 'R':
                    position = (position[0] + 1, position[1])
                elif command == 'M':
                    position = (position[0], position[1] + 1)
                elif command == 'D':
                    position = (position[0], position[1] - 1)
            
            rover['position'] = position
            rover['status'] = "FINISHED"
            
            return {
                "id": id, 
                "status": rover['status'], 
                "position": rover['position'], 
                "commands": rover['commands']
            }
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rover Not Found")

@app.get("/commands/{id}")
def get_commands(id: int):
    return utils.get_rover_commands(id)