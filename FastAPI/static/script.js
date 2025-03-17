let commands = "";
let rover_id = null;
let mapData = {};
let map = [];
let begin = false;
let available = true;
let mine_list = [];
let disarmed_mine_list = [];

const invincibleModeToggle = document.getElementById("invisibleModeToggle");
const invincibleModeLabel = document.getElementById("invisibleModeLabel");

invincibleModeToggle.addEventListener('change', function() {
    if (invincibleModeToggle.checked) {
      invincibleModeLabel.textContent = 'Invincible Mode: On';
    } else {
      invincibleModeLabel.textContent = 'Invincible Mode: Off';
    }
});

document.getElementById("commandForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    rover_id = document.getElementById("roverId").value;
    try {
        // Retrieving Commands
        const commandsResponse = await fetch(`/commands/${rover_id}`);
        if (!commandsResponse.ok) {
            throw new Error(`Failed to fetch commands for Rover ID ${rover_id}`);
        }
        const commandsData = await commandsResponse.json();
        commands = commandsData.commands;
        const commandsDiv = document.getElementById("roverCommands");
        commandsDiv.textContent = `Commands: ${commands}`;

        // Generating and Retrieving Map
        const mapResponse = await fetch("/map");
        if (!mapResponse.ok) {
            throw new Error("Failed to fetch Map Data.");
        }
        mapData = await mapResponse.json();
        map = mapData.map;
        row = mapData.row;
        col = mapData.col;
        const mapContainer = document.getElementById("map");
        mapContainer.innerHTML = ""; 

        const table = document.createElement("table");
        table.style.borderCollapse = "collapse";
        for (let i = 0; i < row; i++) {
            const tableRow = document.createElement("tr");
            for (let j = 0; j < col; j++) {
                const tableCell = document.createElement("td");
                tableCell.style.border = "1px solid black";
                tableCell.style.padding = "10px";
                tableCell.style.textAlign = "center";
                tableCell.style.width = "20px";
                tableCell.style.height = "20px"; 
                tableCell.textContent = map[i][j];
                tableCell.id = `${i}-${j}`;
                if (map[i][j] === 1) {
                    tableCell.style.backgroundColor = "orange";
                } 
                else if (map[i][j] === 0) {
                    tableCell.style.backgroundColor = "white";
                }
                tableRow.appendChild(tableCell);
            }
            table.appendChild(tableRow);
        }
        mapContainer.appendChild(table);

        // Retrieving Mine Locations
        const mineResponse = await fetch("/mines");
        if (!mineResponse.ok) {
            throw new Error("Failed to fetch mine data.");
        }
        mine_list = await mineResponse.json();
        const mineLocationsStr = mine_list.map(mine => {
            return `(${mine.row}, ${mine.col})`;
        }).join(", ");

        const mineLocationsDiv = document.getElementById("mineLocations");
        mineLocationsDiv.textContent = `Mine Locations: ${mineLocationsStr}`;

        // Update Rover Message 
        const roverStatusMessageDiv = document.getElementById("roverStatusMessage");
        roverStatusMessageDiv.innerHTML = "";
        const rover_message_elem = document.createElement("h2");
        rover_message_elem.textContent = "Rover Map";
        roverStatusMessageDiv.appendChild(rover_message_elem);
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
    begin = true;
});

document.getElementById("startButton").addEventListener("click", async function (e) {
    e.preventDefault();
    if (begin == true && available == true) {
        available = false;
        const roverStatusMessageDiv = document.getElementById("roverStatusMessage");
        roverStatusMessageDiv.innerHTML = "";
        const rover_message_elem = document.createElement("h2");
        rover_message_elem.textContent = `Executing Commands for Rover ${rover_id}...`;
        roverStatusMessageDiv.appendChild(rover_message_elem);
        await start_rover_movement();
    }
    else if (available == false) {
        alert("Another Rover is Already Running, Please Wait!");
    }
    else alert("No Commands Available");
});


async function start_rover_movement() {
    let rover_row_pos = 0;
    let rover_col_pos = 0;
    let current_direction = "SOUTH";
    const max_row_size = mapData.row;
    const max_col_size = mapData.col;
    const map = mapData.map;
    let disarm = false;
    let success = true;
    disarmed_mine_list = [];

    const disarmedMinesDiv = document.getElementById("disarmedMines");
    disarmedMinesDiv.innerHTML = "";
    const disarmedMinesHeader = document.createElement("h3");
    disarmedMinesHeader.textContent = "Disarmed Mines:";
    disarmedMinesDiv.appendChild(disarmedMinesHeader);
        
    update_cell(rover_row_pos, rover_col_pos, "*", "yellow");

    for (let i = 0; i < commands.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 100));

        if (commands.at(i) === "L" || commands.at(i) === "R") {
            current_direction = update_direction(current_direction, commands.at(i));
        } 
        
        else if (commands.at(i) === "M") {
            let update = false;
            let prev_row = rover_row_pos;
            let prev_col = rover_col_pos;

            if (current_direction === "SOUTH" && rover_row_pos < max_row_size - 1) {
                rover_row_pos += 1;
                update = true;
            } 
            else if (current_direction === "WEST" && rover_col_pos > 0) {
                rover_col_pos -= 1;
                update = true;
            } 
            else if (current_direction === "NORTH" && rover_row_pos > 0) {
                rover_row_pos -= 1;
                update = true;
            } 
            else if (current_direction === "EAST" && rover_col_pos < max_col_size - 1) {
                rover_col_pos += 1;
                update = true;
            }

            if (update === true) {
                if (!invincibleModeToggle.checked) {
                    if (mine_list.some(mine => mine.row === prev_row && mine.col === prev_col)) {
                        if (!disarm) {
                            const disarmedMinesDiv = document.getElementById("disarmedMines");
                                
                            const disarm_mine_elem = document.createElement("h3");
                            disarm_mine_elem.textContent = `[X] Mine Exploded at (${rover_row_pos}, ${rover_col_pos})`;
                            disarmedMinesDiv.appendChild(disarm_mine_elem);
                            update_cell(prev_row, prev_col, "X", "#ff5845");
                            const roverStatusMessageDiv = document.getElementById("roverStatusMessage");
                            roverStatusMessageDiv.innerHTML = "";
                            const rover_message_elem = document.createElement("h2");
                            rover_message_elem.textContent = `Rover ${rover_id} Hit a Mine at (${rover_row_pos}, ${rover_col_pos})`;
                            roverStatusMessageDiv.appendChild(rover_message_elem);
                            success = false;
                            break; 
                        }
                    } 
                    else {
                        update_cell(rover_row_pos, rover_col_pos, "*", "yellow");
                    }
                }
                else {
                    if (map[rover_row_pos][rover_col_pos] === 1) {
                        for (const mine of mine_list) {
                            if (mine.row === rover_row_pos && mine.col === rover_col_pos) {
                                disarmed_mine_list.push([rover_row_pos, rover_col_pos]);
                                const pin = await disarm_mine(mine.serialNumber);
                                const disarmedMinesDiv = document.getElementById("disarmedMines");
                                
                                const disarm_mine_elem = document.createElement("h3");
                                disarm_mine_elem.textContent = `[+] Mine Disarmed at (${rover_row_pos}, ${rover_col_pos}) with PIN: ${pin}`;
                                disarmedMinesDiv.appendChild(disarm_mine_elem);
                                update_cell(rover_row_pos, rover_col_pos, "*", "#90EE90");
                                map[rover_row_pos][rover_col_pos] = 0;
                                mine_list = mine_list.filter(mine => mine.row !== rover_row_pos || mine.col !== rover_col_pos);
                                break;
                            }
                        }
                    } 
                    else {
                        update_cell(rover_row_pos, rover_col_pos, "*", "yellow");
                    }
                }
            }
        }
        else if (commands.at(i) == "D") {
            disarm = true;
            for (const mine of mine_list) {
                if (mine.row === rover_row_pos && mine.col === rover_col_pos) {
                    disarmed_mine_list.push([rover_row_pos, rover_col_pos]);
                    const pin = await disarm_mine(mine.serialNumber);

                    const disarmedMinesDiv = document.getElementById("disarmedMines");
                    const disarm_mine_elem = document.createElement("h3");
                    disarm_mine_elem.textContent = `[+] Mine Disarmed at (${rover_row_pos}, ${rover_col_pos}) with PIN: ${pin}`;
                    disarmedMinesDiv.appendChild(disarm_mine_elem);

                    update_cell(rover_row_pos, rover_col_pos, "*", "#90EE90");
                    map[rover_row_pos][rover_col_pos] = 0;
                    mine_list = mine_list.filter(mine => mine.row !== rover_row_pos || mine.col !== rover_col_pos);
                    break;
                }
            } 
            disarm = false;
        }
    }

    if (success) {
        alert("Successfully Executed All Commands");
        const roverStatusMessageDiv = document.getElementById("roverStatusMessage");
        roverStatusMessageDiv.innerHTML = "";
        const rover_message_elem = document.createElement("h2");
        rover_message_elem.textContent = `Successfully Executed All Commands`;
        roverStatusMessageDiv.appendChild(rover_message_elem);
        exploration_run = false;
    } else {
        alert("Rover Exploded!");
    }

    available = true;
}

function update_cell(row, col, char, color) {
    const cell_to_update = document.getElementById(`${row}-${col}`);
    cell_to_update.innerText = char;
    cell_to_update.style.backgroundColor = color;
}

function update_direction(curr_direction, move) {
    if (curr_direction === "NORTH") {
      if (move === "L") {
        return "WEST";
      } else {
        return "EAST";
      }
    } else if (curr_direction === "WEST") {
      if (move === "L") {
        return "SOUTH";
      } else {
        return "NORTH";
      }
    } else if (curr_direction === "SOUTH") {
      if (move === "L") {
        return "EAST";
      } else {
        return "WEST";
      }
    } else if (curr_direction === "EAST") {
      if (move === "L") {
        return "NORTH";
      } else {
        return "SOUTH";
      }
    }
  }

const disarm_mine = async (id) => {
    try {
      const response = await fetch(`/mines/${id}`, {
        method: "GET",
      });
  
      return await response.json();
    } catch (error) {
      alert(error);
    }
  };